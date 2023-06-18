from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import os

MODEL_NAME = "t5-large"
SPECIAL_TOKENS = ["<player name>", "<phase change>", "<vote>", "<victim>", "<text>",
                  "<voting history>", "<mention history>", "<talking percentage>"]
EXAMPLE_MESSAGE = "<phase change> Nighttime <player name> Natalie Morris <text> Yo <player name> " \
                  "Ryan Hodges <text> hi <player name> Natalie Morris <text> who shall we knock " \
                  "off first? Bryce? <player name> Ryan Hodges <text> sure <player name> Ryan " \
                  "Hodges <vote> Bryce Fields <player name> Natalie Morris <vote> Bryce Fields " \
                  "<phase change> Daytime <phase change> Daytime <player name> Mary Trujillo " \
                  "<text> hello <player name> Christina Rollins <text> Hi <player name> Troy " \
                  "Thomas <text> I don't really understand how we're supposed to know who to " \
                  "vote for, I just chose Bryce Fields at random.. <player name> Ryan Hodges " \
                  "<text> hey <player name> Christopher Smith <text> Hello <player name> Diana " \
                  "Pennington <text> "
OUTPUT_PATH_DIR = "./predictions/t5_large_not_fine_tuned/greedy/"
TRAIN_SET = "./training_data/training_by_all_data_with_or_without_votes_february_2023/" #TODO continue


def prepare():
    os.environ["HF_DATASETS_CACHE"] = "../cache/hf_cache/datasets"
    os.environ["HF_METRICS_CACHE"] = "../cache/hf_cache/metrics"
    os.environ["HF_MODULES_CACHE"] = "../cache/hf_cache/modules"
    os.environ["HF_DATASETS_DOWNLOADED_EVALUATE_PATH"] = "../cache/hf_cache/datasets_downloaded_evaluate"
    os.environ["TRANSFORMERS_CACHE"] = "../cache/transformers_cache"
    os.environ["TORCH_HOME"] = "../cache/torch_home"


def generate_message(model, tokenizer, input_text):
    encoded_input = tokenizer.encode(input_text, return_tensors="pt")
    output = model.generate(encoded_input)
    decoded_output = tokenizer.decode(output[0], skip_special_tokens=True)
    print(decoded_output)
    return decoded_output


def main():
    prepare()
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.add_tokens(SPECIAL_TOKENS)
    generate_message(model, tokenizer, input_text=EXAMPLE_MESSAGE)



if __name__ == "__main__":
    main()
