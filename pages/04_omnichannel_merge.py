# pages/04_omnichannel_merge.py
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

task_cfg = TASKS_DATA["modul_04"]
render_stage_header("04", task_cfg["title"], task_cfg["description"])

# Ambil data dari stage sebelumnya
df_online = get_latest_dataframe("online_orders")
df_pos = get_latest_dataframe("offline_pos_orders")
df_products = get_latest_dataframe("products_catalog")

if df_online is None or df_pos is None or df_products is None:
    st.warning("Dataset belum tersedia. Jalankan modul 01, 02, dan 03 terlebih dahulu.")
    st.stop()

# -----------------------------------------------------------------------------
# Bagian 1: Komparasi Skema Kolom Transaksi & Preview
# -----------------------------------------------------------------------------
st.subheader("1. Komparasi Skema Kolom Transaksi & Preview")
st.markdown(
    "Operasi ritel modern menggabungkan transaksi online e-commerce "
    "dan titik penjualan kasir fisik (POS) yang memiliki struktur kolom berbeda. Sebelum dianalisis secara terpusat, "
    "nama kolom harus diselaraskan, digabungkan secara vertikal, dan diperkaya dengan data master produk melalui relasi *join*."
)
st.markdown(
    "Jalankan tombol di bawah ini untuk memeriksa perbedaan skema kolom mentah antara transaksi online dan POS dari memori sistem."
)

st.code(
    """# Kode Inspeksi Skema
online_cols = list(df_online.columns)
pos_cols = list(df_pos.columns)
""",
    language="python",
)

if st.button("Jalankan Inspeksi Skema Kolom", type="primary"):
    with st.spinner("Memindai struktur kolom tabel..."):
        online_cols = list(df_online.columns)
        pos_cols = list(df_pos.columns)

        st.session_state["diag_run_stage_04"] = True
        st.session_state["diag_schemas_04"] = {
            "online": online_cols,
            "pos": pos_cols,
        }

if st.session_state.get("diag_run_stage_04", False):
    schemas = st.session_state["diag_schemas_04"]
    col_schema1, col_schema2 = st.columns(2)
    with col_schema1:
        st.markdown("**Skema Kolom Transaksi Online (`online_orders`):**")
        for c in schemas["online"]:
            st.code(c, language="text")
    with col_schema2:
        st.markdown("**Skema Kolom Transaksi POS (`offline_pos_orders`):**")
        for c in schemas["pos"]:
            st.code(c, language="text")
    
    st.success("Inspeksi skema selesai. Gunakan referensi kode penyelarasan di bawah untuk menggabungkannya.")

st.markdown("**Kode Referensi Lengkap Penyelarasan & Relational Join:**")
st.code(
    """# 1. Standardisasi kolom Online & penambahan label channel
df_online_prep = df_online.rename(columns={
    'customer_id': 'customer_ref',
    'warehouse_code': 'location_ref'
}).copy()
df_online_prep['channel'] = 'ONLINE'

# 2. Standardisasi kolom POS & penambahan label channel
df_pos_prep = df_pos.rename(columns={
    'pos_invoice_no': 'order_id',
    'pos_sku_code': 'sku_id',
    'pos_cust_contact': 'customer_ref',
    'store_branch': 'location_ref',
    'quantity_sold': 'qty'
}).copy()
df_pos_prep['channel'] = 'OFFLINE'
if 'discount_rate' not in df_pos_prep.columns:
    df_pos_prep['discount_rate'] = 0.0

cols = ['order_id', 'channel', 'customer_ref', 'sku_id', 'qty', 'discount_rate', 'location_ref']

# 3. Penggabungan vertikal (Union)
df_omnichannel = pd.concat(
    [df_online_prep[[c for c in cols if c in df_online_prep.columns]],
     df_pos_prep[[c for c in cols if c in df_pos_prep.columns]]],
    ignore_index=True
)

# 4. Left Join dengan katalog SKU
df_master_enriched = df_omnichannel.merge(
    df_products[['product_id', 'product_name', 'category', 'clean_price' if 'clean_price' in df_products.columns else 'cost_price']],
    left_on='sku_id',
    right_on='product_id',
    how='left'
)
""",
    language="python",
)

st.divider()

