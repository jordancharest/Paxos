# for global configs
from threading import RLock


# all threads need access to these resources
running = True
worker = None
calendar = None
mutex = RLock()
timeout = 0.500 # 500 milliseconds