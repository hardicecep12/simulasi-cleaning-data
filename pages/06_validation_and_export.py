# pages/06_validation_and_export.py
import io
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
)
from modules.ui_feedback import render_player_badge, render_stage_header

# Inisialisasi State Sesi & Header
init_session_state()
render_player_badge()

task_cfg = TASKS_DATA["modul_06"]
render_stage_header("06", task_cfg["title"], task_cfg["description"])

# Ambil master data hasil stage 05 dengan pemulihan otomatis
df_clean_master = get_latest_dataframe("clean_master")

if df_clean_master is None:
    df_master_alt = get_latest_dataframe("omnichannel_master")
    if df_master_alt is not None:
        with st.spinner("Memulihkan dan membersihkan data otomatis dari tahap sebelumnya..."):
            df_clean = df_master_alt[df_master_alt["qty"] > 0].copy()
            df_clean["discount_rate"] = df_clean["discount_rate"].clip(lower=0.0, upper=1.0)
            q1 = df_clean["qty"].quantile(0.25)
            q3 = df_clean["qty"].quantile(0.75)
            iqr = q3 - q1
            upper_limit = q3 + (1.5 * iqr)
            df_clean["is_bulk_buyer"] = df_clean["qty"] > upper_limit
            df_clean_master = df_clean
    else:
        st.warning("Master dataset bersih belum tersedia. Selesaikan seluruh tahapan modul sebelumnya terlebih dahulu.")
        st.stop()

# -----------------------------------------------------------------------------
# Bagian 1: Audit Mutu Data
# -----------------------------------------------------------------------------
st.subheader("1. Audit Mutu Data")
st.markdown(
    "Sebelum dataset siap digunakan oleh tim "
    "Business Intelligence atau model *Machine Learning*, kualitas data harus diprofiling secara menyeluruh "
    "(memastikan tidak ada *null values* pada kolom wajib, keunikan ID transaksi, dan konsistensi tipe data). "
    "Format Apache Parquet dipilih karena mendukung kompresi kolom yang efisien dan penyimpanan skema natif."
)
st.markdown(
    "Jalankan tombol di bawah ini untuk memeriksa profil integritas akhir dataset omnichannel dan menampilkan sampel data bersih dari memori sistem."
)

if st.button("Jalankan Audit Profiling Mutu Data", type="primary"):
    with st.spinner("Menganalisis profil data akhir..."):
        total_rows = len(df_clean_master)
        null_count = int(df_clean_master.isnull().sum().sum())
        unique_orders = df_clean_master["order_id"].nunique() if "order_id" in df_clean_master.columns else len(df_clean_master)
        
        # Deteksi nama kolom harga satuan secara fleksibel
        possible_unit_cols = ["clean_price", "unit_price", "price", "harga_satuan", "unit_cost"]
        unit_col = next((col for col in possible_unit_cols if col in df_clean_master.columns), None)
        
        if unit_col and "qty" in df_clean_master.columns:
            total_revenue = (df_clean_master["qty"] * df_clean_master[unit_col]).sum()
        else:
            total_revenue = 0

        sample_master = df_clean_master.head(3)

        st.session_state["diag_run_stage_06"] = True
        st.session_state["diag_metrics_06"] = {
            "total_rows": total_rows,
            "null_count": null_count,
            "unique_orders": unique_orders,
            "total_revenue": total_revenue,
            "sample_master": sample_master,
        }

if st.session_state.get("diag_run_stage_06", False):
    metrics = st.session_state["diag_metrics_06"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Baris Master", f"{metrics['total_rows']:,}")
    c2.metric("Total Missing Values", f"{metrics['null_count']:,}")
    c3.metric("Order ID Unik", f"{metrics['unique_orders']:,}")
    c4.metric("Estimasi Revenue", f"Rp {metrics['total_revenue']:,.0f}")
    
    if not metrics["sample_master"].empty:
        st.markdown("**Sampel Master Dataset Bersih:**")
        desired_sample_cols = ['order_id', 'channel', 'sku_id', 'qty', 'discount_rate']
        available_sample_cols = [c for c in desired_sample_cols if c in metrics["sample_master"].columns]
        st.dataframe(metrics["sample_master"][available_sample_cols], hide_index=True)
    
    st.success("Audit mutu data selesai. Gunakan pemahaman Anda untuk menyelesaikan latihan praktik di bawah.")

st.divider()

# -----------------------------------------------------------------------------
# Bagian 2: Evaluasi Pemahaman Format Penyimpanan Data
# -----------------------------------------------------------------------------
st.subheader("2. Evaluasi Pemahaman Format Penyimpanan Data")
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
        0: "Penjelasan: Format Apache Parquet menyimpan metadata skema secara native dan menggunakan kompresi berbasis kolom, sehingga sangat optimal untuk analitik skala besar.",
        1: "Penjelasan: Parquet adalah format biner berorientasi kolom (*columnar storage*), bukan berorientasi baris murni seperti CSV.",
        2: "Penjelasan: Parquet merupakan format biner terkompresi, sehingga tidak dapat dibaca atau diedit secara langsung menggunakan teks editor seperti Notepad.",
        3: "Penjelasan: Pembacaan file Parquet tetap memerlukan library atau engine khusus seperti pyarrow atau fastparquet di Pandas."
    }

    st.info(explanations.get(selected_index, "Penjelasan tidak tersedia."))

st.divider()

# -----------------------------------------------------------------------------
# Bagian 3: Pemetaan Dimensi Mutu Data
# -----------------------------------------------------------------------------
st.subheader("3. Pemetaan Dimensi Mutu Data")
match_data = task_cfg["matching"]
render_column_matching(
    task_id=match_data["task_id"],
    title=match_data["title"],
    source_columns=match_data["sources"],
    target_options=match_data["targets"],
    correct_mapping=match_data["correct_mapping"],
    points=match_data["points"],
)

