import streamlit as st
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import time
OUTPUT_PATH = "/cs/snapless/gabis/nive/Mafia-Project/user_interface/game_output.csv" # todo validate relative path
OUTPUT_FILE_HEADER = "time,name,type,message"



def main():

    if 'name' not in st.session_state:
        st.title("Welcome to the Messaging App")

        def submit_name():
            st.session_state["name"] = st.session_state["name_input"]
            st.session_state["name_input"] = ""

        st.text_input("Enter your name", key="name_input", on_change=submit_name)

    else:
        messaging_page()


def messaging_page():

    # todo maybe try https://stackoverflow.com/questions/74910140/how-do-i-update-values-in-streamlit-on-a-schedule
    # todo or maybe https://stackoverflow.com/questions/62718133/how-to-make-streamlit-reloads-every-5-seconds
    # todo or read more https://docs.streamlit.io/library/advanced-features/caching
    # todo or databutton: https://discuss.streamlit.io/t/is-it-possible-to-include-a-kind-of-scheduler-within-streamlit/31279
    st_autorefresh(interval=200, key="getting_game_data")
    st.title("Messaging Page")

    # Get the user's name from session state
    name = st.session_state["name"]

    with open(OUTPUT_PATH, "r") as f:
        st.session_state["messages"] = f.readlines()

    st.text("All messages:")
    for message in st.session_state["messages"]:
        st.text(message)

    def submit_message():
        now = f"{str(datetime.now().hour).zfill(2)}:" \
              f"{str(datetime.now().minute).zfill(2)}:" \
              f"{str(datetime.now().second).zfill(2)}"
        line = f"{now},{name},text,{st.session_state['user_text_input']}"
        st.session_state["user_text_input"] = ""
        with open(OUTPUT_PATH, "a") as f:
            f.write(line + "\n")

    st.text_input("Write a message", key="user_text_input", on_change=submit_message)
    time.sleep(4)


if __name__ == "__main__":
    main()



"""
Design Ideas:

players insert their names
they wait until predefined number of players signed in
they are assigned to roles
they are moved to the nighttime screen where their role is always presented to them
in nighttime screen bstanders dont see chat but only wait
after victim is chosen everyone moves to daytime screen where victim is declared
only players that weren't voted out can write in chat, timer starts, they can vote and change their votes
when timer finishes they need to vote (but can also vote before)
victim is declared
if mafia or bystanders didnt win yet (by predefined numbers) then we continue nighttime and daytime
"""