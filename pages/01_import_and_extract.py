# pages/01_import_and_extract.py
import os
import sys
import zipfile
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
from config.tasks_database import TASKS_DATA
from modules.code_executor import run_user_code_with_timeout
from modules.data_loader import extract_and_load_zip, verify_required_tables
from modules.hint_system import render_hints
from modules.quiz_components import (
    render_column_matching,
    render_fill_one_word,
)
from modules.state_manager import (
    init_session_state,
    record_task_score,
    save_cleaned_checkpoint,
)
from modules.ui_feedback import (
    render_player_badge,
    render_stage_header,
    render_stage_navigation,
)
from modules.validator import check_script_summary

init_session_state()
render_player_badge()

task_cfg = TASKS_DATA["modul_01"]
render_stage_header("01", task_cfg["title"], task_cfg["description"])

# -----------------------------------------------------------------------------
# Bagian 1: Ekstraksi Data Mentah dari Arsip ZIP & Run Mode
# -----------------------------------------------------------------------------
st.subheader("1. Ekstraksi Data Mentah dari Arsip ZIP & Run Mode")
st.markdown(
    "Pipeline berikut memproses file arsip ZIP secara langsung di dalam memori RAM tanpa "
    "menyimpan file sementara ke *disk*. Proses ini membaca setiap file CSV ke dalam kamus "
    "Pandas DataFrame dengan deteksi otomatis pemisah kolom."
)
st.markdown(
    "Jalankan tombol di bawah ini untuk mengekstrak arsip dataset omnichannel, memuat seluruh tabel ke dalam memori sistem, "
    "serta menginspeksi sampel struktur datanya secara langsung."
)

zip_file_path = "data/raw/electronics_omnichannel.zip"

if st.button("Jalankan Ekstraksi & Muat ke Memori", type="primary"):
    if not os.path.exists(zip_file_path):
        st.error(
            f"File tidak ditemukan di `{zip_file_path}`. "
            "Jalankan `python generate_raw_data.py` terlebih dahulu di terminal."
        )
    else:
        with st.status("Mengekstrak dan memvalidasi dataset...", expanded=True) as status:
            st.write("Membaca arsip ZIP multi-CSV...")
            loaded_dfs = extract_and_load_zip(zip_file_path)
            st.write(f"Ditemukan {len(loaded_dfs)} file CSV.")

            required_tables = [
                "products_catalog",
                "customers",
                "online_orders",
                "offline_pos_orders",
                "inventory_stock",
                "returns_warranty",
            ]
            is_valid, missing = verify_required_tables(loaded_dfs, required_tables)

            if is_valid:
                st.session_state["raw_dfs"] = loaded_dfs
                save_cleaned_checkpoint("raw", loaded_dfs)
                status.update(
                    label="Semua tabel berhasil dimuat ke runtime memory!",
                    state="complete",
                    expanded=False,
                )
                st.success("Dataset siap digunakan untuk tahap latihan berikutnya.")
            else:
                status.update(label="Ekstraksi gagal: Tabel tidak lengkap.", state="error")
                st.error(f"Tabel hilang: {missing}")

if "raw_dfs" in st.session_state and st.session_state["raw_dfs"]:
    st.divider()
    selected_table = st.selectbox(
        "Pilih tabel untuk diinspeksi:",
        list(st.session_state["raw_dfs"].keys()),
    )
    df_selected = st.session_state["raw_dfs"][selected_table]

    c1, c2, c3 = st.columns(3)
    c1.metric("Jumlah Baris", f"{df_selected.shape[0]:,}")
    c2.metric("Jumlah Kolom", df_selected.shape[1])
    c3.metric("Total Missing Values", int(df_selected.isnull().sum().sum()))

    st.markdown(f"**Sampel Data Tabel `{selected_table}`:**")
    st.dataframe(df_selected.head(5), use_container_width=True)

st.divider()

# -----------------------------------------------------------------------------
# Bagian 2: Evaluasi Konsep Ekstraksi Data Kompresi
# -----------------------------------------------------------------------------
st.subheader("2. Evaluasi Konsep Ekstraksi Data Kompresi")
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
        0: "Penjelasan: `io.BytesIO()` memungkinkan byte biner dari arsip ZIP dibaca langsung sebagai file virtual di dalam memori RAM oleh Pandas tanpa perlu diekstrak ke hard disk fisik.",
        1: "Penjelasan: Penyimpanan sementara ke disk lambat dan kurang optimal untuk aplikasi web interaktif skala modular.",
        2: "Penjelasan: Pustaka Pandas tidak dapat membaca file ZIP secara langsung tanpa penanganan stream bytes terlebih dahulu.",
        3: "Penjelasan: Ekstraksi penuh ke direktori lokal membebani penyimpanan media dan memperlambat proses I/O."
    }

    st.info(explanations.get(selected_index, "Penjelasan tidak tersedia."))

