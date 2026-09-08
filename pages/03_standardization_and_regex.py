# pages/03_standardization_and_regex.py
import sys
from pathlib import Path

# 1. Path Resolver
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import pandas as pd
import streamlit as st
from config.tasks_database import TASKS_DATA
from modules.code_executor import run_user_code_with_timeout
from modules.hint_system import render_hints
from modules.quiz_components import (
    render_column_matching,
    render_fill_one_word,
)
from modules.state_manager import (
    get_latest_dataframe,
    init_session_state,
    record_task_score,
    save_cleaned_checkpoint,
)
from modules.ui_feedback import (
    render_player_badge,
    render_stage_header,
    render_stage_navigation,
)

# Inisialisasi State Sesi & Header
init_session_state()
render_player_badge()

task_cfg = TASKS_DATA["modul_03"]
render_stage_header("03", task_cfg["title"], task_cfg["description"])

# Ambil data dari stage sebelumnya
df_products_raw = get_latest_dataframe("products_catalog")
df_customers_raw = get_latest_dataframe("customers")
df_pos_raw = get_latest_dataframe("offline_pos_orders")

if df_products_raw is None or df_customers_raw is None or df_pos_raw is None:
    st.warning("Dataset belum dimuat. Jalankan modul '01' dan '02' terlebih dahulu.")
    st.stop()

# -----------------------------------------------------------------------------
# Bagian 1: Diagnostik String Kotor & Konsep Regex
# -----------------------------------------------------------------------------
st.subheader("1. Diagnostik String Kotor & Konsep Regex")
st.markdown(
    "**Apa itu Regex?** Regular Expression (Regex) adalah pola urutan karakter yang digunakan "
    "untuk mencari, mencocokkan, atau memanipulasi teks secara spesifik.\n\n"
    "**Mengapa Regex Penting dalam Analisis Data?** Data mentah dunia nyata hampir selalu berantakan "
    "(misalnya harga produk yang bercampur huruf/simbol mata uang atau nomor telepon dengan format tanda hubung acak). "
    "Regex memungkinkan Anda membersihkan teks kompleks pada jutaan baris data secara otomatis tanpa perulangan manual."
)
st.markdown(
    "Jalankan tombol di bawah ini untuk memindai sampel nilai kotor pada kolom harga produk, "
    "nomor kontak pelanggan, dan format tanggal transaksi POS dari memori sistem."
)

st.code(
    """# Kode Inspeksi String Kotor
import pandas as pd

sample_prices = df_products['raw_price'].dropna().unique()[:3]
sample_phones = df_customers['contact_phone'].dropna().unique()[:3]
sample_dates = df_pos['transaction_date'].dropna().unique()[:3]
""",
    language="python",
)

if st.button("Jalankan Inspeksi String Kotor", type="primary"):
    with st.spinner("Memindai anomali format data..."):
        sample_prices = df_products_raw["raw_price"].dropna().unique()[:3].tolist()
        sample_phones = df_customers_raw["contact_phone"].dropna().unique()[:3].tolist()
        sample_dates = df_pos_raw["transaction_date"].dropna().unique()[:3].tolist()

        st.session_state["diag_run_stage_03"] = True
        st.session_state["diag_samples_03"] = {
            "prices": sample_prices,
            "phones": sample_phones,
            "dates": sample_dates,
        }

if st.session_state.get("diag_run_stage_03", False):
    samples = st.session_state["diag_samples_03"]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Sampel Format Harga:**")
        for p in samples["prices"]:
            st.code(str(p), language="text")
    with col2:
        st.markdown("**Sampel Format Kontak:**")
        for ph in samples["phones"]:
            st.code(str(ph), language="text")
    with col3:
        st.markdown("**Sampel Tanggal POS:**")
        for d in samples["dates"]:
            st.code(str(d), language="text")
    
    st.success("Inspeksi string selesai. Gunakan pemahaman Anda untuk menyelesaikan latihan praktik di bawah.")

st.divider()

# -----------------------------------------------------------------------------
# Bagian 2: Evaluasi Pola Pencarian Karakter Menggunakan Regex
# -----------------------------------------------------------------------------
st.subheader("2. Evaluasi Pola Pencarian Karakter Menggunakan Regex")
mcq_data = task_cfg["mcq"]
st.markdown(f"**Soal:** {mcq_data['question']}")

mcq_key = f"mcq_eval_{mcq_data['task_id']}"
submitted_key = f"mcq_submitted_{mcq_data['task_id']}"

selected_option = st.radio(
    "Pilih jawaban yang paling tepat:",
    options=mcq_data["options"],
    key=mcq_key,
)

if st.button("Kirim Jawaban", key=f"btn_{mcq_data['task_id']}"):
    st.session_state[submitted_key] = True

