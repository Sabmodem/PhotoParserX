import multiprocessing
from redis import Redis
from rq import Worker
import asyncio
from config import common as conf

def run_worker():
    Worker(['default'], connection=Redis(host=conf.redis_host, port=conf.redis_port)).work()

def run_wsserver():
    from wsserver import main
    asyncio.run(main())

def run_app():
    from app import main 
    asyncio.run(main())

def main():
    procs = []
    procs.append(multiprocessing.Process(target=run_worker))
    procs.append(multiprocessing.Process(target=run_wsserver))
    procs.append(multiprocessing.Process(target=run_app))

    for i in procs:
        i.start()

    for i in procs:
        i.join()

if __name__ == '__main__':
    main()
