import string
from con_dataset import ConDataset

CON_DATASET_DIR_PATH = r"./datasets/Con article"
TRIES_PATH = r"./tries"
EMOJIS = [":)", ":(", "(:", "):", ":D", "D:",
          "XD", ":P", "XP", "P:", ":O", "O:"]
EMOJIS_FOR_REGEX = ["".join(["[" + char + "]" for char in emoji])
                    for emoji in EMOJIS]
GREETINGS = ["hi", "hello", "hii", "hiii", "hey", "heyy", "heyyy"]
DOUBLE_PUNCTUATION = ("[" + string.punctuation + "]") * 2
TRIPLE_LETTERS = "|".join([char * 3 for char in string.ascii_lowercase])


def main():
    data = ConDataset(CON_DATASET_DIR_PATH)
    data.replace_all_names_with_placeholders()
    data.find_identical_sentences_with_different_case()
    data.find_sentences_with_all_upper_words()
    data.lower_all_sentences()
    data.find_sentences_with_groups_of_words("sentences_with_greeting.txt",
                                             group_of_words=GREETINGS)
    data.find_sentences_with_groups_of_words("sentences_with_emojies.txt",
                                             group_of_words=EMOJIS_FOR_REGEX)
    data.find_sentences_with_groups_of_words("sentences_with_double_punc.txt",
                                             pattern=DOUBLE_PUNCTUATION)
    data.find_and_count_sentences_with_sequence("mm")
    data.find_and_count_sentences_with_sequence("[.][.]",
                                                dest_path=
                                                "sentences_with_2_dots.txt")
    data.find_sentences_with_groups_of_words("sentences_with_triplets.txt",
                                             pattern=TRIPLE_LETTERS)


if __name__ == "__main__":
    main()