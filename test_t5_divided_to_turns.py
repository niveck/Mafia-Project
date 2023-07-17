import sys
from evaluate_on_game import evaluate_on_game
from prepare import prepare

MODEL_PATH = "train_output_divided_to_turns_with_1_pass_to_100"
MODEL_MAX_SOURCE_LENGTH = 1024
OUTPUT_PATH_DIR = "predictions/t5_large_10_epochs_no_struct_beam_search/divided_to_turns_with_1_pass_to_100/"
VALIDATION_SET_PATH = "training_data/training_without_votes_divided_to_turns_with_1_pass_to_100_july_2023/validation_data.csv"
GAME_IDS = [
    "f0ac69d0-a9ee-662f-6cdd-b64dbf23a72d-data",
    "f2c4a8cd-7cf5-efa0-bc21-b8f655da8b09-data",
    "fb8339cf-c251-ac37-d742-4c4b3ee16a53-data"]


def main(game_id):
    print(f"Game ID: {game_id}")
    evaluate_on_game(dataset_path=VALIDATION_SET_PATH, game_id=game_id,
                     max_source_length=MODEL_MAX_SOURCE_LENGTH,
                     model_path=MODEL_PATH, output_dir_path=OUTPUT_PATH_DIR)
    print("\n")


if __name__ == "__main__":
    prepare()
    print(f"Working with default constants")
    for game in GAME_IDS:
        main(game)
