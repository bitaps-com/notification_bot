from utils import server

workers = 1
bind = "%s:%s" %(server['host'],server['port'])
timeout = 30
worker_class = "aiohttp.GunicornUVLoopWebWorker"