import time

# Defining the example methods


def constant(value: int) -> int:
    """Returns a constant value."""
    return value


def load_data(path: str) -> list[int]:
    """Simulates loading data from a file."""
    print(f"Loading data from {path}")
    time.sleep(2)
    return list(range(10))


def filter_data(data: list[int], threshold: int) -> list[int]:
    """Filters data based on a threshold."""
    print(f"Filtering data with threshold {threshold}")
    time.sleep(2)
    return [x for x in data if x > threshold]


def sum_data(data: list[int]) -> int:
    """Sums the data."""
    print("Summing data")
    return sum(data)


def merge_data(data0: list[int], data1: list[int]) -> list[int]:
    """Merges two data lists."""
    print("Merging data")
    time.sleep(1)
    return data0 + data1
