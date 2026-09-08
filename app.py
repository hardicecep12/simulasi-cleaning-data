# app.py
import os
import streamlit as st

from modules.state_manager import (
    init_session_state,
    reset_all_session_data,
    set_player_profile,
)

# -----------------------------------------------------------------------------
# 1. Konfigurasi Halaman & Kustomisasi Visual Nyaman
# -----------------------------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "assets", "logo.svg")

st.set_page_config(
    page_title="Interactive Data Cleaning Platform",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if os.path.exists(logo_path):
    st.logo(logo_path)

st.markdown(
    """
    <style>
    :root {
        --primary-color: #38bdf8 !important;
    }
    /* Estetika logo toggle yang lebih rapi dan nyaman */
    [data-testid="stLogo"] {
        border: 1px solid rgba(148, 163, 184, 0.3) !important;
        border-radius: 10px !important;
        padding: 6px 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.2s ease-in-out;
    }
    [data-testid="stLogo"] img, 
    header img {
        max-height: 52px !important;
        width: auto !important;
        object-fit: contain !important;
    }
    /* Kotak notifikasi dan peringatan yang lebih lembut */
    div.stAlert[data-baseweb="notification"], [data-testid="stNotification"], div[data-testid="stAlert"] {
        border-radius: 8px !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
    }
    /* Aksen pilihan jawaban atau radio button */
    div[data-baseweb="radio"] div[aria-checked="true"] {
        border-color: #38bdf8 !important;
    }
    div[data-baseweb="radio"] div[aria-checked="true"] div {
        background-color: #38bdf8 !important;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Inisialisasi state sesi global
init_session_state()

# -----------------------------------------------------------------------------
# 2. Top Bar (Profil & Skor Ringkas)
# -----------------------------------------------------------------------------
player_name = st.session_state.get("player_name", "")
player_role = st.session_state.get("player_role", "Junior Data Analyst")
total_score = st.session_state.get("total_score", 0)

if player_name:
    nav_col1, nav_col2, nav_col3 = st.columns([3, 1, 1], gap="medium")
    with nav_col1:
        st.markdown(f"**{player_name}** | *{player_role}*")
    with nav_col2:
        st.markdown(f"**Skor:** `{total_score} Pts`")
    with nav_col3:
        if st.button("Reset Sesi", type="secondary", use_container_width=True):
            reset_all_session_data(keep_player=False)
            st.rerun()
    st.divider()

    total_modules = 6
    completed_tasks = st.session_state.get("completed_tasks", set())
    completed_modules_count = len(
        {task.split("_")[0] for task in completed_tasks if "_" in task}
    )
    progress_ratio = min(completed_modules_count / total_modules, 1.0)
    
    prog_col1, prog_col2 = st.columns([4, 1], gap="medium")
    with prog_col1:
        st.progress(progress_ratio)
    with prog_col2:
        st.markdown(f"Selesai: **{completed_modules_count}/{total_modules}** Modul")
    st.divider()

# -----------------------------------------------------------------------------
# 3. Tata Letak Utama (Vertikal dengan Kotak Berborder Rapi)
# -----------------------------------------------------------------------------
st.title("Interactive Data Cleaning Platform")
st.markdown(
    "Platform simulasi interaktif untuk praktik pembersihan data (*data cleaning*) "
    "secara komprehensif pada kasus ritel elektronik (integrasi transaksi toko online dan kasir POS)."
)

st.divider()

if not player_name:
    with st.container(border=True):
        st.subheader("Registrasi Sesi Pelatihan")
        st.markdown("Masukkan identitas Anda untuk memulai pencatatan progres modul dan penilaian skor:")

        with st.form("form_player_registration"):
            input_name = st.text_input(
                "Nama Lengkap / Panggilan:",
                placeholder="Contoh: Budi Santoso",
            )
            input_role = st.selectbox(
                "Tingkat Keahlian / Posisi Saat Ini:",
                [
                    "Junior Data Analyst",
                    "Data Engineer Trainee",
                    "Business Intelligence Specialist",
                    "Student / Self-Learner",
                ],
            )
            btn_submit = st.form_submit_button(
                "Mulai Sesi Latihan", type="primary", use_container_width=True
            )

            if btn_submit:
                if input_name.strip():
                    set_player_profile(input_name, input_role)
                    st.success(f"Selamat datang, {input_name}! Sesi pelatihan telah diaktifkan.")
                    st.rerun()
                else:
                    st.warning("Nama pemain wajib diisi sebelum memulai.")

    with st.container(border=True):
        st.markdown("**Standar Penilaian & Kelulusan:**")
        st.markdown(
            """
        * **6 Modul Praktik**: Masing-masing modul berbobot 100 poin (Total 600 Poin).
        * **Format Latihan**: Pilihan ganda, menjodohkan metadata, sintaks 1 kata, dan eksekusi skrip live.
        * **Ambang Batas Kompeten**: Minimal perolehan skor **70% (420 Poin)** untuk mendapatkan status Lulus.
        """
        )
else:
    st.success(
        f"Sesi Aktif: **{st.session_state['player_name']}** | Posisi: **{st.session_state['player_role']}**"
    )
    
    with st.container(border=True):
        st.subheader("Mulai Sesi Pelatihan")
        st.markdown("Anda telah terdaftar dan siap melanjutkan rangkaian modul pembersihan data.")
        
        if st.button("Mulai Sekarang", type="primary", use_container_width=True):
            st.switch_page("pages/01_import_and_extract.py")

st.divider()

with st.container(border=True):
    st.subheader("Status Runtime Dataset")
    is_loaded = "raw_dfs" in st.session_state and bool(st.session_state["raw_dfs"])

    if is_loaded:
        st.success("Dataset: Siap di Memori Runtime")
        st.markdown(f"Tabel Terbaca: `{len(st.session_state['raw_dfs'])} CSV`")
    else:
        st.warning("Dataset: Belum Diekstrak")
        st.info("Buka Modul 01 untuk mengekstrak data mentah.")

if player_name:
    st.divider()
    if st.button("Ganti Profil Pemain", use_container_width=True):
        st.session_state["player_name"] = ""
        st.rerun()
