# pages/02_missing_and_duplicates.py
import sys
from pathlib import Path

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

init_session_state()
render_player_badge()

task_cfg = TASKS_DATA["modul_02"]
render_stage_header("02", task_cfg["title"], task_cfg["description"])

df_online_raw = get_latest_dataframe("online_orders")
df_pos_raw = get_latest_dataframe("offline_pos_orders")

if df_online_raw is None or df_pos_raw is None:
    st.warning(
        "Dataset belum dimuat ke runtime memory. "
        "Silakan buka halaman '01_import_and_extract' terlebih dahulu untuk mengekstrak data mentah."
    )
    st.stop()

# -----------------------------------------------------------------------------
# Bagian 1: Diagnostik Data Transaksi dan Anomali
# -----------------------------------------------------------------------------
st.subheader("1. Diagnostik Data Transaksi dan Anomali")
st.markdown(
    "Data duplikat (seperti pesanan online ganda akibat kegagalan jaringan atau double click) mendistorsi total perhitungan pendapatan riil. "
    "Nilai kosong atau anomali pada kontak pelanggan kasir POS memerlukan imputasi agar profil transaksi tetap akurat."
)
st.markdown(
    "Jalankan tombol di bawah ini untuk memeriksa anomali duplikasi pada transaksi online, "
    "data kontak kosong pada kasir POS, serta menampilkan sampel data anomali secara langsung dari memori sistem."
)

if st.button("Jalankan Inspeksi Data", type="primary"):
    with st.spinner("Menganalisis anomali data..."):
        total_online = len(df_online_raw)
        dupe_online = df_online_raw.duplicated(subset=["order_id"]).sum()
        
        total_pos = len(df_pos_raw)
        invalid_contacts = df_pos_raw["pos_cust_contact"].isin(
            [None, "-", "GUEST", "NON_MEMBER", "0000"]
        ).sum() + df_pos_raw["pos_cust_contact"].isnull().sum()

        sample_dupes = df_online_raw[df_online_raw.duplicated(subset=["order_id"], keep=False)].head(2)
        sample_invalid_pos = df_pos_raw[
            df_pos_raw["pos_cust_contact"].isin([None, "-", "GUEST", "NON_MEMBER", "0000"]) | 
            df_pos_raw["pos_cust_contact"].isnull()
        ].head(2)

        st.session_state["diag_run_stage_02"] = True
        st.session_state["diag_metrics"] = {
            "total_online": total_online,
            "dupe_online": dupe_online,
            "total_pos": total_pos,
            "invalid_contacts": invalid_contacts,
            "sample_dupes": sample_dupes,
            "sample_invalid_pos": sample_invalid_pos,
        }

if st.session_state.get("diag_run_stage_02", False):
    metrics = st.session_state["diag_metrics"]
    col_diag1, col_diag2 = st.columns(2)
    with col_diag1:
        st.metric("Total Baris Online Orders", f"{metrics['total_online']:,}")
        st.metric("Duplikasi order_id", f"{metrics['dupe_online']:,}", delta="Anomali", delta_color="inverse")
    with col_diag2:
        st.metric("Total Baris POS Orders", f"{metrics['total_pos']:,}")
        st.metric("Kontak Kosong atau Anonim", f"{metrics['invalid_contacts']:,}", delta="Anomali", delta_color="inverse")
    
    if not metrics["sample_dupes"].empty:
        st.markdown("**Sampel Transaksi Online Duplikat**")
        desired_cols = ['order_id', 'customer_id', 'order_status', 'order_date']
        available_cols = [col for col in desired_cols if col in metrics["sample_dupes"].columns]
        st.dataframe(metrics["sample_dupes"][available_cols], hide_index=True)
    
    if not metrics["sample_invalid_pos"].empty:
        st.markdown("**Sampel Transaksi POS Kontak Kosong atau Anonim**")
        desired_pos_cols = ['pos_invoice_no', 'pos_sku_code', 'pos_cust_contact', 'store_branch']
        available_pos_cols = [col for col in desired_pos_cols if col in metrics["sample_invalid_pos"].columns]
        st.dataframe(metrics["sample_invalid_pos"][available_pos_cols], hide_index=True)

    st.success("Inspeksi selesai. Gunakan pemahaman Anda untuk menyelesaikan latihan praktik di bawah.")

st.divider()

# -----------------------------------------------------------------------------
# Bagian 2: Evaluasi Konsep Duplikasi Transaksi Online
# -----------------------------------------------------------------------------
st.subheader("2. Evaluasi Konsep Duplikasi Transaksi Online")
mcq_data = task_cfg["mcq"]
st.markdown(f"**Soal:** {mcq_data['question']}")

mcq_key = f"mcq_eval_{mcq_data['task_id']}"
submitted_key = f"mcq_submitted_{mcq_data['task_id']}"

