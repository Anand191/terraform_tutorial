import time
from functools import wraps
from pathlib import Path
from typing import Dict

import yaml
from dotenv import find_dotenv, load_dotenv


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


def load_env():
    load_dotenv(find_dotenv(".env_dev"))


def load_conf(project_root: str) -> Dict:
    root = Path(project_root)
    conf_path = root / "ai_assistant" / "config.yaml"
    with open(conf_path) as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
    return cfg
