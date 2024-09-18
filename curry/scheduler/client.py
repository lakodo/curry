from dask.distributed import Client, LocalCluster

cluster = LocalCluster(threads_per_worker=1, n_workers=1)
print("Creating default locak client for Dask")
default_local_client = Client(cluster)
