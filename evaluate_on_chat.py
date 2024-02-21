import sys
from train.demonstrate import Demonstrator
import torch
from user_interface.chat_room import format_chat_line, OUTPUT_PATH, MODEL_PLAYER_DEFAULT_NAME
import re


def preprocess_chat_messages(chat_path):
    with open(chat_path, "r") as f:
        chat_messages = f.readlines()
    history = ""
    for message in chat_messages:
        parts = re.search(r"\d\d:\d\d:\d\d \| ([^:]+): (.*)", message)
        history += f"<player name> {parts.group(1)} <text> {parts.group(2)} "
    return history


def send_prediction_to_chat(prediction, chat_path, model_player_name):
    line = format_chat_line(model_player_name, prediction)
    with open(chat_path, "a") as f:
        f.write(line + "\n")


def evaluate_on_chat(model_path, model_player_name=MODEL_PLAYER_DEFAULT_NAME, chat_path=OUTPUT_PATH,
                     max_source_length=1024):
    model = Demonstrator(max_source_length=max_source_length, model_path=model_path)
    history_in_model_format = preprocess_chat_messages(chat_path)  # should end with " "
    history_input = history_in_model_format + f"<player name> {model_player_name} <text> "
    with torch.no_grad():
        prediction = model.predict(history_input)
    send_prediction_to_chat(prediction, chat_path, model_player_name)
    return prediction


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise ValueError("Usage: evaluate_on_chat.py <trained model path>")
    evaluate_on_chat(sys.argv[1])
