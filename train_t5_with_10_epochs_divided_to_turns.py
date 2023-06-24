from prepare import prepare
from main import decompress_file
from train.train_runner import run_train

if __name__ == "__main__":
    prepare()
    decompress_file(r"/cs/snapless/gabis/nive/Mafia-Project/training_data/"
                    r"training_by_all_messages_without_votes_divided_to_turns_june_2023/"
                    r"train_data.csv")
    decompress_file(r"/cs/snapless/gabis/nive/Mafia-Project/training_data/"
                    r"training_by_all_messages_without_votes_divided_to_turns_june_2023/"
                    r"validation_data.csv")
    run_train("train.train_configs."
              "t5_multitask_bystander_with_names_without_votes_divided_to_turns_config."
              "T5MultitaskBystanderWithNamesWithoutVotesDividedToTurnsConfig")
