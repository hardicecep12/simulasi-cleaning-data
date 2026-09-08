# modules/code_executor.py
import contextlib
import io
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
import numpy as np
import pandas as pd


def _safe_copy_var(v):
    if isinstance(v, pd.DataFrame):
        return v.copy()
    elif isinstance(v, dict):
        return {k: _safe_copy_var(sub_v) for k, sub_v in v.items()}
    return v


def _run_script(code_str: str, context: dict, stdout_capture: io.StringIO):
    with contextlib.redirect_stdout(stdout_capture):
        # Gunakan context sebagai globals dan locals sekaligus agar variabel terbaca global di dalam loop
        exec(code_str, context, context)


def run_user_code_with_timeout(
    code_str: str,
    context_vars: dict,
    timeout_seconds: int = 5,
) -> tuple[bool, dict, str]:
    """
    Mengeksekusi skrip user dengan isolasi variabel dan batas waktu eksekusi.
    
    Returns:
        (success: bool, updated_context: dict, output_or_error_message: str)
    """
    exec_env = {
        "pd": pd,
        "np": np,
        **{k: _safe_copy_var(v) for k, v in context_vars.items()},
    }

    stdout_capture = io.StringIO()

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_run_script, code_str, exec_env, stdout_capture)
        try:
            future.result(timeout=timeout_seconds)
            return True, exec_env, stdout_capture.getvalue()
        except FutureTimeout:
            return (
                False,
                {},
                f"Batas waktu eksekusi ({timeout_seconds} detik) terlampaui. "
                "Periksa apakah ada perulangan tanpa henti (infinite loop).",
            )
        except Exception as err:
            return False, {}, f"{type(err).__name__}: {str(err)}"
