from bittensor_query import query_scheduler
import sched, time
from dotenv import dotenv_values
if __name__ == "__main__":

    config = dotenv_values(".env")

    # This runs immediately and then afterwards every PING_INTERVAL seconds
    s = sched.scheduler(time.time, time.sleep)
    s.enter(1, 1, query_scheduler, (s, config))
    s.run()
