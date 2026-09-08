# modules/quiz_components.py
import streamlit as st
from modules.state_manager import record_task_score


def render_multiple_choice(
    task_id: str,
    question: str,
    options: list[str],
    correct_index: int,
    points: int = 15,
    explanations: dict[int, str] = None,
):
    """Merender kuis pilihan ganda dengan opsi coba lagi jika jawaban salah."""
    if "task_submissions" not in st.session_state:
        st.session_state["task_submissions"] = {}

    if question:
        st.markdown(f"**Soal:** {question}")

    sub_state = st.session_state["task_submissions"].get(task_id, {})
    is_submitted = sub_state.get("is_submitted", False)
    is_correct = sub_state.get("is_correct", False)
    saved_choice = sub_state.get("user_choice", None)

    default_index = None
    if saved_choice in options:
        default_index = options.index(saved_choice)

    # Widget aktif jika belum submit atau jika jawaban sebelumnya salah (bisa dicoba lagi)
    is_disabled = is_submitted and is_correct

    user_choice = st.radio(
        "Pilih jawaban yang paling tepat:",
        options,
        index=default_index,
        key=f"mcq_{task_id}",
        disabled=is_disabled,
    )

    if not is_submitted or not is_correct:
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("Submit Jawaban", key=f"btn_mcq_{task_id}"):
                if user_choice is None:
                    st.warning("Pilih salah satu jawaban terlebih dahulu.")
                else:
                    selected_index = options.index(user_choice)
                    correct = (selected_index == correct_index)

                    st.session_state["task_submissions"][task_id] = {
                        "is_submitted": True,
                        "is_correct": correct,
                        "user_choice": user_choice,
                        "selected_index": selected_index,
                    }
                    if correct:
                        record_task_score(task_id, points, max_points=points)
                    st.rerun()

        if is_submitted and not is_correct:
            st.error("Jawaban belum tepat.")
            selected_idx = sub_state.get("selected_index", 0)
            if explanations and selected_idx in explanations:
                st.info(explanations[selected_idx])
            
            with col_btn2:
                if st.button("Coba Lagi", key=f"btn_retry_mcq_{task_id}"):
                    del st.session_state["task_submissions"][task_id]
                    st.rerun()
    else:
        st.success("Tepat sekali! Jawaban Anda benar.")
        selected_idx = sub_state.get("selected_index", 0)
        if explanations and selected_idx in explanations:
            st.info(explanations[selected_idx])


def render_fill_one_word(
    task_id: str,
    instruction: str,
    code_snippet: str,
    correct_keywords: list[str],
    points: int = 20,
):
    """Merender latihan isian singkat dengan opsi coba lagi jika salah."""
    if "task_submissions" not in st.session_state:
        st.session_state["task_submissions"] = {}

    st.markdown(f"**Instruksi:** {instruction}")
    st.code(code_snippet, language="python")

    sub_state = st.session_state["task_submissions"].get(task_id, {})
    is_submitted = sub_state.get("is_submitted", False)
    is_correct = sub_state.get("is_correct", False)
    default_val = sub_state.get("user_input", "")

    user_input = st.text_input(
        "Isi bagian '___' yang kosong:",
        value=default_val,
        key=f"fill_{task_id}",
        placeholder="Ketik 1 kata/parameter di sini...",
        disabled=(is_submitted and is_correct),
    ).strip()

    if not is_submitted or not is_correct:
        col_f1, col_f2 = st.columns([1, 1])
        with col_f1:
            if st.button("Periksa Kata Kunci", key=f"btn_fill_{task_id}"):
                if not user_input:
                    st.warning("Kolom isian tidak boleh kosong.")
                else:
                    correct = user_input.lower() in [k.lower() for k in correct_keywords]
                    st.session_state["task_submissions"][task_id] = {
                        "is_submitted": True,
                        "is_correct": correct,
                        "user_input": user_input,
                    }
                    if correct:
                        record_task_score(task_id, points, max_points=points)
                    st.rerun()

        if is_submitted and not is_correct:
            st.error(f"`{default_val}` belum tepat. Perhatikan kembali dokumentasi atau gunakan hint.")
            with col_f2:
                if st.button("Coba Lagi", key=f"btn_retry_fill_{task_id}"):
                    del st.session_state["task_submissions"][task_id]
                    st.rerun()
    else:
        st.success(f"Benar! Parameter/fungsi `{default_val}` tepat.")


def render_column_matching(
    task_id: str,
    title: str,
    source_columns: list[str],
    target_options: list[str],
    correct_mapping: dict[str, str],
    points: int = 25,
):
    """Merender latihan menjodohkan kolom dengan opsi coba lagi jika salah."""
    if "task_submissions" not in st.session_state:
        st.session_state["task_submissions"] = {}

    if title:
        st.markdown(f"**{title}**")

    sub_state = st.session_state["task_submissions"].get(task_id, {})
    is_submitted = sub_state.get("is_submitted", False)
    is_correct = sub_state.get("is_correct", False)
    saved_mapping = sub_state.get("user_mapping", {})

    user_mapping = {}
    col_a, col_b = st.columns([1, 1])

    for i, src_col in enumerate(source_columns):
        with col_a:
            st.text(f"Kolom Sumber: {src_col}")
        with col_b:
            default_sel = saved_mapping.get(src_col, "-- Pilih Padanan Kolom --")
            options_list = ["-- Pilih Padanan Kolom --"] + target_options
            default_idx = options_list.index(default_sel) if default_sel in options_list else 0

            selected = st.selectbox(
                f"Padanan {src_col}",
                options_list,
                index=default_idx,
                key=f"match_{task_id}_{i}",
                label_visibility="collapsed",
                disabled=(is_submitted and is_correct),
            )
            user_mapping[src_col] = selected

    if not is_submitted or not is_correct:
        col_m1, col_m2 = st.columns([1, 1])
        with col_m1:
            if st.button("Validasi Penjodohan", key=f"btn_match_{task_id}"):
                if any(v.startswith("--") for v in user_mapping.values()):
                    st.warning("Lengkapi seluruh pasangan kolom sebelum melakukan validasi.")
                else:
                    is_all_correct = all(
                        user_mapping.get(k) == v for k, v in correct_mapping.items()
                    )

                    st.session_state["task_submissions"][task_id] = {
                        "is_submitted": True,
                        "is_correct": is_all_correct,
                        "user_mapping": user_mapping,
                    }

                    if is_all_correct:
                        record_task_score(task_id, points, max_points=points)
                    st.rerun()

        if is_submitted and not is_correct:
            st.error("Beberapa pasangan kolom belum tepat. Silakan periksa kembali.")
            with col_m2:
                if st.button("Coba Lagi", key=f"btn_retry_match_{task_id}"):
                    del st.session_state["task_submissions"][task_id]
                    st.rerun()
    else:
        st.success("Semua pasangan kolom berhasil dijodohkan dengan sempurna!")
