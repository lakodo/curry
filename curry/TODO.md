# TODO


- start with obvious blocks (loading data, saving data, dummy python function execution, log, export to csv)
- try to plot a time serie and some intervals
- use Jinja2 with a fastapi app in the server folder -> each block should generate a template for its specific needs (see Block.producer)

## Goal

Curry's goal is to handle flows of blocks and hide Dask behind the scenes.

## Example

Example of a flow:

```python

import curry
# 1. Enlist blocks
# 2. Enlist workers
# 3. Build a flow (a graph of blocks)
# 4. Execute the flow

```
