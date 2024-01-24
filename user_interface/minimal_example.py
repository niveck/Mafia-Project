import streamlit as st


def move_to_page(page):
    st.session_state["page"] = page


def new_player_entry_page():
    st.title("Welcome to a minimal example...")
    def enter_waiting_room():  move_to_page("WAITING_FOR_OTHER_USERS_TO_ENTER")
    st.button("Click to move to waiting room", key="enter_waiting_room",
              on_click=enter_waiting_room)


def waiting_for_other_users_to_enter_page():
    st.title(f"**Welcome!**")
    st.info("Waiting for other players to enter...")
    move_to_page("NIGHTTIME")


def nighttime_page():
    st.title("Nighttime")
    st.info("Your role is bystander")


def main():
    if "page" not in st.session_state:
        st.session_state["page"] = "NEW_PLAYER_ENTRY"
    page = st.session_state["page"]
    if page == "NEW_PLAYER_ENTRY":
        new_player_entry_page()
    elif page == "WAITING_FOR_OTHER_USERS_TO_ENTER":
        waiting_for_other_users_to_enter_page()
    elif page == "NIGHTTIME":
        nighttime_page()


if __name__ == "__main__":
    main()
