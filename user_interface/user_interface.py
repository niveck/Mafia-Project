import streamlit as st
from streamlit.components.v1 import html
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import time
from threading import Thread
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

FAKE_INFINITE_TIME = 10000000000
PAGES_DURATION = {INSTRUCTIONS: 5,
                  NIGHTTIME: 5,  # todo return to 90
                  DAYTIME: 5,  # todo change into real
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
# TODO maybe remove these:

# Game data files:
PARENT_DIR = "/cs/snapless/gabis/nive/Mafia-Project/"
PARTICIPANTS_RECORD = PARENT_DIR + "user_interface/participants_record.txt"
OUTPUT_PATH = PARENT_DIR + "user_interface/game_output.csv"
OUTPUT_FILE_HEADER = "time,name,type,message"


def seconds_as_minutes(seconds):
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes:02d}:{remaining_seconds:02d}"


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
    return len(st.session_state["players"]) == len(PLAYERS)


def waiting_for_other_users_to_enter_page():
    st.title(f"**Welcome {st.session_state['name']}!**")
    st.info("Waiting for other players to enter...")
    st_autorefresh(interval=ONE_SECOND, key="waiting_for_players")
    if all_players_entered():
        # move_to_page(INSTRUCTIONS)  # todo return
        move_to_page(NIGHTTIME)


# def timer_and_move_to_page(seconds, page):
    # for _ in range(seconds):
    #     time.sleep(1)  # todo can it just be time.sleep(seconds?)
    # move_to_page(page)
    # st_autorefresh(interval=ONE_SECOND, key=f"timer_move_to_{page}")
async def wait_timer_and_move_to_next_page(current_page):
    await asyncio.sleep(PAGES_DURATION[current_page])
    move_to_page(NEXT_PAGES[current_page])
    st_autorefresh(interval=ONE_SECOND, key=f"timer_move_from_{current_page}")


# async def wait_timer_and_move_to_next_page(page):
#     if page in PAGES_DURATION:
#         st_autorefresh(interval=ONE_SECOND, key="before_sleep")
#         await asyncio.sleep(PAGES_DURATION[page])
#         st_autorefresh(interval=ONE_SECOND, key="after_sleep")
#         move_to_page(NEXT_PAGES[page])


def instructions_page():
    st.title(f"**Welcome all players:**")
    for player_index, player_name in enumerate(st.session_state["players"]):
        st.text(player_name)
        if player_name.strip() == st.session_state["name"]:
            st.session_state["role"] = PLAYERS[player_index]
    st.info(f"Your role is {st.session_state['role']}")
    st.header("Game instructions:")
    st.text("- Write in English\n- Don't reveal your role")
    # timer_and_move_to_page(INSTRUCTION_READING_TIME, NIGHTTIME)
    asyncio.run(wait_timer_and_move_to_next_page(INSTRUCTIONS))


def nighttime_page():
    st.session_state["role"] = "Bystander"  # todo remove
    st.title("Nighttime")
    st.info(f"Your role is {st.session_state['role']}")
    # start_time = datetime.now()
    my_html = f"""
    <script>
    function startTimer(duration, display) {'{'}
        var timer = duration, minutes, seconds;
        setInterval(function () {'{'}
            minutes = parseInt(timer / 60, 10)
            seconds = parseInt(timer % 60, 10);

            minutes = minutes < 10 ? "0" + minutes : minutes;
            seconds = seconds < 10 ? "0" + seconds : seconds;

            display.textContent = minutes + ":" + seconds;

            if (--timer < 0) {'{'}
                timer = duration;
            {'}'}
        {'}'}, 1000);
    {'}'}

    window.onload = function () {'{'}
        var turnSeconds = {PAGES_DURATION[NIGHTTIME]},
            display = document.querySelector('#time');
        startTimer(turnSeconds, display);
    {'}'};
    </script>

    <body>
      <div>Registration closes in <span id="time">
        {seconds_as_minutes(PAGES_DURATION[NIGHTTIME])}</span> minutes!</div>
    </body>
    """
    html(my_html)
    # timer_and_move_to_page(NIGHTTIME_DURATION, DAYTIME)
    # asyncio.run(wait_timer_and_move_to_next_page(NIGHTTIME))
    thread = Thread(target=asyncio.run, args=(wait_timer_and_move_to_next_page(NIGHTTIME),))
    thread.start()
    thread.join(PAGES_DURATION[NIGHTTIME] + 5)
    if not thread.is_alive():
        st.text("**thread not alive!**")
        move_to_page(NEXT_PAGES[NIGHTTIME])
    else:
        st.text("**thread still alive...**")
    # todo continue


def daytime_page():
    st.title("**You've reached Daytime!**")
    # asyncio.run(wait_timer_and_move_to_next_page(DAYTIME))
    thread = Thread(target=asyncio.run, args=(wait_timer_and_move_to_next_page(DAYTIME),))
    thread.start()
    thread.join(PAGES_DURATION[DAYTIME] + 5)
    if not thread.is_alive():
        move_to_page(NEXT_PAGES[DAYTIME])
    # todo continue
    # pass


def game_ended_page():
    # todo continue
    pass


def main():
    if "page" not in st.session_state:
        st.session_state["page"] = NEW_PLAYER_ENTRY
    page = st.session_state["page"]
    # Thread(target=asyncio.run, args=(wait_timer_and_move_to_next_page(page),)).start()  # TODO remove the "threading."
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
