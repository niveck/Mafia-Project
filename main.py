import os
import pandas as pd
from con_dataset import ConDataset

CON_DATASET_DIR_PATH = r"./datasets/Con article"
TRIES_PATH = r"./tries"

# def main():
#     data = ConDataset(CON_DATASET_DIR_PATH)
#     data.extract_table_from_all_games("info").to_csv(os.path.join(
#         TRIES_PATH, "all_info.csv"))


if __name__ == "__main__":
    # main()
    data = ConDataset(CON_DATASET_DIR_PATH)
    sentences = data.extract_all_sentences()
    lower = lambda x: x.lower()
    sentences_compare = pd.concat([sentences, sentences.apply(lower)], axis=1)
    sentences_compare.columns = ["contents", "lower_contents"]
    sentences_compare.to_csv("./tries/without_names.csv", index=False)
    # todo:
    # Count how many unique values are in regular case in contrary to lower
    # case
    # count how many end with: ?, !, .., ?!, !?, !!, ??, mm
    # the sentences that exist in both completely lower and not completely
    # import string # use string.punctuation
    # sentences_compare.lower_contents[sentences_compare.lower_contents.apply(lambda x: x[-1:])==".."]
    # sentences_compare.lower_contents[sentences_compare.lower_contents.apply(lambda x: x[-1:])=="mm"]
    # sentences_compare.lower_contents.value_counts()[:60]
