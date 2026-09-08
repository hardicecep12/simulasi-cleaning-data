# modules/ui_feedback.py
import streamlit as st


def render_player_badge():
    """Merender informasi pemain dan skor di sidebar."""
    name = st.session_state.get("player_name", "Guest")
    role = st.session_state.get("player_role", "Trainee")
    score = st.session_state.get("total_score", 0)

    st.sidebar.markdown(f"**Pemain:** {name}")
    st.sidebar.caption(f"Peran: {role}")
    st.sidebar.metric(label="Total Skor Akumulasi", value=f"{score} Pts")
    st.sidebar.divider()


def render_stage_header(stage_number: str, title: str, description: str):
    """Merender header tahap latihan."""
    st.title(f"Tahap {stage_number}: {title}")
    st.markdown(description)
    st.divider()


def render_next_button(label="Lanjut ke Sesi Berikutnya", key=None):
    """Merender tombol navigasi next dengan gaya konsisten."""
    return st.button(label, type="primary", key=key, use_container_width=True)


def render_stage_navigation(current_tasks, next_page_path, next_label):
    """Mengalihkan halaman otomatis ke sesi berikutnya jika seluruh task selesai."""
    completed_tasks = st.session_state.get("completed_tasks", set())
    is_all_completed = all(task_id in completed_tasks for task_id in current_tasks)

    st.divider()
    if is_all_completed:
        redirect_key = f"redirected_{next_page_path}"
        if not st.session_state.get(redirect_key, False):
            st.session_state[redirect_key] = True
            st.success("Seluruh latihan selesai! Mengalihkan ke sesi berikutnya...")
            st.switch_page(next_page_path)
        else:
            st.success("Tahap ini telah diselesaikan.")
            if render_next_button(label=next_label, key=f"btn_{next_page_path}"):
                st.switch_page(next_page_path)
    else:
        st.info("Selesaikan semua latihan di atas untuk melanjutkan ke sesi berikutnya.")
