from evaluate_on_game import evaluate_on_game
from prepare import prepare


MODEL_PATH = "train_output_divided_to_turns_10_epochs"
MODEL_MAX_SOURCE_LENGTH = 512
OUTPUT_PATH_DIR = "./predictions/t5_large_not_fine_tuned/with_instruction/"
VALIDATION_SET_DIR = "./training_data/training_by_all_messages_without_votes_divided_to_turns_june_2023/"
VALIDATION_SET_FILE = "validation_data.csv"
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
                     model_path=MODEL_PATH, output_dir_path=OUTPUT_PATH_DIR)
    print("\n")


if __name__ == "__main__":
    prepare()
    for game in GAME_IDS:
        main(game)
