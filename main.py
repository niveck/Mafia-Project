import string
import pandas as pd
from con_dataset import ConDataset
from mafiasum_dataset import MafiascumDataset
import gzip

# from docopt import docopt  # todo use this for usage and argv instead of paths

CON_DATASET_DIR_PATH = r"./datasets/Con article"
MAFIASCUM_DATASET_DIR_PATH = r"./datasets/Mafiascum"
EMOJIS = [":)", ":(", "(:", "):", ":D", "D:",
          "XD", ":P", "XP", "P:", ":O", "O:",
          ":/", "\\:"]
EMOJIS_FOR_REGEX = ["".join(["[" + char + "]" for char in emoji])
                    for emoji in EMOJIS]
GREETINGS = ["hello", "hi", "hey"]
GREETING_PATTERNS = ["\\b" + word + "+\\b" for word in GREETINGS]
DIFFERENT_LENGTHS_HAHA = [rf"\ba*{'ha' * i}h*\b" for i in range(1, 21)]
LAUGHS_PATTERN = "|".join(DIFFERENT_LENGTHS_HAHA) + r"|\blol+\b|\blmao+\b"
DOUBLE_PUNCTUATION = ("[" + string.punctuation + "]") * 2
TRIPLE_LETTERS = "|".join([char * 3 for char in string.ascii_lowercase])
HMM_PATTERN = "\\W*\\bhm+[.]*\\b\\W*"
ONLY_HMM_PATTERN = "\\A" + HMM_PATTERN + "\\Z"
NUMBER_OF_CLUSTERS = 100
REDUCED_DIMENSION_3D = 3
VALIDATION_GAME_IDS = ["f0ac69d0-a9ee-662f-6cdd-b64dbf23a72d-data",
                       "f2c4a8cd-7cf5-efa0-bc21-b8f655da8b09-data",
                       "fb8339cf-c251-ac37-d742-4c4b3ee16a53-data"]


def con_dataset_main():
    """
    Main method runs for the Con dataset
    """
    data = ConDataset(CON_DATASET_DIR_PATH)
    data.replace_all_names_with_placeholders()
    # data.find_identical_sentences_with_different_case()
    # data.find_sentences_with_all_upper_words()
    data.lower_all_sentences()
    # data.find_sentences_with_str_from_group("sentences_with_hmm.txt",
    #                                         pattern=HMM_PATTERN)
    # data.find_sentences_with_str_from_group("only_hmm_sentences.txt",
    #                                         pattern=ONLY_HMM_PATTERN)
    # data.find_sentences_with_str_from_group("sentences_with_laughs.txt",
    #                                         pattern=LAUGHS_PATTERN)
    # data.find_sentences_with_str_from_group("sentences_with_greeting.txt",
    #                                         group_of_strs=GREETING_PATTERNS,
    #                                         strs_are_words=False)
    # data.find_sentences_with_str_from_group("sentences_with_emojis.txt",
    #                                         group_of_strs=EMOJIS_FOR_REGEX,
    #                                         strs_are_words=False)
    # data.find_sentences_with_str_from_group("sentences_with_double_punc.txt",
    #                                         pattern=DOUBLE_PUNCTUATION)
    # data.find_sentences_with_str_from_group("sentences_with_triplets.txt",
    #                                         pattern=TRIPLE_LETTERS)
    data.cluster_sentences(number_of_clusters=NUMBER_OF_CLUSTERS)
    data.reduce_dimension_and_plot_clusters(dimension=REDUCED_DIMENSION_3D)


def mafiascum_dataset_main():
    """
    Main method runs for the MafiaScum dataset
    """
    data = MafiascumDataset(MAFIASCUM_DATASET_DIR_PATH)
    raw_dataset = data.raw_dataset
    print("breaking point")


def preprocess_con_data_for_training_by_role():
    """
    Saves csv files with tables for training model over the Con Dataset, with messages distinguished by role
    """
    data = ConDataset(CON_DATASET_DIR_PATH)
    bystanders_training_data_with_names = data.get_data_of_winning_players_by_role("bystander")
    bystanders_training_data_with_ids = data.get_data_of_winning_players_by_role("bystander",
                                                                                 use_player_ids=True)
    bystanders_training_data_with_names.to_csv("bystanders_training_data_with_names.csv")
    bystanders_training_data_with_ids.to_csv("bystanders_training_data_with_ids.csv")
    mafia_training_data_with_names = data.get_data_of_winning_players_by_role("mafia")
    mafia_training_data_with_ids = data.get_data_of_winning_players_by_role("mafia", use_player_ids=True)
    mafia_training_data_with_names.to_csv("mafia_training_data_with_names.csv")
    mafia_training_data_with_ids.to_csv("mafia_training_data_with_ids.csv")


