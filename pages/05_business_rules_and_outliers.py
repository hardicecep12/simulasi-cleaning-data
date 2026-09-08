# pages/05_business_rules_and_outliers.py
import sys
from pathlib import Path

# 1. Path Resolver
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import numpy as np
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

task_cfg = TASKS_DATA["modul_05"]
render_stage_header("05", task_cfg["title"], task_cfg["description"])

# Ambil master data hasil stage 04 dengan pemulihan otomatis
df_master = get_latest_dataframe("omnichannel_master")

if df_master is None:
    df_online = get_latest_dataframe("online_orders")
    df_pos = get_latest_dataframe("offline_pos_orders")
    df_products = get_latest_dataframe("products_catalog")

    if df_online is not None and df_pos is not None and df_products is not None:
        with st.spinner("Memulihkan dan menyelaraskan data omnichannel secara otomatis..."):
            df_online_prep = df_online.rename(columns={'customer_id': 'customer_ref', 'warehouse_code': 'location_ref'}).copy()
            df_online_prep['channel'] = 'ONLINE'
            
            df_pos_prep = df_pos.rename(columns={'pos_invoice_no': 'order_id', 'pos_sku_code': 'sku_id', 'pos_cust_contact': 'customer_ref', 'store_branch': 'location_ref', 'quantity_sold': 'qty'}).copy()
            df_pos_prep['channel'] = 'OFFLINE'
            if 'discount_rate' not in df_pos_prep.columns:
                df_pos_prep['discount_rate'] = 0.0

            cols = ['order_id', 'channel', 'customer_ref', 'sku_id', 'qty', 'discount_rate', 'location_ref']
            df_omnichannel = pd.concat(
                [df_online_prep[[c for c in cols if c in df_online_prep.columns]],
                 df_pos_prep[[c for c in cols if c in df_pos_prep.columns]]],
                ignore_index=True
            )
            price_col = 'clean_price' if 'clean_price' in df_products.columns else 'cost_price'
            df_master = df_omnichannel.merge(
                df_products[['product_id', 'product_name', 'category', price_col]],
                left_on='sku_id',
                right_on='product_id',
                how='left'
            )
            save_cleaned_checkpoint("stage_04", {"omnichannel_master": df_master})
    else:
        st.warning("Dataset omnichannel belum tersedia. Selesaikan modul sebelumnya terlebih dahulu.")
        st.stop()

# -----------------------------------------------------------------------------
# Bagian 1: Diagnostik Anomali Transaksi & Run Mode
# -----------------------------------------------------------------------------
st.subheader("1. Diagnostik Anomali Transaksi")
st.markdown(
    "**Mengapa Aturan Bisnis & Deteksi Outlier Penting?** Data transaksi ritel sering kali mengandung nilai yang melanggar "
    "logika operasional nyata (misalnya kuantitas penjualan bernilai negatif/nol atau diskon promosi yang melebihi 100%). "
    "Selain itu, pembelian borongan (*bulk buyers* atau *scalpers*) yang ekstrem dapat mendistorsi analisis statistik jika tidak ditandai menggunakan metode rentang antar-kuartil (IQR)."
)
st.markdown(
    "Jalankan tombol di bawah ini untuk memindai baris transaksi dengan kuantitas tidak valid, "
    "diskon berlebih, serta melihat sampel data anomali secara langsung dari memori sistem."
)

if st.button("Jalankan Diagnostik Anomali & Run Mode", type="primary"):
    with st.spinner("Memindai anomali kuantitas dan diskon..."):
        invalid_qty_count = (df_master["qty"] <= 0).sum()
        invalid_disc_count = (df_master["discount_rate"] > 1.0).sum()

        q1 = df_master["qty"].quantile(0.25)
        q3 = df_master["qty"].quantile(0.75)
        iqr = q3 - q1
        upper_fence = q3 + (1.5 * iqr)
        outliers_qty = (df_master["qty"] > upper_fence).sum()

        sample_invalid_qty = df_master[df_master["qty"] <= 0].head(2)
        sample_invalid_disc = df_master[df_master["discount_rate"] > 1.0].head(2)

        st.session_state["diag_run_stage_05"] = True
        st.session_state["diag_metrics_05"] = {
            "invalid_qty": invalid_qty_count,
            "invalid_disc": invalid_disc_count,
            "upper_fence": upper_fence,
            "outliers_qty": outliers_qty,
            "sample_qty": sample_invalid_qty,
            "sample_disc": sample_invalid_disc,
        }

