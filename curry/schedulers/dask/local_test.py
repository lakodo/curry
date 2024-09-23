from __future__ import annotations

import logging
import time

from dask import bag as db
from dask.distributed import Client

logger = logging.getLogger("curry.scheduler.dask.local_test")

if __name__ == "__main__":

    client = Client(address="tcp://127.0.0.1:18000")

    def multiply_by_two(x: int) -> int:
        time.sleep(1)
        print(f"multiply_by_two({x})")
        return 2 * x

    N = 4000

    x = db.from_sequence(range(N))

    mults = x.map(multiply_by_two)

    summed = mults.sum()


    t0=time.time()
    summed = client.compute(summed)

    time.sleep(1.0)

    while not summed.done():
        print("loop")
        time.sleep(1.0)
    t1=time.time()

    print(f"[{t1-t0}s] `sum(range({N}))` on cluster: {summed.result()}\t(should be {N * (N - 1)})")

    client.close()
