import string
from con_dataset import ConDataset
from docopt import docopt  # todo use this for usage and argv instead of paths

CON_DATASET_DIR_PATH = r"./datasets/Con article"
EMOJIS = [":)", ":(", "(:", "):", ":D", "D:",
          "XD", ":P", "XP", "P:", ":O", "O:",
          ":/", "\\:"]
EMOJIS_FOR_REGEX = ["".join(["[" + char + "]" for char in emoji])
                    for emoji in EMOJIS]
GREETINGS = ["hello", "hi", "hey"]
GREETING_PATTERNS = ["\\b" + word + "[" + word[-1] + "]*\\b"
                     for word in GREETINGS]
DOUBLE_PUNCTUATION = ("[" + string.punctuation + "]") * 2
TRIPLE_LETTERS = "|".join([char * 3 for char in string.ascii_lowercase])


def main():
    data = ConDataset(CON_DATASET_DIR_PATH)
    data.replace_all_names_with_placeholders()
    data.find_identical_sentences_with_different_case()
    data.find_sentences_with_all_upper_words()
    data.lower_all_sentences()
    data.find_sentences_with_str_from_group("sentences_with_greeting.txt",
                                            group_of_strs=GREETING_PATTERNS,
                                            strs_are_words=False)
    data.find_sentences_with_str_from_group("sentences_with_emojies.txt",
                                            group_of_strs=EMOJIS_FOR_REGEX,
                                            strs_are_words=False)
    data.find_sentences_with_str_from_group("sentences_with_double_punc.txt",
                                            pattern=DOUBLE_PUNCTUATION)
    data.find_sentences_with_str_from_group("sentences_with_mm.txt",
                                            pattern="mm")
    data.find_sentences_with_str_from_group(pattern="[.][.]",
                                            dest_path=
                                            "sentences_with_2_dots.txt")
    data.find_sentences_with_str_from_group("sentences_with_triplets.txt",
                                            pattern=TRIPLE_LETTERS)


if __name__ == "__main__":
    main()
