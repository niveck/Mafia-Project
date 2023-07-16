import sys
from prepare import prepare
from main import decompress_file
from train.train_runner import run_train

if __name__ == "__main__":
    prepare()
    # decompress_file(r"./training_data/"
    #                 r"training_by_all_messages_without_votes_divided_to_turns_june_2023/"
    #                 r"train_data.csv.gz")
    # decompress_file(r"./training_data/"
    #                 r"training_by_all_messages_without_votes_divided_to_turns_june_2023/"
    #                 r"validation_data.csv.gz")
    # sys.argv[1] should be number of pass turns (1 or 2)
    run_train(f"t5_multitask_bystander_divided_to_turns_with_{sys.argv[1]}_pass_config."
              f"T5MultitaskBystanderDividedToTurnsWith{sys.argv[1]}PassConfig")
