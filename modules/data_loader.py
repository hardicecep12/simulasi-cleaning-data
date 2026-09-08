# modules/data_loader.py
import io
import os
import zipfile
import pandas as pd
import streamlit as st


@st.cache_data(show_spinner=False)
def extract_and_load_zip(zip_path: str) -> dict[str, pd.DataFrame]:
    """Mengekstrak file ZIP dan memuat seluruh CSV ke dictionary DataFrame in-memory."""
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"File ZIP tidak ditemukan di: {zip_path}")

    loaded_dfs = {}
    with zipfile.ZipFile(zip_path, "r") as archive:
        file_list = [f for f in archive.namelist() if f.endswith(".csv")]

        for file_name in file_list:
            table_name = os.path.basename(file_name).replace(".csv", "")
            raw_bytes = archive.read(file_name)

            # Deteksi delimiter (koma vs titik koma) dari sampel baris pertama
            sample_text = raw_bytes[:1024].decode("utf-8", errors="ignore")
            first_line = (
                sample_text.splitlines()[0] if sample_text.splitlines() else ""
            )
            delimiter = ";" if first_line.count(";") > first_line.count(",") else ","

            # Load ke pandas DataFrame
            df = pd.read_csv(io.BytesIO(raw_bytes), sep=delimiter)
            loaded_dfs[table_name] = df

    return loaded_dfs


def verify_required_tables(
    loaded_dfs: dict, required_tables: list[str]
) -> tuple[bool, list[str]]:
    """Memverifikasi kelengkapan tabel yang diperlukan."""
    missing = [tbl for tbl in required_tables if tbl not in loaded_dfs]
    return len(missing) == 0, missing
