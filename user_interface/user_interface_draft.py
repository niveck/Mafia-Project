import streamlit as st
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import time

OUTPUT_PATH = "/cs/snapless/gabis/nive/Mafia-Project/user_interface/game_output.csv"
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
        lines = f.readlines()

    if len(lines) > 1 and lines[-1] == lines[-2]:
        lines.pop()
        with open(OUTPUT_PATH, "w") as f:
            f.writelines(lines)

    st.session_state["messages"] = lines

    st.text("All messages:")
    for message in st.session_state["messages"]:
        st.text(message)

    def submit_message():
        now = datetime.now()
        current_time = f"{now.hour:02d}:{now.minute:02d}:{now.second:02d}"
        line = f"{current_time},{name},text,{st.session_state['user_text_input']}"
        st.session_state["user_text_input"] = ""
        with open(OUTPUT_PATH, "a") as f:
            if "messages" in st.session_state and len(st.session_state["messages"]) > 0 \
                    and line != st.session_state["messages"][-1]:
                f.write(line + "\n")

    st.text_input("Write a message", key="user_text_input", on_change=submit_message)
    # time.sleep(4)


if __name__ == "__main__":
    main()
