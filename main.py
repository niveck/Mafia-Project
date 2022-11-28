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
GREETING_PATTERNS = ["\\b" + word + "+\\b" for word in GREETINGS]
DIFFERENT_LENGTHS_HAHA = [rf"\ba*{'ha' * i}h*\b" for i in range(1, 21)]
LAUGHS_PATTERN = "|".join(DIFFERENT_LENGTHS_HAHA) + r"|\blol+\b|\blmao+\b"
DOUBLE_PUNCTUATION = ("[" + string.punctuation + "]") * 2
TRIPLE_LETTERS = "|".join([char * 3 for char in string.ascii_lowercase])
HMM_PATTERN="\\W*\\bhm+[.]*\\b\\W*"
ONLY_HMM_PATTERN = "\\A" + HMM_PATTERN + "\\Z"


def main():
    data = ConDataset(CON_DATASET_DIR_PATH)
    data.replace_all_names_with_placeholders()
    data.find_identical_sentences_with_different_case()
    data.find_sentences_with_all_upper_words()
    data.lower_all_sentences()
    data.find_sentences_with_str_from_group("sentences_with_hmm.txt",
                                            pattern=HMM_PATTERN)
    data.find_sentences_with_str_from_group("only_hmm_sentences.txt",
                                            pattern=ONLY_HMM_PATTERN)
    data.find_sentences_with_str_from_group("sentences_with_laughs.txt",
                                            pattern=LAUGHS_PATTERN)
    data.find_sentences_with_str_from_group("sentences_with_greeting.txt",
                                            group_of_strs=GREETING_PATTERNS,
                                            strs_are_words=False)
    data.find_sentences_with_str_from_group("sentences_with_emojis.txt",
                                            group_of_strs=EMOJIS_FOR_REGEX,
                                            strs_are_words=False)
    data.find_sentences_with_str_from_group("sentences_with_double_punc.txt",
                                            pattern=DOUBLE_PUNCTUATION)
    data.find_sentences_with_str_from_group("sentences_with_triplets.txt",
                                            pattern=TRIPLE_LETTERS)


if __name__ == "__main__":
    main()
