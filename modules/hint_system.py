# modules/hint_system.py
import streamlit as st
from modules.state_manager import record_hint_usage


def render_hints(task_id: str, hints_dict: dict[int, str]):
    """
    Merender UI bantuan bertingkat (Level 1, 2, 3).
    
    Structure hints_dict:
    {
        1: "Petunjuk konsep atau logika bisnis",
        2: "Nama fungsi, method, atau parameter yang relevan",
        3: "Contoh potongan kode Python konkret"
    }
    """
    with st.expander("Bantuan Pengerjaan (Hint Bertingkat)"):
        st.caption("Pilih level hint sesuai kebutuhan Anda:")

        tab1, tab2, tab3 = st.tabs(
            ["Level 1: Konsep", "Level 2: Sintaksis", "Level 3: Solusi Kode"]
        )

        with tab1:
            if 1 in hints_dict:
                st.info(hints_dict[1])
                record_hint_usage(task_id, 1)

        with tab2:
            if 2 in hints_dict:
                st.warning(hints_dict[2])
                record_hint_usage(task_id, 2)

        with tab3:
            if 3 in hints_dict:
                st.code(hints_dict[3], language="python")
                record_hint_usage(task_id, 3)
