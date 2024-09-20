"""
Launch with:
```shell
srun -n 1 dynamic_workload.py
```
"""

from dask_jobqueue.slurm import SLURMCluster

cluster = SLURMCluster()
cluster.adapt(minimum=1, maximum=10)  # Tells Dask to call `srun -n 1 ...` when it needs new workers
