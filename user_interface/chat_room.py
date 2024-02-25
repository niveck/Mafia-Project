import streamlit as st
from streamlit_autorefresh import st_autorefresh
from datetime import datetime


HALF_SECOND = 500  # milliseconds

# Game data files:
PARENT_DIR = "/cs/snapless/gabis/nive/Mafia-Project/"
# PARENT_DIR = "C:/Users/nive/OneDrive - Mobileye/Desktop/University/Mafia-Project/"
PLAYERS_RECORD = PARENT_DIR + "user_interface/chat_room_players.txt"
OUTPUT_PATH = PARENT_DIR + "user_interface/chat_room_output.txt"
GAME_MANAGER_NAME = "GAME MANGER"
MODEL_PLAYER_DEFAULT_NAME = "Johnny"


def get_name_page():
    st.title("Welcome to the game of Mafia!")

    def save_name():
        name = st.session_state["name_input"].strip()
        with open(PLAYERS_RECORD, "a") as f:
            f.write(name + "\n")
        st.session_state["name"] = name

    st.text_input("Enter your character's name:", key="name_input", on_change=save_name)


def format_chat_line(name, text):
    now = datetime.now()
    current_time = f"{now.minute:02d}:{now.second:02d}:{now.microsecond // 10000:02d}"
    line = f"{current_time} | {name}: {text}"
    return line


def chat_page():
    st.title("The Mafia Chat Room")

    def submit_message():
        text = st.session_state["user_text_input"]
        st.session_state["user_text_input"] = ""
        if not text.strip():
            return
        name = st.session_state["name"]
        line = format_chat_line(name, text)
        with open(OUTPUT_PATH, "a") as f:
            f.write(line + "\n")

    st.text_input("Write a message", key="user_text_input", on_change=submit_message)
    st.session_state["messages"] = get_reversed_current_lines(OUTPUT_PATH)
    st.text("All messages:")
    for message in st.session_state["messages"]:
        st.text(message)
    st_autorefresh(interval=HALF_SECOND)


def get_reversed_current_lines(output_path):
    with open(output_path, "r") as f:
        lines = f.readlines()
    if len(lines) > 1 and lines[-1] == lines[-2]:
        lines.pop()
        with open(output_path, "w") as f:
            f.writelines(lines)
    return lines[::-1]


def main():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "name" not in st.session_state:
        st.session_state["name"] = ""
    if not st.session_state["name"]:
        get_name_page()
    else:
        chat_page()


if __name__ == "__main__":
    main()