selected_option = st.radio(
    "Pilih jawaban yang paling tepat",
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
        0: "Penjelasan: `drop_duplicates(subset=['order_id'], keep='first')` adalah metode yang tepat untuk menghapus baris duplikat berdasarkan kolom kunci unik transaksi dan mempertahankan catatan awal.",
        1: "Penjelasan: `dropna()` keliru karena fungsi tersebut digunakan untuk membuang baris yang memiliki nilai kosong (null), bukan baris duplikat.",
        2: "Penjelasan: `fillna()` keliru karena digunakan untuk mengisi nilai kosong, bukan menghapus data duplikat.",
        3: "Penjelasan: `groupby()` keliru karena merupakan fungsi agregasi kelompok dan bukan perintah deduplikasi data langsung."
    }

    st.info(explanations.get(selected_index, "Penjelasan tidak tersedia."))

st.divider()

# -----------------------------------------------------------------------------
# Bagian 3: Strategi Penanganan Nilai Kosong dan Duplikat
# -----------------------------------------------------------------------------
st.subheader("3. Strategi Penanganan Nilai Kosong dan Duplikat")
match_data = task_cfg["matching"]
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
# Bagian 4: Parameter Fungsi Deduplikasi Data
# -----------------------------------------------------------------------------
st.subheader("4. Parameter Fungsi Deduplikasi Data")
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
# Bagian 5: Implementasi Skrip Pembersihan dan Imputasi
# -----------------------------------------------------------------------------
st.subheader("5. Implementasi Skrip Pembersihan dan Imputasi")
script_data = task_cfg["script_task"]
st.markdown(f"**Instruksi:** {script_data['instruction']}")

render_hints(script_data["task_id"], script_data["hints"])

user_script = st.text_area(
    "Editor Kode Python",
    value=script_data["starter_code"],
    height=220,
    key=f"editor_{script_data['task_id']}",
)

if st.button("Jalankan Skrip & Validasi Hasil", type="primary"):
    if "___" in user_script:
        st.warning("Harap lengkapi semua bagian '___' sebelum mengeksekusi kode.")
    else:
        with st.spinner("Mengeksekusi skrip dan menguji integritas data..."):
            context = {
                "df_online": df_online_raw.copy(),
                "df_pos": df_pos_raw.copy(),
            }
            success, result_env, logs = run_user_code_with_timeout(
                user_script, context, timeout_seconds=5
            )

            if not success:
                st.error(f"Eksekusi Gagal:\n{logs}")
            else:
                errors = []
                if "df_online_dedup" not in result_env:
                    errors.append("Variabel `df_online_dedup` tidak ditemukan.")
                if "df_pos_imputed" not in result_env:
                    errors.append("Variabel `df_pos_imputed` tidak ditemukan.")

                if not errors:
                    df_onl_res = result_env["df_online_dedup"]
                    df_pos_res = result_env["df_pos_imputed"]

                    dupes_left = df_onl_res.duplicated(subset=["order_id"]).sum()
                    if dupes_left > 0:
                        errors.append(f"Masih terdapat {dupes_left} order_id duplikat.")

                    invalid_pos_left = df_pos_res["pos_cust_contact"].isin(
                        [None, "-", "GUEST", "NON_MEMBER", "0000"]
                    ).sum() + df_pos_res["pos_cust_contact"].isnull().sum()
                    if invalid_pos_left > 0:
                        errors.append(f"Masih terdapat {invalid_pos_left} kontak yang belum diimputasi.")

                if errors:
                    for err in errors:
                        st.error(f"Audit Gagal: {err}")
                else:
                    st.success("Validasi Sempurna! Duplikasi berhasil dibuang dan kontak POS terimputasi.")
                    save_cleaned_checkpoint(
                        "stage_02",
                        {
                            "online_orders": result_env["df_online_dedup"],
                            "offline_pos_orders": result_env["df_pos_imputed"],
                        },
                    )
                    record_task_score(
                        script_data["task_id"],
                        script_data["points"],
                        max_points=script_data["points"],
                    )

                    m1, m2 = st.columns(2)
                    m1.metric(
                        "Baris Online Orders Bersih",
                        f"{len(result_env['df_online_dedup']):,}",
                        delta=f"-{len(df_online_raw) - len(result_env['df_online_dedup'])} Duplikat",
                    )
                    m2.metric(
                        "Total GUEST_OFFLINE Imputed",
                        f"{(result_env['df_pos_imputed']['pos_cust_contact'] == 'GUEST_OFFLINE').sum():,}",
                    )

# -----------------------------------------------------------------------------
# Navigasi Tahap Berdasarkan Status Penyelesaian Task
# -----------------------------------------------------------------------------
stage_02_tasks = [
    mcq_data["task_id"],
    match_data["task_id"],
    fill_data["task_id"],
    script_data["task_id"],
]

render_stage_navigation(
    current_tasks=stage_02_tasks,
    next_page_path="pages/03_standardization_and_regex.py",
    next_label="Lanjut ke Sesi Berikutnya: Standardization & Regex",
)
