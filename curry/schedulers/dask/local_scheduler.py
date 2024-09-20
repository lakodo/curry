from __future__ import annotations

import asyncio
import gc
import logging
import sys

from distributed import Scheduler
from distributed._signals import wait_for_signals
from distributed.compatibility import asyncio_run
from distributed.config import get_loop_factory
from distributed.proctitle import (
    enable_proctitle_on_children,
    enable_proctitle_on_current,
)

logger = logging.getLogger("distributed.scheduler")


def main() -> None:
    """Launch a Dask scheduler."""

    g0, g1, g2 = gc.get_threshold()  # https://github.com/dask/distributed/issues/1653
    gc.set_threshold(g0 * 3, g1 * 3, g2 * 3)

    enable_proctitle_on_current()
    enable_proctitle_on_children()

    if sys.platform.startswith("linux"):
        import resource  # module fails importing on Windows

        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        limit = max(soft, hard // 2)
        resource.setrlimit(resource.RLIMIT_NOFILE, (limit, hard))

    async def run() -> None:
        logger.info("-" * 47)

        scheduler = Scheduler(port=18000, dashboard_address=":18001")
        logger.info("-" * 47)

        async def wait_for_scheduler_to_finish() -> None:
            """Wait for the scheduler to initialize and finish"""
            await scheduler
            await scheduler.finished()

        async def wait_for_signals_and_close() -> None:
            """Wait for SIGINT or SIGTERM and close the scheduler upon receiving one of those signals"""
            signum = await wait_for_signals()
            await scheduler.close(reason=f"signal-{signum}")

        wait_for_signals_and_close_task = asyncio.create_task(wait_for_signals_and_close())
        wait_for_scheduler_to_finish_task = asyncio.create_task(wait_for_scheduler_to_finish())

        done, _ = await asyncio.wait(
            [wait_for_signals_and_close_task, wait_for_scheduler_to_finish_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        # Re-raise exceptions from done tasks
        [task.result() for task in done]
        logger.info("Stopped scheduler at %r", scheduler.address)

    try:
        asyncio_run(run(), loop_factory=get_loop_factory())
    finally:
        logger.info("End scheduler")


if __name__ == "__main__":
    main()  # pragma: no cover
