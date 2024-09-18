# TODO

https://docs.dask.org/en/stable/deploying-python-advanced.html
- launch dask in another process (create make command)
- remove dask client from server
- configure server dask client to use the dask cluster (.env/settings_pydantic ?)



- dask (à part) to get progress from client
    - add localcluster to some new dask module
    - find a way to get progress from it
- ws bassis to exchange data
- front alpinejs to relay data without refreshing
- start with obvious blocks (loading data, saving data, dummy python function execution, log, export to csv)
- try to plot a time serie and some intervals
- submit tasks from tasks https://github.com/dask/dask-examples/blob/main/applications/evolving-workflows.ipynb


## Extra

use validate_call of registered function
from pydantic import ValidationError, validate_call

## Quick wins 

- prophet block (https://github.com/dask/dask-examples/blob/main/applications/forecasting-with-prophet.ipynb)
- worker resilience: https://examples.dask.org/resilience.html
- evolving workflows https://github.com/dask/dask-examples/blob/main/applications/evolving-workflows.ipynb