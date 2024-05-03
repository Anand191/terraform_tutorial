import time
from functools import wraps


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        exec_time = end_time - start_time
        print(f"Function {func.__name__}{args} {kwargs} took {exec_time:.4f} sec")
        return result

    return timeit_wrapper
