import time
from functools import wraps


def timing_decorator(func):
    """
    Measures the execution time of a function.

    Args:
        func (function): Function to be timed.

    Returns:
        tuple: Function result and elapsed time.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        return result, elapsed_time
    return wrapper

@timing_decorator
def compute_indicateur1():
    return 42