if st.session_state.get("diag_run_stage_05", False):
    metrics = st.session_state["diag_metrics_05"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Kuantitas Anomali (<= 0)", f"{metrics['invalid_qty']:,} Baris")
    c2.metric("Diskon Anomali (> 100%)", f"{metrics['invalid_disc']:,} Baris")
    c3.metric(f"Outlier Borongan (Qty > {metrics['upper_fence']:.0f})", f"{metrics['outliers_qty']:,} Baris")
    
    if not metrics["sample_qty"].empty:
        st.markdown("**Sampel Transaksi Kuantitas Tidak Valid (<= 0):**")
        st.dataframe(metrics["sample_qty"][['order_id', 'channel', 'sku_id', 'qty', 'discount_rate']], hide_index=True)
    
    if not metrics["sample_disc"].empty:
        st.markdown("**Sampel Transaksi Diskon Berlebih (> 100%):**")
        st.dataframe(metrics["sample_disc"][['order_id', 'channel', 'sku_id', 'qty', 'discount_rate']], hide_index=True)

    st.success("Diagnostik aturan bisnis selesai. Gunakan pemahaman Anda untuk menyelesaikan latihan praktik di bawah.")

st.divider()

# -----------------------------------------------------------------------------
# Bagian 2: Evaluasi Konsep Deteksi Outlier (IQR)
# -----------------------------------------------------------------------------
st.subheader("2. Evaluasi Konsep Deteksi Outlier (IQR)")
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
        0: "Penjelasan: `Q3 + 1.5 * IQR` adalah rumus batas atas (Upper Fence) yang benar dalam metode statistik IQR untuk mendeteksi pencilan (outlier) tinggi di sisi kanan distribusi data.",
        1: "Penjelasan: `Q1 - 1.5 * IQR` keliru karena rumus tersebut digunakan untuk menghitung batas bawah (Lower Fence) deteksi outlier di sisi kiri distribusi data.",
        2: "Penjelasan: `Mean + 3 * StdDev` keliru karena menggunakan pendekatan standar deviasi berbasis distribusi normal, bukan metode non-parametrik kuartil IQR.",
        3: "Penjelasan: `Median + 2 * IQR` keliru dan tidak sesuai dengan standar formula baku metode Tukey untuk rentang antar-kuartil."
    }

    st.info(explanations.get(selected_index, "Penjelasan tidak tersedia."))

st.divider()

# -----------------------------------------------------------------------------
# Bagian 3: Perlakuan Penanganan Anomali Bisnis
# -----------------------------------------------------------------------------
st.subheader("3. Perlakuan Penanganan Anomali Bisnis")
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
# Bagian 4: Operator Filtering Pandas untuk Kuantitas Valid
# -----------------------------------------------------------------------------
st.subheader("4. Operator Filtering Pandas untuk Kuantitas Valid")
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
# Bagian 5: Implementasi Skrip Filtering Aturan Bisnis & Capping Diskon
# -----------------------------------------------------------------------------
st.subheader("5. Implementasi Skrip Filtering Aturan Bisnis & Capping Diskon")
script_data = task_cfg["script_task"]
st.markdown(f"**Instruksi:** {script_data['instruction']}")

render_hints(script_data["task_id"], script_data["hints"])

user_script = st.text_area(
    "Editor Kode Python:",
    value=script_data["starter_code"],
    height=260,
    key=f"editor_{script_data['task_id']}",
)

if st.button("Jalankan Skrip & Validasi Aturan Bisnis", type="primary"):
    if "___" in user_script:
        st.warning("Harap lengkapi semua bagian '___' sebelum mengeksekusi kode.")
    else:
        with st.spinner("Mengaudit aturan bisnis dan memvalidasi batas nilai..."):
            context = {"df_omnichannel": df_master.copy()}
            success, result_env, logs = run_user_code_with_timeout(
                user_script, context, timeout_seconds=5
            )

            if not success:
                st.error(f"Eksekusi Gagal:\n{logs}")
            else:
                errors = []
                if "df_clean" not in result_env:
                    errors.append("Variabel `df_clean` tidak ditemukan.")
                else:
                    df_res = result_env["df_clean"]
                    if (df_res["qty"] <= 0).any():
                        errors.append("Masih terdapat nilai kuantitas <= 0.")
                    if (df_res["discount_rate"] > 1.0).any():
                        errors.append("Masih terdapat diskon melebihi 1.0 (100%).")
                    if "is_bulk_buyer" not in df_res.columns:
                        errors.append("Kolom flag `is_bulk_buyer` tidak ditemukan.")

                if errors:
                    for err in errors:
                        st.error(f"Audit Gagal: {err}")
                else:
                    st.success("Validasi Berhasil! Seluruh anomali aturan bisnis berhasil disaring dan diskon telah dibatasi.")
                    save_cleaned_checkpoint(
                        "stage_05",
                        {"clean_master": result_env["df_clean"]},
                    )
                    record_task_score(
                        script_data["task_id"],
                        script_data["points"],
                        max_points=script_data["points"],
                    )

                    df_res = result_env["df_clean"]
                    m1, m2, m3 = st.columns(3)
                    m1.metric(
                        "Total Transaksi Bersih",
                        f"{len(df_res):,} Baris",
                        delta=f"-{len(df_master) - len(df_res)} Baris Anomali Dibuang",
                    )
                    m2.metric("Maksimum Diskon", f"{df_res['discount_rate'].max() * 100:.0f}%")
                    m3.metric("Transaksi Bulk Flagged", f"{(df_res['is_bulk_buyer']).sum():,} Orders")

# -----------------------------------------------------------------------------
# Navigasi Tahap Berdasarkan Status Penyelesaian Task
# -----------------------------------------------------------------------------
stage_05_tasks = [
    task_cfg["mcq"]["task_id"],
    task_cfg["matching"]["task_id"],
    task_cfg["fill_one_word"]["task_id"],
    script_data["task_id"],
]

render_stage_navigation(
    current_tasks=stage_05_tasks,
    next_page_path="pages/06_validation_and_export.py",
    next_label="Lanjut ke Sesi Berikutnya: Validation and Export",
)
