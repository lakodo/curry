from __future__ import annotations

import logging
from time import sleep

import dask
from dask import bag as db
from dask.distributed import Client

logger = logging.getLogger("curry.scheduler.dask.local_test")


if __name__ == "__main__":
    dask.config.set({"distributed.scheduler.allowed-failures": 100})

    client = Client(address="tcp://127.0.0.1:18000")

    def multiply_by_two(x: int) -> int:
        sleep(0.02)
        print(f"multiply_by_two({x})")
        return 2 * x

    N = 400

    x = db.from_sequence(range(N), npartitions=N // 2)

    mults = x.map(multiply_by_two)

    summed = mults.sum()

    summed = client.compute(summed)

    while not summed.done():
        print("loop")
        sleep(3.0)

    print(f"`sum(range({N}))` on cluster: {summed.result()}\t(should be {N * (N - 1)})")

    client.close()
