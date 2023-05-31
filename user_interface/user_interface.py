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
# DAYTIME_RELOAD = 3.1  # todo maybe unnecessary because of timer
GAME_ENDED = 4

# Game hyperparameters:
NUM_PLAYERS = 2
NUM_MAFIA = 1

# Game timers:
ONE_SECOND = 100  # 100 milliseconds
INSTRUCTION_READING_TIME = 5

# Game data files:
PARTICIPANTS_RECORD = "./user_interface/participants_record.txt"


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


def all_players_entered():
    if "players" not in st.session_state:
        st.session_state["players"] = []
    with open(PARTICIPANTS_RECORD, "r") as f:
        st.session_state["players"] = f.readlines()
    if len(st.session_state["players"]) == NUM_PLAYERS:
        return True
    else:
        return False


def waiting_for_other_users_to_enter_page():
    st.title(f"**Welcome {st.session_state['name']}!**")
    st.info("Waiting for other players to enter...")
    st_autorefresh(interval=ONE_SECOND, key="waiting_for_players")
    if all_players_entered():
        move_to_page(INSTRUCTIONS)


def timer_and_move_to_page(seconds, page):
    for _ in range(seconds):
        time.sleep(1)
    move_to_page(NIGHTTIME)
    st_autorefresh(interval=ONE_SECOND, key=f"timer_move_to_{page}")


def instructions_page():
    st.title(f"**Welcome all players:**")
    for player_name in st.session_state["players"]:
        st.text(player_name)
    st.header("Game instructions:")
    st.text("- Write in English\n- Don't reveal your role")
    timer_and_move_to_page(INSTRUCTION_READING_TIME, NIGHTTIME)


def nighttime_page():
    st.title("Nighttime")
    # todo continue


def daytime_page():
    # todo continue
    pass


def game_ended_page():
    # todo continue
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
