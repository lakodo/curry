# Curry

[![Release](https://img.shields.io/github/v/release/lakodo/curry)](https://img.shields.io/github/v/release/lakodo/curry)
[![Build status](https://img.shields.io/github/actions/workflow/status/lakodo/curry/main.yml?branch=main)](https://github.com/lakodo/curry/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/lakodo/curry/branch/main/graph/badge.svg)](https://codecov.io/gh/lakodo/curry)
[![Commit activity](https://img.shields.io/github/commit-activity/m/lakodo/curry)](https://img.shields.io/github/commit-activity/m/lakodo/curry)
[![License](https://img.shields.io/github/license/lakodo/curry)](https://img.shields.io/github/license/lakodo/curry)

Wrap dask scheduler to make it easy to buid datascience flow

- **Github repository**: <https://github.com/lakodo/curry/>
- **Documentation** <https://lakodo.github.io/curry/>

#

## Dev

### Run the server

```shell
make run-server
```

### Run the demo script

```shell
# Install uv is not already done
pip install uv
# or
pipx intall uv
# or (cleaner)
curl -LsSf https://astral.sh/uv/install.sh | sh


# launch the demo
uv run python curry/demos/existing_functions/demo.py
# you can open the "mydask.png" file to see the Dask graph generated by this workflow.
```

Using make:

```
make run-demo
```

### Run tailwind postcss

```shell
# it's a watch process
npm run build:css
```