st.divider()

# -----------------------------------------------------------------------------
# Bagian 3: Pemetaan Metadata File CSV dan Entitas Bisnis
# -----------------------------------------------------------------------------
st.subheader("3. Pemetaan Metadata File CSV dan Entitas Bisnis")
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
# Bagian 4: Penanganan Karakter Delimiter CSV
# -----------------------------------------------------------------------------
st.subheader("4. Penanganan Karakter Delimiter CSV")
st.markdown("Cuplikan data mentah dari file POS:")

sample_preview = (
    "pos_invoice_no;pos_sku_code;pos_cust_contact;transaction_date;store_branch;cashier_id;quantity_sold;raw_subtotal;pos_serial_number;payment_type\n"
    "POS-TX-00001;SKU-EL-161;08509787251;09/02/2026;STORE-JKT-CP;CASHIER-02;1;Rp 455.625;;QRIS\n"
    "POS-TX-00002;SKU-EL-139;08523136154;18/06/2026;STORE-BDG-PVJ;CASHIER-02;1;Rp 5.000.433;;EDC_BCA"
)
if os.path.exists(zip_file_path):
    try:
        with zipfile.ZipFile(zip_file_path, "r") as archive:
            for fname in archive.namelist():
                if "offline_pos_orders.csv" in fname:
                    raw_bytes = archive.read(fname)
                    lines = raw_bytes.decode("utf-8", errors="ignore").splitlines()[:3]
                    sample_preview = "\n".join(lines)
                    break
    except Exception:
        pass

st.code(sample_preview, language="text")

fill_data = task_cfg["fill_one_word"].copy()
fill_data["instruction"] = (
    "Berdasarkan cuplikan data POS di atas, lengkapi parameter fungsi untuk memuat "
    "file ke dalam variabel `df_pos` dengan karakter pemisah yang tepat:"
)
fill_data["code_snippet"] = "df_pos = pd.read_csv(file_buffer, sep='___')"

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
# Bagian 5: Implementasi Skrip Inspeksi Skema Tabel
# -----------------------------------------------------------------------------
st.subheader("5. Implementasi Skrip Inspeksi Skema Tabel")
script_data = task_cfg["script_task"].copy()
script_data["starter_code"] = """summary = {}
for name, df in raw_dfs.items():
    summary[name] = df.___
"""
st.markdown(f"**Instruksi:** {script_data['instruction']}")

render_hints(script_data["task_id"], script_data["hints"])

user_script = st.text_area(
    "Editor Kode Python:",
    value=script_data["starter_code"],
    height=180,
    key=f"editor_{script_data['task_id']}",
)

if st.button("Jalankan Skrip & Validasi", type="primary"):
    if "___" in user_script:
        st.warning("Harap lengkapi semua bagian '___' sebelum mengeksekusi kode.")
    elif "raw_dfs" not in st.session_state or not st.session_state["raw_dfs"]:
        st.warning("Silakan ekstrak dataset terlebih dahulu pada Bagian 1 di atas.")
    else:
        with st.spinner("Mengeksekusi skrip dalam sandbox..."):
            context = {"raw_dfs": st.session_state["raw_dfs"]}
            success, result_env, logs = run_user_code_with_timeout(
                user_script, context, timeout_seconds=5
            )

            if success:
                required_tbs = list(st.session_state["raw_dfs"].keys())
                is_valid_summary, msg = check_script_summary(result_env, required_tbs)

                if is_valid_summary:
                    st.success("Skrip berhasil dieksekusi dan divalidasi dengan benar!")
                    if logs.strip():
                        st.text_area("Output Eksekusi (stdout):", logs, height=120)
                    record_task_score(
                        script_data["task_id"],
                        script_data["points"],
                        max_points=script_data["points"],
                    )
                else:
                    st.error(f"Validasi Gagal: {msg}")
            else:
                st.error(f"Eksekusi Gagal:\n{logs}")

# -----------------------------------------------------------------------------
# Navigasi Tahap Berdasarkan Status Penyelesaian Task
# -----------------------------------------------------------------------------
stage_01_tasks = [
    mcq_data["task_id"],
    match_data["task_id"],
    fill_data["task_id"],
    script_data["task_id"],
]

render_stage_navigation(
    current_tasks=stage_01_tasks,
    next_page_path="pages/02_missing_and_duplicates.py",
    next_label="Lanjut ke Sesi Berikutnya: Missing & Duplicates",
)