if st.session_state.get(submitted_key, False):
    selected_index = mcq_data["options"].index(selected_option)
    is_correct = (selected_index == mcq_data["correct_index"])

    if is_correct:
        st.success("Jawaban Anda Benar!")
        record_task_score(mcq_data["task_id"], mcq_data["points"], max_points=mcq_data["points"])
    else:
        st.error("Jawaban Anda Belum Tepat.")

    explanations = {
        0: "Penjelasan: `r'[^0-9]'` adalah jawaban yang tepat. Tanda caret (`^`) di dalam kurung siku berfungsi sebagai negasi (kecuali), sehingga mencocokkan karakter apa pun selain angka (non-digit).",
        1: "Penjelasan: `r'[a-zA-Z]'` kurang tepat karena pola ini hanya mencocokkan huruf alfabet (huruf besar dan kecil), bukan seluruh karakter non-digit.",
        2: "Penjelasan: `r'\\d+'` keliru karena pola ini justru digunakan untuk mencari dan mencocokkan digit angka, bukan karakter non-digit.",
        3: "Penjelasan: `r'[\\s,.]'` keliru karena pola ini hanya mencocokkan karakter spasi, tanda koma, dan titik secara spesifik, bukan seluruh karakter non-digit."
    }

    st.info(explanations.get(selected_index, "Penjelasan tidak tersedia."))

st.divider()

# -----------------------------------------------------------------------------
# Bagian 3: Pemetaan Direktif Format Tanggal (Datetime Parsing)
# -----------------------------------------------------------------------------
st.subheader("3. Pemetaan Direktif Format Tanggal (Datetime Parsing)")
match_data = task_cfg["matching"]
st.markdown(f"**Instruksi:** {match_data['title']}")

render_column_matching(
    task_id=match_data["task_id"],
    title="",
    source_columns=match_data["sources"],
    target_options=match_data["targets"],
    correct_mapping=match_data["correct_mapping"],
    points=match_data["points"],
)

st.divider()

# -----------------------------------------------------------------------------
# Bagian 4: Konversi Tipe Data String ke Datetime di Pandas
# -----------------------------------------------------------------------------
st.subheader("4. Konversi Tipe Data String ke Datetime di Pandas")
fill_data = task_cfg["fill_one_word"]

render_hints(fill_data["task_id"], fill_data.get("hints", []))

render_fill_one_word(
    task_id=fill_data["task_id"],
    instruction=fill_data["instruction"],
    code_snippet=fill_data["code_snippet"],
    correct_keywords=fill_data["correct_keywords"],
    points=fill_data["points"],
)

st.divider()

# -----------------------------------------------------------------------------
# Bagian 5: Praktik Koding Pembersihan Harga dan Kontak Pelanggan
# -----------------------------------------------------------------------------
st.subheader("5. Praktik Koding Pembersihan Harga dan Kontak Pelanggan")
script_data = task_cfg["script_task"]
st.markdown(f"**Instruksi:** {script_data['instruction']}")

render_hints(script_data["task_id"], script_data["hints"])

user_script = st.text_area(
    "Editor Kode Python:",
    value=script_data["starter_code"],
    height=260,
    key=f"editor_{script_data['task_id']}",
)

if st.button("Jalankan Skrip & Validasi Standarisasi", type="primary"):
    if "___" in user_script:
        st.warning("Harap lengkapi semua bagian '___' sebelum mengeksekusi kode.")
    else:
        with st.spinner("Mengeksekusi skrip pembersihan regex dan datetime..."):
            context = {
                "df_products": df_products_raw.copy(),
                "df_customers": df_customers_raw.copy(),
                "df_pos": df_pos_raw.copy(),
            }
            success, result_env, logs = run_user_code_with_timeout(
                user_script, context, timeout_seconds=5
            )

            if not success:
                st.error(f"Eksekusi Gagal:\n{logs}")
            else:
                errors = []
                if "df_products_clean" not in result_env:
                    errors.append("Variabel `df_products_clean` tidak ditemukan.")
                if "df_customers_clean" not in result_env:
                    errors.append("Variabel `df_customers_clean` tidak ditemukan.")
                if "df_pos_clean" not in result_env:
                    errors.append("Variabel `df_pos_clean` tidak ditemukan.")

                if not errors:
                    df_prod_res = result_env["df_products_clean"]
                    df_pos_res = result_env["df_pos_clean"]

                    if "clean_price" not in df_prod_res.columns or not pd.api.types.is_integer_dtype(df_prod_res["clean_price"]):
                        errors.append("Kolom 'clean_price' harus bertipe Integer.")
                    if "tx_datetime" not in df_pos_res.columns or not pd.api.types.is_datetime64_any_dtype(df_pos_res["tx_datetime"]):
                        errors.append("Kolom 'tx_datetime' harus bertipe Datetime.")

                if errors:
                    for err in errors:
                        st.error(f"Audit Gagal: {err}")
                else:
                    st.success("Validasi Berhasil! Harga, kontak, dan tanggal telah terstandarisasi.")
                    save_cleaned_checkpoint(
                        "stage_03",
                        {
                            "products_catalog": result_env["df_products_clean"],
                            "customers": result_env["df_customers_clean"],
                            "offline_pos_orders": result_env["df_pos_clean"],
                        },
                    )
                    record_task_score(
                        script_data["task_id"],
                        script_data["points"],
                        max_points=script_data["points"],
                    )

# -----------------------------------------------------------------------------
# Navigasi Tahap Berdasarkan Status Penyelesaian Task
# -----------------------------------------------------------------------------
stage_03_tasks = [
    mcq_data["task_id"],
    match_data["task_id"],
    fill_data["task_id"],
    script_data["task_id"],
]

render_stage_navigation(
    current_tasks=stage_03_tasks,
    next_page_path="pages/04_omnichannel_merge.py",
    next_label="Lanjut ke Sesi Berikutnya: Omnichannel Merge",
)
