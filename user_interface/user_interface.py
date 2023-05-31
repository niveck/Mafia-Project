import streamlit as st
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import time

# Pages IDs:
NEW_PLAYER_ENTRY = 0
WAITING_FOR_OTHER_USERS_TO_ENTER = 0.5
INSTRUCTIONS = 1
NIGHTTIME = 2
# NIGHTTIME_RELOAD = 2.1  # todo maybe unnecessary because of timer
DAYTIME = 3
# DAYTIME_RELOAD = 3.1
GAME_ENDED = 4

# Game hyperparameters:
NUM_PLAYERS = 2
NUM_MAFIA = 1

# Game data files:
PARTICIPANTS_RECORD = "./participants_record.txt"


def new_player_entry_page():
    st.title("Welcome to the game of Mafia!")
    st.text_input("Enter fake first name:", key="first_name")
    st.text_input("Enter fake last name:", key="last_name")

    def save_names_and_wait_for_others():
        name = st.session_state["first_name"] + " " + st.session_state["last_name"]
        st.session_state["name"] = name
        with open(PARTICIPANTS_RECORD, "a") as f:
            f.write(name + "\n")
        move_to_page(WAITING_FOR_OTHER_USERS_TO_ENTER)

    st.button("Send and wait for other players", key="send_names",
              on_click=save_names_and_wait_for_others)


def move_to_page(page):
    st.session_state["page"] = page


def check_if_all_players_entered():
    if "players" not in st.session_state:
        st.session_state["players"] = []
    with open(PARTICIPANTS_RECORD, "r") as f:
        st.session_state["players"] = f.readlines()
    if len(st.session_state["players"]) == NUM_PLAYERS:
        move_to_page(INSTRUCTIONS)


def waiting_for_other_users_to_enter_page():
    st.title(f"**Welcome {st.session_state['name']}!**")
    st.info("Waiting for other players to enter...")
    while True:
        check_if_all_players_entered()
        time.sleep(1)


def nighttime_page():
    pass


def daytime_page():
    pass


def game_ended_page():
    pass


def instructions_page():
    pass


def main():
    if "page" not in st.session_state:
        st.session_state["page"] = NEW_PLAYER_ENTRY
    page = st.session_state["page"]
    if page == NEW_PLAYER_ENTRY:
        new_player_entry_page()
    elif page == WAITING_FOR_OTHER_USERS_TO_ENTER:
        waiting_for_other_users_to_enter_page()
    elif page == INSTRUCTIONS:
        instructions_page()
    elif page == NIGHTTIME:
        nighttime_page()
    elif page == DAYTIME:
        daytime_page()
    elif page == GAME_ENDED:
        game_ended_page()


if __name__ == "__main__":
    main()
