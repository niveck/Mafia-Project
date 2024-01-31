import streamlit as st
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import time
import asyncio


# Pages IDs:
NEW_PLAYER_ENTRY = 0
WAITING_FOR_OTHER_USERS_TO_ENTER = 0.5
INSTRUCTIONS = 1
NIGHTTIME = 2
# NIGHTTIME_RELOAD = 2.1  # todo maybe unnecessary because of timer
DAYTIME = 3
# DAYTIME_RELOAD = 3.1  # todo maybe unnecessary because of timer
GAME_ENDED = 4

PAGES_DURATION = {INSTRUCTIONS: 5,  # todo change into real
                  NIGHTTIME: 12,  # todo return to 90
                  DAYTIME: 12,  # todo change into real
                  }  # in seconds

NEXT_PAGES = {INSTRUCTIONS: NIGHTTIME,
              NIGHTTIME: DAYTIME,
              DAYTIME: NIGHTTIME,  # todo change into real
              }

# Game hyperparameters:
PLAYERS = ["Bystander", "Mafioso", "Bystander", "Bystander",
           "Bystander", "Mafioso", "Bystander", "Bystander"]

# Game timers:
ONE_SECOND = 1000  # 1000 milliseconds

# Game data files:
PARENT_DIR = "/cs/snapless/gabis/nive/Mafia-Project/"
PARTICIPANTS_RECORD = PARENT_DIR + "user_interface/participants_record.txt"
PLAYERS_ROLES_PATH = PARENT_DIR + "user_interface/players_roles.json"  # TODO maybe remove?
NIGHTTIME_OUTPUT_PATH = PARENT_DIR + "user_interface/nighttime_game_output.csv"
DAYTIME_OUTPUT_PATH = PARENT_DIR + "user_interface/daytime_game_output.csv"
TIMER_PATH = PARENT_DIR + "user_interface/timer.txt"
OUTPUT_FILE_HEADER = "time,name,type,message"


def seconds_as_minutes(seconds):  # TODO maybe remove?
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes:02d}:{remaining_seconds:02d}"


def new_player_entry_page():
    st.title("Welcome to the game of Mafia!")
    st.text_input("Enter fake first name:", key="first_name")
    st.text_input("Enter fake last name:", key="last_name")
    
    def save_names_and_wait_for_others():
        name = st.session_state["first_name"].strip() + " " + st.session_state["last_name"].strip()
        st.session_state["name"] = name
        with open(PARTICIPANTS_RECORD, "a") as f:
            f.write(name + "\n")
        move_to_page(WAITING_FOR_OTHER_USERS_TO_ENTER)  # TODO it doesnt handle 2 player choosing the same name
    
    st.button("Send and wait for other players", key="send_names",
              on_click=save_names_and_wait_for_others)


def move_to_page(page):
    st.session_state["page"] = page
    st.session_state["current_page_count"] = 0


def all_players_entered():
    if "players" not in st.session_state:
        st.session_state["players"] = []
    with open(PARTICIPANTS_RECORD, "r") as f:
        st.session_state["players"] = f.readlines()
    return len(st.session_state["players"]) == len(PLAYERS)


def waiting_for_other_users_to_enter_page():
    st.title(f"**Welcome {st.session_state['name']}!**")
    st.info("Waiting for other players to enter...")
    st_autorefresh(interval=ONE_SECOND, key="waiting_for_players")
    if all_players_entered():
        move_to_page(INSTRUCTIONS)


async def wait_timer_and_move_to_next_page(current_page):
    if st.session_state["current_page_count"] == 0:
        secs = int(str(time.time()).split('.')[0])
        with open(TIMER_PATH, "w") as f:
            f.write(str(secs))

    st.session_state["current_page_count"] += 1
    while True:
        await asyncio.sleep(0.1)
        old_secs = int(list(open(TIMER_PATH, "r"))[0])
        cur_secs = int(str(time.time()).split('.')[0])
        if cur_secs - old_secs > PAGES_DURATION[current_page]:
            break

    move_to_page(NEXT_PAGES[current_page])
    st_autorefresh(interval=ONE_SECOND, key=f"timer_move_from_{current_page}")


