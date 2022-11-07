from bittensor_query import query_scheduler
import sched, time

if __name__ == "__main__":
    ### START: You should change the variables below as needed.

    # The name to show in the pings to the Global Webhook
    USER = "name"

    # Notifications about miners below the trust threshold go to this webhook if at least one miner is below threshold
    WEBHOOK_USER = ""  # Must fill this out

    # Notifications that a check has been performed go to this webhook
    WEBHOOK_GLOBAL = ""  # Must fill this out

    # Run every 300 seconds (5 mins)
    PING_INTERVAL = 300

    # Cold wallet name (on the server)
    WALLET_NAME = "wallet"

    # Local or Nakamoto (lowercase)
    SUBTENSOR_NETWORK = "local"

    # Leave as "none" unless you want to point to an external subtensor, otherwise ip:9944
    SUBTENSOR_CHAIN_ENDPOINT = "none"

    # Only send notifications if miners drop below this level of trust
    TRUST_THRESHOLD = 0.6

    # Your PYTZ timezone
    # Note: for some reason, GMT+1 ends up being interpreted as GMT-1 and visa versa

    # How to find timezones (recommended but optional to use your specific timezone)
    # https://stackoverflow.com/questions/13866926/is-there-a-list-of-pytz-timezones
    PY_TIMEZONE = "Etc/GMT+0"

    # Show debug messages in the server running the script
    DEBUG = "True"
    ### END: You should change the variables above as needed.

    config = {
        "USER": USER,
        "WALLET_NAME": WALLET_NAME,
        "SUBTENSOR_NETWORK": SUBTENSOR_NETWORK,
        "SUBTENSOR_CHAIN_ENDPOINT": SUBTENSOR_CHAIN_ENDPOINT,
        "TRUST_THRESHOLD": TRUST_THRESHOLD,
        "PY_TIMEZONE": PY_TIMEZONE,
        "DEBUG": DEBUG,
        "WEBHOOK_USER": WEBHOOK_USER,
        "WEBHOOK_GLOBAL": WEBHOOK_GLOBAL,
        "PING_INTERVAL": PING_INTERVAL,
    }

    # This runs immediately and then afterwards every PING_INTERVAL seconds
    s = sched.scheduler(time.time, time.sleep)
    s.enter(1, 1, query_scheduler, (s, config))
    s.run()