st.divider()

# -----------------------------------------------------------------------------
# Bagian 4: Sintaks Metode Ekspor File Parquet Pandas
# -----------------------------------------------------------------------------
st.subheader("4. Sintaks Metode Ekspor File Parquet Pandas")
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
# Bagian 5: Implementasi Skrip Agregasi Pendapatan Omnichannel
# -----------------------------------------------------------------------------
st.subheader("5. Implementasi Skrip Agregasi Pendapatan Omnichannel")
script_data = task_cfg["script_task"]
st.markdown(f"**Instruksi:** {script_data['instruction']}")

render_hints(script_data["task_id"], script_data["hints"])

user_script = st.text_area(
    "Editor Kode Python:",
    value=script_data["starter_code"],
    height=220,
    key=f"editor_{script_data['task_id']}",
)

if st.button("Jalankan Skrip & Validasi Agregasi", type="primary"):
    if "___" in user_script:
        st.warning("Harap lengkapi semua bagian '___' sebelum mengeksekusi kode.")
    else:
        with st.spinner("Menghitung agregasi finansial master dataset..."):
            context = {"df_master": df_clean_master.copy()}
            success, result_env, logs = run_user_code_with_timeout(
                user_script, context, timeout_seconds=5
            )

            if not success:
                st.error(f"Eksekusi Gagal:\n{logs}")
            else:
                errors = []
                if "channel_summary" not in result_env:
                    errors.append("Variabel `channel_summary` tidak ditemukan.")
                else:
                    summary = result_env["channel_summary"]
                    if not isinstance(summary, (pd.Series, pd.DataFrame)):
                        errors.append("`channel_summary` harus berupa Pandas Series atau DataFrame hasil groupby.")

                if errors:
                    for err in errors:
                        st.error(f"Audit Gagal: {err}")
                else:
                    st.success("Validasi Berhasil! Agregasi pendapatan kotor omnichannel terverifikasi valid.")
                    record_task_score(
                        script_data["task_id"],
                        script_data["points"],
                        max_points=script_data["points"],
                    )

                    if logs.strip():
                        st.text_area("Output Eksekusi (stdout):", logs, height=120)

st.divider()

# -----------------------------------------------------------------------------
# Bagian 6: Unduh Master Dataset Bersih (Multi-Format)
# -----------------------------------------------------------------------------
st.subheader("6. Unduh Master Dataset Bersih")

col_dl_parquet, col_dl_csv = st.columns(2)

parquet_buffer = io.BytesIO()
df_clean_master.to_parquet(parquet_buffer, index=False, engine="pyarrow")
parquet_bytes = parquet_buffer.getvalue()

with col_dl_parquet:
    st.download_button(
        label="Unduh Format Parquet (.parquet)",
        data=parquet_bytes,
        file_name="clean_omnichannel_master.parquet",
        mime="application/octet-stream",
        type="primary",
        use_container_width=True,
    )

csv_bytes = df_clean_master.to_csv(index=False).encode("utf-8")
with col_dl_csv:
    st.download_button(
        label="Unduh Format CSV (.csv)",
        data=csv_bytes,
        file_name="clean_omnichannel_master.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.divider()

# -----------------------------------------------------------------------------
# Bagian 7: Rapor Akhir & Evaluasi Kinerja Pemain
# -----------------------------------------------------------------------------
st.subheader("7. Rapor Kinerja & Kelulusan Sesi Latihan")

player_name = st.session_state.get("player_name", "Guest Trainee")
player_role = st.session_state.get("player_role", "Junior Data Analyst")
total_score = st.session_state.get("total_score", 0)
scores_dict = st.session_state.get("quiz_scores", {})

MAX_POSSIBLE_SCORE = 600
score_percentage = (total_score / MAX_POSSIBLE_SCORE) * 100

st.markdown(
    f"""
    <div style="padding: 20px; border: 2px solid #2563EB; border-radius: 8px; background-color: #F8FAFC;">
        <h4 style="margin-top: 0; color: #1E3A8A;">KARTU HASIL PELATIHAN DATA CLEANING</h4>
        <p><strong>Nama Pemain:</strong> {player_name}</p>
        <p><strong>Peran / Posisi:</strong> {player_role}</p>
        <p><strong>Total Skor Akhir:</strong> <span style="font-size: 18px; font-weight: bold; color: #0D9488;">{total_score} / {MAX_POSSIBLE_SCORE} ({score_percentage:.1f}%)</span></p>
        <hr style="border: 1px solid #CBD5E1; margin: 12px 0;">
        <p><strong>Status Kelulusan:</strong> <span style="font-weight: bold; color: {'#16A34A' if score_percentage >= 70 else '#D97706'};">{'LULUS DENGAN PREDIKAT KOMPETEN' if score_percentage >= 70 else 'PERLU LATIHAN TAMBAHAN'}</span></p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### Rincian Poin per Modul:")
score_rows = []
modules_map = {
    "m1": "Modul 01: Import and Extract",
    "m2": "Modul 02: Missing and Duplicates",
    "m3": "Modul 03: Standardization and Regex",
    "m4": "Modul 04: Omnichannel Merge",
    "m5": "Modul 05: Business Rules and Outliers",
    "m6": "Modul 06: Validation and Export",
}

for mod_prefix, mod_name in modules_map.items():
    mod_score = sum(val for key, val in scores_dict.items() if key.startswith(mod_prefix))
    score_rows.append({"Modul Latihan": mod_name, "Poin Diperoleh": f"{mod_score} / 100 Pts"})

st.table(pd.DataFrame(score_rows))