def preprocess_all_con_data_for_training(add_structured_data=True):
    """
    Saves csv files with tables for training model over the Con Dataset, with no distinction by role
    """
    data = ConDataset(CON_DATASET_DIR_PATH)
    # get_data_for_all_players
    path_prefix = "./training_data/training_by_all_data_with_structured_data_april_2023/"
    file_prefix = "train_and_validation_data_combined"
    if add_structured_data:
        file_prefix += "_with_structured_data"
    data.get_data_for_all_players(include_votes=True, use_player_ids=True, add_structured_data=add_structured_data)\
        .to_csv(path_prefix + file_prefix + "_with_votes_with_ids.csv")
    data.get_data_for_all_players(include_votes=False, use_player_ids=True, add_structured_data=add_structured_data)\
        .to_csv(path_prefix + file_prefix + "_without_votes_with_ids.csv")
    data.get_data_for_all_players(include_votes=True, use_player_ids=False, add_structured_data=add_structured_data)\
        .to_csv(path_prefix + file_prefix + "_with_votes_with_names.csv")
    data.get_data_for_all_players(include_votes=False, use_player_ids=False, add_structured_data=add_structured_data)\
        .to_csv(path_prefix + file_prefix + "_without_votes_with_names.csv")


def preprocess_con_data_divided_to_turns(number_of_pass_messages=0):
    """
    Saves csv files with tables for training model over the Con Dataset,
    such that every message is a turn in the game where the current player sends it
    and other players send a message of <pass>
    :param number_of_pass_messages: how many other players should be sampled to say <pass> each turn
    """
    data = ConDataset(CON_DATASET_DIR_PATH)
    dir_path = f"./training_data/training_without_votes_" \
               f"divided_to_turns_with_{number_of_pass_messages}_pass_july_2023/"
    target_file_name = "train_and_validation_data_combined.csv"
    data.get_data_for_all_players_divided_to_turns(include_votes=False, add_structured_data=False,
                                                   pass_messages_per_turn=number_of_pass_messages)\
        .to_csv(dir_path + target_file_name)


def split_to_train_and_validation(data_csv_path, train_output_path=None,
                                  validation_output_path=None):
    train_and_validation_prefix = "train_and_validation_data_combined"
    if not train_output_path or not validation_output_path:
        if train_and_validation_prefix in data_csv_path:
            train_output_path = data_csv_path.replace(train_and_validation_prefix, "train_data")
            validation_output_path = data_csv_path.replace(train_and_validation_prefix,
                                                           "validation_data")
            print(f"Output paths not fully provided, so were generated out of data_csv_path:"
                  f"\ntrain_output_path: {train_output_path}"
                  f"\nvalidation_output_path: {validation_output_path}")
        else:
            raise ValueError("Output paths not fully provided "
                             "and could not be generated out of data_csv_path")
    all_data = pd.read_csv(data_csv_path)
    rows_of_validation_games = all_data["game_id"].isin(VALIDATION_GAME_IDS)
    all_data[~rows_of_validation_games].to_csv(train_output_path, index=False)
    all_data[rows_of_validation_games].to_csv(validation_output_path, index=False)


def compress_file(file_to_compress_path):
    with open(file_to_compress_path, "rb") as f_in:
        with gzip.open(file_to_compress_path + ".gz", "wb") as f_out:
            f_out.writelines(f_in)


def decompress_file(compressed_file_path, decompressed_output_path=None):
    if not decompressed_output_path:
        decompressed_output_path = compressed_file_path.replace(".gz", "")
    with gzip.open(compressed_file_path, "rb") as f_in:
        with open(decompressed_output_path, "wb") as f_out:
            f_out.write(f_in.read())


if __name__ == "__main__":
    # con_dataset_main()
    # mafiascum_dataset_main()
    # preprocess_con_data_for_training_by_role()
    # preprocess_all_con_data_for_training()
    preprocess_con_data_divided_to_turns(number_of_pass_messages=1)
    preprocess_con_data_divided_to_turns(number_of_pass_messages=2)
    # split_to_train_and_validation(r"./training_data/training_by_all_messages_without_votes_divided_to_turns_june_2023/train_and_validation_data_combined.csv")

