# for global configs
from threading import RLock


# all threads need access to these resources
running = True
worker = None
calendar = None
mutex = RLock()
server_sleep = 0.1
paxos_timeout = 5 * server_sleep