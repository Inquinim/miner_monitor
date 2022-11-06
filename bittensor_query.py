from datetime import datetime
import time
import bittensor
from bittensor._cli import cli as cli
from bittensor._cli.cli_impl import CLI as CLI
from bittensor._cli.cli_impl import CacheException
import requests
from netaddr import IPAddress
import pytz

# Adapted from:
# https://github.com/opentensor/bittensor/blob/master/bittensor/_cli/cli_impl.py

def query_scheduler(sc, var_dict):
    """
    """
    
    dt = datetime.strftime(datetime.now(tz=pytz.timezone(var_dict['PY_TIMEZONE'])), "%d/%m/%Y at %I:%M %p")
    print(f"Pinging {var_dict['WALLET_NAME']} on {dt}")

    # Query the metagraph for the miners found on the local system under the provided wallet name
    query_miners(var_dict)

    print(f"Finished {var_dict['WALLET_NAME']} on {dt}")

    requests.post(
        var_dict['WEBHOOK_GLOBAL'], {"content": f"{var_dict['USER']}: Pinged metagraph on {dt}"}
    )

    sc.enter(var_dict["PING_INTERVAL"], 1, query_scheduler, (sc, var_dict))


def send_dc_notification(message: str, webhook: str):
    json_dict = {"content": f"{message}"}
    r = requests.post(webhook, json_dict)
    if r.status_code != 204:
        # print(f"{r.headers}")
        if r.status_code == 429:
            print("Rate limit hit.")
            sleep_qty = r.headers["x-ratelimit-reset-after"]
            print(f"Sleeping for {sleep_qty} seconds.")
            time.sleep(sleep_qty)
        else:
            print(f"{r.status_code=}")

def query_miners(var_dict):
    """"""
    _, wallet_name, subtensor_network, subtensor_chain_endpoint, trust_threshold, py_timezone, debug, webhook, _ = var_dict.values()

    timezone = pytz.timezone(py_timezone)
    args = ["overview", "--wallet.name", wallet_name, "--subtensor.network", subtensor_network]
    if subtensor_chain_endpoint is not None:
        args.extend(["--subtensor.chain_endpoint", subtensor_chain_endpoint])

    # Send message if unable to connect to the subtensor endpoint
    config: bittensor.Config = cli.config(args)
    coldkey_wallet = bittensor.wallet( config=config)
    subtensor = bittensor.subtensor(config=config)

    if not coldkey_wallet.coldkeypub_file.exists_on_device():
        assert False, f"Public coldkey is missing for {wallet_name}."

    all_hotkeys = CLI._get_hotkey_wallets_for_wallet( coldkey_wallet )


    # Check we have keys to display.
    if len(all_hotkeys) == 0:
        assert False, "No hotkeys found for specified cold wallet."

    # This includes unregistered hotkeys
    print(f"Number of hotkeys found: {len(all_hotkeys)}")

    neurons = []

    # Sync from metagraph cache
    try:
        if config.subtensor.get(
            "network", bittensor.defaults.subtensor.network
        ) not in ("local", "nakamoto"):
            raise CacheException(
                "This network is not cached, defaulting to regular overview."
            )

        if config.get("no_cache"):
            raise CacheException(
                "Flag was set to not use cache, defaulting to regular overview."
            )

        metagraph: bittensor.Metagraph = bittensor.metagraph(subtensor=subtensor)
        try:
            # Grab cached neurons from IPFS
            all_neurons = metagraph.retrieve_cached_neurons()
        except Exception:
            raise CacheException(
                "Failed to retrieve cached neurons, defaulting to regular overview."
            )

        # Map the hotkeys to uids
        hotkey_to_neurons = {n.hotkey: n.uid for n in all_neurons}
        for wallet in all_hotkeys: # tqdm
            uid = hotkey_to_neurons.get(wallet.hotkey.ss58_address)
            if uid is not None:
                nn = all_neurons[uid]
                neurons.append((nn, wallet))
    except CacheException:
        for wallet in all_hotkeys:
            # Get overview without cache
            nn = subtensor.neuron_for_pubkey(wallet.hotkey.ss58_address)
            if not nn.is_null:
                neurons.append((nn, wallet))
                
    if debug:
        print(f"Num neurons: {len(neurons)}")

    # Add neurons (miners) with trust lower than the threshold, exclude validators
    neurons_below = [nn[0] for nn in neurons if nn[0].trust < trust_threshold and len(nn[0].bonds) == 0]
            
    # Sort by trust from low to high
    neurons_below.sort(key=lambda x: x.trust, reverse=True)

    # Send off an overview notification if there are any miners below the threshold
    if len(neurons_below) > 0:
        dt = datetime.strftime(datetime.now(tz=timezone), "%d/%m/%Y at %I:%M %p")
        send_dc_notification(f"Miner(s) below trust threshold: {len(neurons_below)} / {len(neurons)} on {dt}", webhook)
    
    # Send off the notifications
    for neuron in neurons_below:
        message = f"UID {neuron.uid} ({IPAddress(neuron.ip)}:{neuron.port}) below trust threshold: {neuron.trust:.3f} | emissions: {int(neuron.emission * 1000000000):,}"
        send_dc_notification(message, webhook)
        # Can't send too many notifications at once due to rate limit
        time.sleep(1)