# TODO

## Next steps

### 0/ intégrer sqlite

~~- utiliser sqlite pour sauvegarder un flow (sqlalchemy!)~~

- creer un model de flow
- utilsier des boutons avec requet GET pour le modifier (cf 1/)

### 1/ block flow builder

> penser non interactif
dans le endpoint builder/{workflow_id}

lister les blocks possibles à droite
afficher un select en dessous du dernier block pour choisir le prochaiun block
avoir un formalisme d'input output pour matcher les transactions (sort de rendering prefix du block)

- en fonction des outputs du blocs d'avant on peut proposer les blocs compatibles et en plus un bloc de "fin"

### 2/ dask progress and result display

-

## Autre

- dask (à part) to get progress from client
  - add localcluster to some new dask module
  - find a way to get progress from it
- ws bassis to exchange data
- front alpinejs to relay data without refreshing
- start with obvious blocks (loading data, saving data, dummy python function execution, log, export to csv)
- try to plot a time serie and some intervals
- submit tasks from tasks <https://github.com/dask/dask-examples/blob/main/applications/evolving-workflows.ipynb>

## App structure

- flow builder/study/notebook : play with blocks and build some processes
- apps/dashboards/regular flows: register a flow as a "static" flow
- admin-workers: enlist workers and connect to scheduler(s)

## Extra

use validate_call of registered function
from pydantic import ValidationError, validate_call

## Dasks examples

- prophet block (<https://github.com/dask/dask-examples/blob/main/applications/forecasting-with-prophet.ipynb>)
- worker resilience: <https://examples.dask.org/resilience.html>
- evolving workflows <https://github.com/dask/dask-examples/blob/main/applications/evolving-workflows.ipynb>
- <https://docs.dask.org/en/stable/deploying-python-advanced.html>
