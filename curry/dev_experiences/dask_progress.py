import os
import random
from time import sleep


from dask.distributed import get_client, secede, rejoin
from multiprocessing import Process, freeze_support, set_start_method
import dask
from dask import bag as db
from dask.distributed import Client, LocalCluster


if __name__ == '__main__':
    freeze_support()
    set_start_method('spawn')


    dask.config.set({"distributed.scheduler.allowed-failures": 100})
    cluster = LocalCluster(threads_per_worker=1, n_workers=4, memory_limit=400e6)
    client = Client(cluster)
    
    print(client)
    print(cluster)


    def multiply_by_two(x: int) -> int:
        sleep(0.02)
        return 2 * x


    N = 4000

    x = db.from_sequence(range(N), npartitions=N // 2)

    mults = x.map(multiply_by_two)

    summed = mults.sum()

    all_current_workers = [w.pid for w in cluster.scheduler.workers.values()]
    non_preemptible_workers = all_current_workers[:2]


    def kill_a_worker():
        preemptible_workers = [w.pid for w in cluster.scheduler.workers.values() if w.pid not in non_preemptible_workers]
        if preemptible_workers:
            os.kill(random.choice(preemptible_workers), 15)


    summed = client.compute(summed)

    while not summed.done():
        kill_a_worker()
        sleep(3.0)

    print(f"`sum(range({N}))` on cluster: {summed.result()}\t(should be {N * (N - 1)})")
