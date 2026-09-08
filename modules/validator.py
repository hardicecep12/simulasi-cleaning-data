# modules/validator.py
import pandas as pd


def check_schema_columns(
    df: pd.DataFrame, required_cols: list[str]
) -> tuple[bool, str]:
    """Memeriksa keberadaan kolom-kolom wajib."""
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        return False, f"Kolom berikut tidak ditemukan: {missing}"
    return True, "Semua kolom wajib tersedia."


def check_no_nulls(
    df: pd.DataFrame, target_cols: list[str]
) -> tuple[bool, str]:
    """Memeriksa tidak adanya nilai null pada kolom penting."""
    null_counts = df[target_cols].isnull().sum()
    failed_cols = null_counts[null_counts > 0]
    if not failed_cols.empty:
        return (
            False,
            f"Masih terdapat nilai null pada kolom: {dict(failed_cols)}",
        )
    return True, "Tidak ada nilai null pada kolom target."


def check_numeric_range(
    df: pd.DataFrame, col: str, min_val: float, max_val: float
) -> tuple[bool, str]:
    """Memeriksa apakah seluruh nilai numerik berada dalam batas wajar."""
    if not pd.api.types.is_numeric_dtype(df[col]):
        return False, f"Kolom '{col}' harus bertipe numerik (int/float)."
    out_of_bounds = df[(df[col] < min_val) | (df[col] > max_val)]
    if len(out_of_bounds) > 0:
        return (
            False,
            f"Ditemukan {len(out_of_bounds)} baris di luar rentang [{min_val}, {max_val}] pada kolom '{col}'.",
        )
    return True, f"Seluruh nilai pada kolom '{col}' valid dalam rentang."


def check_script_summary(
    result_env: dict, required_tables: list[str]
) -> tuple[bool, str]:
    """Memvalidasi hasil dictionary summary dari skrip manual (Task 5)."""
    if "summary" not in result_env:
        return False, "Variabel 'summary' belum didefinisikan dalam skrip."
    
    summary = result_env["summary"]
    if not isinstance(summary, dict):
        return False, "Variabel 'summary' harus berupa tipe data dictionary."

    missing = [t for t in required_tables if t not in summary]
    if missing:
        return False, f"Dictionary summary belum memuat tabel: {missing}"

    for table in required_tables:
        val = summary[table]
        if not isinstance(val, tuple) or len(val) != 2:
            return False, f"Nilai untuk tabel '{table}' harus berupa tuple (baris, kolom)."

    return True, "Skrip berhasil menghasilkan summary dimensi tabel dengan benar."