def instructions_page():
    st.title(f"**Welcome all players:**")
    initiate_players_info()
    show_public_players_roles()
    st.header("Game instructions:")
    st.text("- Write in English\n- Don't reveal your role")
    asyncio.run(wait_timer_and_move_to_next_page(INSTRUCTIONS))


def initiate_players_info():
    st.session_state["players_roles"] = {}
    st.session_state["players_eliminated"] = {}
    st.session_state["column1_players"] = []
    st.session_state["column2_players"] = []
    st.session_state["column3_players"] = []
    for player_index, name in enumerate(st.session_state["players"]):
        player_name = name.strip()
        st.session_state["players_roles"][player_name] = PLAYERS[player_index]
        st.session_state["players_eliminated"][player_name] = False
        if player_index % 3 == 0:
            st.session_state["column1_players"].append(player_name)
        elif player_index % 3 == 1:
            st.session_state["column2_players"].append(player_name)
        else:
            st.session_state["column3_players"].append(player_name)
    st.session_state["role"] = st.session_state["players_roles"][st.session_state["name"]]


def display_player_with_public_role(player_name):
    if st.session_state["players_eliminated"][player_name]:
        role = st.session_state["players_roles"][player_name]
    else:
        role = "unknown role..."
    st.text(f"{player_name} - {role}")


def show_public_players_roles():
    name = st.session_state["name"]
    role = st.session_state["role"]
    st.info(f"You are {name}, your role is *{role}*")
    st.header("All players' public roles:")
    column1, column2, column3 = st.columns(3)
    with column1:
        for player in st.session_state["column1_players"]:
            display_player_with_public_role(player)
    with column2:
        for player in st.session_state["column2_players"]:
            display_player_with_public_role(player)
    with column3:
        for player in st.session_state["column3_players"]:
            display_player_with_public_role(player)


def nighttime_page():
    st.title("Nighttime")
    show_public_players_roles()
    if st.session_state["role"] == "Mafioso":
        messaging_pane()
    else:  # role == "Bystander"
        st.info("Wait until Mafia have made their decision...")
    asyncio.run(wait_timer_and_move_to_next_page(NIGHTTIME))


def messaging_pane():
    if st.session_state["page"] == NIGHTTIME:
        output_path = NIGHTTIME_OUTPUT_PATH
        button_key = "nighttime_user_text_input"
    else:  # page == DAYTIME
        output_path = DAYTIME_OUTPUT_PATH
        button_key = "daytime_user_text_input"
     
    def submit_message():
        text = st.session_state[button_key]
        st.session_state[button_key] = ""
        if not text.strip():
            return
        name = st.session_state["name"]
        now = datetime.now()
        current_time = f"{now.minute:02d}:{now.second:02d}:{now.microsecond // 10000:02d}"
        line = f"{current_time},{name},text,{text}"
        text = ""  # prevents re-saving the same line after autorefresh
        if st.session_state["current_page_count"] == 0:
            return  # prevents rewriting the same message when page changes
        if "messages" in st.session_state and len(st.session_state["messages"]) > 0 \
                and line != st.session_state["messages"][-1]:
            with open(output_path, "a") as f:
                f.write(line + "\n")

    if st.session_state["eliminated"]:
        st.markdown("You got eliminated, therefore cannot message others")
    else:
        st.text_input("Write a message", key=button_key, on_change=submit_message)
    st.session_state["messages"] = get_reversed_current_lines(output_path)
    st.text("All messages:")
    for message in st.session_state["messages"]:
        st.text(message)


def get_reversed_current_lines(output_path):
    with open(output_path, "r") as f:
        lines = f.readlines()
    if len(lines) > 1 and lines[-1] == lines[-2]:
        lines.pop()
        with open(output_path, "w") as f:
            f.writelines(lines)
    return lines[::-1]


def daytime_page():
    st.title("Daytime")
    show_public_players_roles()
    messaging_pane()
    asyncio.run(wait_timer_and_move_to_next_page(DAYTIME))
    # todo continue


def game_ended_page():
    # todo continue
    pass


def main():
    if "page" not in st.session_state:
        st.session_state["page"] = NEW_PLAYER_ENTRY
    page = st.session_state["page"]
    if "current_page_count" not in st.session_state:
        st.session_state["current_page_count"] = 0
    if "eliminated" not in st.session_state:
        st.session_state["eliminated"] = False
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
