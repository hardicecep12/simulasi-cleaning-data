# modules/state_manager.py
import streamlit as st

def init_session_state():
    defaults = {
        "player_name": "",
        "player_role": "Junior Data Analyst",
        "total_score": 0,
        "completed_tasks": set(),
        "total_tasks_count": 6,
        "quiz_scores": {},
        "raw_dfs": {},
        "cleaned_dfs": {},
        "hint_usage_log": {},
        "user_inputs": {},  # Penyimpanan persisten untuk teks editor, pilihan kuis, dan state latihan
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

def save_user_input(key: str, value):
    if "user_inputs" not in st.session_state:
        st.session_state["user_inputs"] = {}
    st.session_state["user_inputs"][key] = value

def get_user_input(key: str, default=None):
    if "user_inputs" in st.session_state and key in st.session_state["user_inputs"]:
        return st.session_state["user_inputs"][key]
    return default

def record_hint_usage(task_id: str, hint_level: int):
    if "hint_usage_log" not in st.session_state:
        st.session_state["hint_usage_log"] = {}
    if task_id not in st.session_state["hint_usage_log"]:
        st.session_state["hint_usage_log"][task_id] = []
    if hint_level not in st.session_state["hint_usage_log"][task_id]:
        st.session_state["hint_usage_log"][task_id].append(hint_level)

def record_task_score(task_id: str, points: int, max_points: int):
    if task_id not in st.session_state["quiz_scores"]:
        st.session_state["quiz_scores"][task_id] = min(points, max_points)
        st.session_state["total_score"] += st.session_state["quiz_scores"][task_id]
        st.session_state["completed_tasks"].add(task_id)

def save_cleaned_checkpoint(stage_name: str, df_dict: dict):
    if "cleaned_dfs" not in st.session_state:
        st.session_state["cleaned_dfs"] = {}
    st.session_state["cleaned_dfs"][stage_name] = {k: v.copy() for k, v in df_dict.items()}

def get_latest_dataframe(table_name: str):
    if "cleaned_dfs" in st.session_state:
        for stage in reversed(list(st.session_state["cleaned_dfs"].keys())):
            if table_name in st.session_state["cleaned_dfs"][stage]:
                return st.session_state["cleaned_dfs"][stage][table_name]
    if "raw_dfs" in st.session_state and table_name in st.session_state["raw_dfs"]:
        return st.session_state["raw_dfs"][table_name]
    return None

def reset_all_session_data(keep_player: bool = True):
    saved_name = st.session_state.get("player_name", "") if keep_player else ""
    saved_role = st.session_state.get("player_role", "Junior Data Analyst") if keep_player else "Junior Data Analyst"
    st.session_state["raw_dfs"] = {}
    st.session_state["cleaned_dfs"] = {}
    st.session_state["completed_tasks"] = set()
    st.session_state["quiz_scores"] = {}
    st.session_state["total_score"] = 0
    st.session_state["hint_usage_log"] = {}
    st.session_state["user_inputs"] = {}
    st.session_state["player_name"] = saved_name
    st.session_state["player_role"] = saved_role

def set_player_profile(name: str, role: str):
    st.session_state["player_name"] = name.strip()
    st.session_state["player_role"] = role
