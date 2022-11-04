from bittensor_query import query_scheduler
import sched, time

from utils import WEBHOOK_USER

if __name__ == "__main__":
    var_dict = {
        "wallet_name": "wallet",
        "subtensor_network": "local",
        "subtensor_chain_endpoint": None, # Set this "your_subtensor_ip:9944" if using an external subtensor
        "trust_threshold": 0.6,
        "pytz": "Etc/GMT+0",
        "debug": True,
        "webhook": WEBHOOK_USER,
    }

    # This runs immediately and then afterwards every PING_INTERVAL seconds
    s = sched.scheduler(time.time, time.sleep)
    s.enter(1, 1, query_scheduler, (s, var_dict))
    s.run()
