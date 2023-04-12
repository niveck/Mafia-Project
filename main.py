import string
from con_dataset import ConDataset
from mafiasum_dataset import MafiascumDataset

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
    Main method runs for the Con dataset
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


if __name__ == "__main__":
    # con_dataset_main()
    # mafiascum_dataset_main()
    # preprocess_con_data_for_training_by_role()
    preprocess_all_con_data_for_training()
