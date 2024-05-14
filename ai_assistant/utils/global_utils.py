import logging
import time
from functools import wraps
from itertools import chain
from pathlib import Path
from types import FrameType
from typing import Dict, cast

import yaml
from dotenv import find_dotenv, load_dotenv
from loguru import logger


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


class InterceptHandler(logging.Handler):
    """Logs to loguru from Python logging module"""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
            frame = cast(FrameType, frame.f_back)
            depth += 1
        logger_with_opts = logger.opt(depth=depth, exception=record.exc_info)
        try:
            logger_with_opts.log(level, "{}", record.getMessage())
        except Exception as e:
            safe_msg = getattr(record, "msg", None) or str(record)
            logger_with_opts.warning(
                "Exception logging the following native logger message: {}, {!r}",
                safe_msg,
                e,
            )


def setup_loguru_logging_interceptor(level=logging.DEBUG, modules=()):
    logging.basicConfig(handlers=[InterceptHandler()], level=level)  # noqa
    for logger_name in chain(("",), modules):
        mod_logger = logging.getLogger(logger_name)
        mod_logger.handlers = [InterceptHandler(level=level)]
        mod_logger.propagate = False