# -----------------------------------------------------------------------------
# Bagian 2: Evaluasi Konsep Relational Join dalam Omnichannel
# -----------------------------------------------------------------------------
st.subheader("2. Evaluasi Konsep Relational Join dalam Omnichannel")
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
        0: "Penjelasan: INNER JOIN keliru karena hanya mempertahankan baris dengan kecocokan kode di kedua tabel, sehingga transaksi yang SKU-nya belum terdaftar di katalog akan terhapus.",
        1: "Penjelasan: LEFT JOIN adalah jawaban yang tepat. Jenis join ini memastikan seluruh baris transaksi dari tabel utama tetap utuh meskipun kode SKU belum tercatat di dalam tabel katalog master.",
        2: "Penjelasan: RIGHT JOIN keliru karena memprioritaskan tabel kanan (katalog), yang berisiko menghilangkan catatan transaksi penjualan riil.",
        3: "Penjelasan: CROSS JOIN keliru karena menghasilkan perkalian silang seluruh kombinasi baris, yang membuat ukuran data meledak secara masif dan tidak valid untuk pencatatan transaksi."
    }

    st.info(explanations.get(selected_index, "Penjelasan tidak tersedia."))

st.divider()

# -----------------------------------------------------------------------------
# Bagian 3: Pemetaan Kolom POS ke Standar Skema Online
# -----------------------------------------------------------------------------
st.subheader("3. Pemetaan Kolom POS ke Standar Skema Online")
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
# Bagian 4: Penggabungan Baris Vertikal (Union) menggunakan Pandas
# -----------------------------------------------------------------------------
st.subheader("4. Penggabungan Baris Vertikal (Union) menggunakan Pandas")
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
# Bagian 5: Implementasi Skrip Penyatuan dan Pengayaan Katalog
# -----------------------------------------------------------------------------
st.subheader("5. Implementasi Skrip Penyatuan dan Pengayaan Katalog")
script_data = task_cfg["script_task"]
st.markdown(f"**Instruksi:** {script_data['instruction']}")

render_hints(script_data["task_id"], script_data["hints"])

user_script = st.text_area(
    "Editor Kode Python:",
    value=script_data["starter_code"],
    height=320,
    key=f"editor_{script_data['task_id']}",
)

if st.button("Jalankan Skrip & Validasi Pipeline", type="primary"):
    if "___" in user_script:
        st.warning("Harap lengkapi semua bagian '___' sebelum mengeksekusi kode.")
    else:
        with st.spinner("Menggabungkan transaksi omnichannel dan memvalidasi integritas relasi..."):
            context = {
                "df_online": df_online.copy(),
                "df_pos": df_pos.copy(),
                "df_products": df_products.copy(),
            }
            success, result_env, logs = run_user_code_with_timeout(
                user_script, context, timeout_seconds=6
            )

            if not success:
                st.error(f"Eksekusi Gagal:\n{logs}")
            else:
                errors = []
                if "df_master_enriched" not in result_env:
                    errors.append("Variabel `df_master_enriched` tidak ditemukan.")
                else:
                    df_res = result_env["df_master_enriched"]
                    expected_rows = len(df_online) + len(df_pos)
                    if len(df_res) != expected_rows:
                        errors.append(f"Jumlah baris ({len(df_res):,}) tidak sesuai total ({expected_rows:,}).")

                    required_cols = ["order_id", "channel", "sku_id", "qty", "product_name"]
                    missing = [c for c in required_cols if c not in df_res.columns]
                    if missing:
                        errors.append(f"Kolom wajib hilang: {missing}")

                if errors:
                    for err in errors:
                        st.error(f"Audit Gagal: {err}")
                else:
                    st.success("Validasi Sempurna! Skema transaksi berhasil diselaraskan dan terhubung dengan katalog master.")
                    save_cleaned_checkpoint(
                        "stage_04",
                        {"omnichannel_master": result_env["df_master_enriched"]},
                    )
                    record_task_score(
                        script_data["task_id"],
                        script_data["points"],
                        max_points=script_data["points"],
                    )

                    df_res = result_env["df_master_enriched"]
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Total Transaksi Tergabung", f"{len(df_res):,} Baris")
                    m2.metric("Porsi Online", f"{(df_res['channel'] == 'ONLINE').sum():,} Orders")
                    m3.metric("Porsi Offline POS", f"{(df_res['channel'] == 'OFFLINE').sum():,} Orders")

# -----------------------------------------------------------------------------
# Navigasi Tahap Berdasarkan Status Penyelesaian Task
# -----------------------------------------------------------------------------
stage_04_tasks = [
    task_cfg["mcq"]["task_id"],
    task_cfg["matching"]["task_id"],
    task_cfg["fill_one_word"]["task_id"],
    script_data["task_id"],
]

render_stage_navigation(
    current_tasks=stage_04_tasks,
    next_page_path="pages/05_business_rules_and_outliers.py",
    next_label="Lanjut ke Sesi Berikutnya: Business Rules and Outliers",
)
