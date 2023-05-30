import streamlit as st
from streamlit_autorefresh import st_autorefresh
# from streamlit_message import message as st_message
from transformers import AutoTokenizer, AutoModelWithLMHead
import torch
from datetime import datetime
import time
OUTPUT_PATH = "/cs/snapless/gabis/nive/Mafia-Project/user_interface/game_output.csv" # todo validate relative path
OUTPUT_FILE_HEADER = "time,name,type,message"

#
# # Load the fine-tuned model
# model_name = 'gpt2'
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelWithLMHead.from_pretrained(model_name)
#
# # Set maximum length for generated text
# max_length = 100
#
# # Streamlit app header
# st.title("Language Model Interface")
#
# # List to store former messages
# message_history = []
#
# # Text input box
# input_text = st.text_area("Enter your input text here", "")
#
# # Add input text to message history
# if st.button("Send"):
#     message_history.append(input_text)
#
#     # Tokenize the input text
#     input_ids = tokenizer.encode(input_text, return_tensors='pt')
#
#     # Generate text from the model
#     output = model.generate(input_ids, max_length=max_length, num_return_sequences=1)
#     generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
#
#     # Add generated text to message history
#     message_history.append(generated_text)
#
# # Display message history
# st.text("Message History:")
# for message in message_history:
#     st.text(message)
#
# st_message("hey there", "0")
# st_message("you're a rock star", "1")
# st_message("yeah!", "2")
# # print(message_history)


def main():

    if 'name' not in st.session_state:
        st.title("Welcome to the Messaging App")

        def submit_name():
            st.session_state["name"] = st.session_state["name_input"]
            st.session_state["name_input"] = ""

        st.text_input("Enter your name", key="name_input", on_change=submit_name)

    else:
        messaging_page()

    # # Original:
    # # Check if user name is provided in session state
    # if 'user_name' not in st.session_state:
    #     st.title("Welcome to the Messaging App")
    #     # Prompt user for name
    #     name = st.text_input("Enter your name")
    #
    #     if st.button("Submit"):
    #         if name:
    #             # Store the user's name in session state
    #             st.session_state['user_name'] = name
    # else:
    #     messaging_page()


def messaging_page():

    def messaging_page_to_reload_automatically(timestamp):
        st_autorefresh(interval=100, key="getting_game_data")
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
            someone_else_sent_something = False
            while not someone_else_sent_something:
                with open(OUTPUT_PATH, "r") as f:
                    if st.session_state["messages"] != f.readlines():
                        someone_else_sent_something = True

        st.text_input("Write a message", key="user_text_input", on_change=submit_message)
        time.sleep(1)

    messaging_page_to_reload_automatically(datetime.now())


    # if "last_message" not in st.session_state:
    #     st.session_state["last_message"] = ""
    #
    # # st_autorefresh(interval=100, key="getting_game_data")
    #
    # # Get other users messages
    # with open(OUTPUT_PATH, "r") as f:
    #     output_file_last_line = f.readlines()[-1]
    # if 'messages' not in st.session_state:
    #     st.session_state['messages'] = []
    #     if output_file_last_line != OUTPUT_FILE_HEADER \
    #             and output_file_last_line not in st.session_state['messages']:
    #         st.session_state['messages'].append(output_file_last_line)

    # Text input for user to write messages
    # message = st.text_input("Write a message", key="message_input", value="")


    # Post the message
    # # if st.button("Post"):
    # if message:
    #     # Store the message in session state
    #     now = f"{str(datetime.now().hour).zfill(2)}:{str(datetime.now().minute).zfill(2)}:{str(datetime.now().second).zfill(2)}"
    #     line = f"{now},{name},text,{message}"
    #     # if line != st.session_state['last_message']:
    #     #     st.session_state['last_message'] = line
    #     #     st.session_state['messages'].append(line) # todo maybe remove
    #     # save this message in genreal database so other users can access it
    #     with open(OUTPUT_PATH, "a") as f:
    #         f.write(line + "\n")


    # # Display the messages
    # if 'messages' in st.session_state:
    #     st.text("Message History:")
    #     for msg in st.session_state['messages']:
    #         st.text(msg)


if __name__ == "__main__":
    main()
