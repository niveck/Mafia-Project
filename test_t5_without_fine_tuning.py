from evaluate_on_game import evaluate_on_game
from prepare import prepare


MODEL_NAME = "t5-large"
MODEL_MAX_SOURCE_LENGTH = 512
# EXAMPLE_MESSAGE = "<phase change> Nighttime <player name> Natalie Morris <text> Yo <player name> " \
#                   "Ryan Hodges <text> hi <player name> Natalie Morris <text> who shall we knock " \
#                   "off first? Bryce? <player name> Ryan Hodges <text> sure <player name> Ryan " \
#                   "Hodges <vote> Bryce Fields <player name> Natalie Morris <vote> Bryce Fields " \
#                   "<phase change> Daytime <phase change> Daytime <player name> Mary Trujillo " \
#                   "<text> hello <player name> Christina Rollins <text> Hi <player name> Troy " \
#                   "Thomas <text> I don't really understand how we're supposed to know who to " \
#                   "vote for, I just chose Bryce Fields at random.. <player name> Ryan Hodges " \
#                   "<text> hey <player name> Christopher Smith <text> Hello <player name> Diana " \
#                   "Pennington <text> "
OUTPUT_PATH_DIR = "./predictions/t5_large_not_fine_tuned/greedy/"
VALIDATION_SET_DIR = "./training_data/training_by_all_data_with_or_without_votes_february_2023/"
VALIDATION_SET_FILE = "validation_data_without_votes_with_names.csv"
VALIDATION_SET_PATH = VALIDATION_SET_DIR + VALIDATION_SET_FILE
GAME_IDS = ["f0ac69d0-a9ee-662f-6cdd-b64dbf23a72d-data",
            "f2c4a8cd-7cf5-efa0-bc21-b8f655da8b09-data",
            "fb8339cf-c251-ac37-d742-4c4b3ee16a53-data"]


def main(game_id):
    print(f"Working with default constants")
    print(f"Dataset file: {VALIDATION_SET_FILE}")
    print(f"Game ID: {game_id}")
    evaluate_on_game(dataset_path=VALIDATION_SET_PATH, game_id=game_id,
                     max_source_length=MODEL_MAX_SOURCE_LENGTH,
                     pretrained_model_name=MODEL_NAME)
    print("\n")


if __name__ == "__main__":
    prepare()
    for game in GAME_IDS:
        main(game)
