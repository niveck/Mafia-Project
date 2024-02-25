import sys
from .chat_room import MODEL_PLAYER_DEFAULT_NAME, OUTPUT_PATH
from .evaluate_on_chat import evaluate_on_chat


def model_should_generate():
    return "!" != input("Enter ! to stop and finish generating messages, "
                        "or anything else to generate: ")


def main(model_path):
    while model_should_generate():
        prediction = evaluate_on_chat(model_path, model_player_name=MODEL_PLAYER_DEFAULT_NAME,
                                      chat_path=OUTPUT_PATH)
        print("Model generated:", prediction)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise ValueError("Usage: evaluate_on_chat.py <trained model path>")
    main(sys.argv[1])
