from base_dataset import BaseDataset
import re
import os
import pandas as pd
from collections import defaultdict
import warnings


class ConDataset(BaseDataset):
    """
    Dataset object, designated to represent the dataset from the Con article
    """
    FIRSTNAME_PLACE_HOLDER = "firstname"
    LASTNAME_PLACE_HOLDER = "lastname"

    def __init__(self, folder_path):
        """
        Initializes primary fields
        :param folder_path: path to the folder containing the data of the
        dataset (can be arranged in different formats)
        :return: a new dataset object
        """
        super().__init__(folder_path)
        self.game_dirs = [os.path.join(folder_path, subdir)
                          for subdir in os.listdir(folder_path)
                          if os.path.isdir(os.path.join(folder_path, subdir))]
        self.raw_sentences = self.extract_raw_sentences()
        self.all_names, self.first_names, self.last_names = \
            self.extract_players_names()
        self.sentences_lowered = False
        self.sentences = self.remove_speaker_names_from_all_sentences()
        self.placeholders_for_names = False

    def extract_table_from_all_games(self, table_name):
        """
        Merges into one pandas dataframe all the tables with the same name from
        all game dirs.
        :param table_name: 'info' / 'network' / 'node' (without .csv suffix)
        :return: Merged tables as dataframe
        """
        return pd.concat([pd.read_csv(os.path.join(game, table_name + ".csv"))
                          for game in self.game_dirs], ignore_index=True)

    def extract_players_names(self):
        """
        :return: 3 sets of all unique names in the game: full names, only first
        names and only last names
        """
        table = self.extract_table_from_all_games("node")
        all_names = set(table["property1"])
        first_names = set()
        last_names = set()
        for name in all_names:
            if type(name) != str:
                continue
            first_and_last = name.split()
            first_names.add(first_and_last[0])
            if len(first_and_last) > 1:
                last_names.add(first_and_last[1])
        return all_names, first_names, last_names

    def extract_raw_sentences(self):
        """
        :return: pandas Series of all raw sentences of dataset
        """
        info = self.extract_table_from_all_games("info")
        return info[info.type == "text"]["contents"]

    @staticmethod
    def remove_speaker_name_from_sentence(sentence):
        """
        :param sentence: string in the format of "<Full Name>: <content>"
        :return: slicing of only "<content>"
        """
        return sentence[sentence.find(":") + 2:]

    def remove_speaker_names_from_all_sentences(self):
        """
        :return: the pandas Series of sentences, without the speaker prefix
        """
        return self.raw_sentences.apply(self.remove_speaker_name_from_sentence)

    def replace_name_with_placeholder(self, sentence):
        """
        :param sentence: a string of text said by a player
        :return: a placeholder instead of a name reference
        (with distinction between first and last name)
        """
        first_names_pattern = "|".join([r"\b" + name + r"\b"
                                        for name in self.first_names])
        last_names_pattern = "|".join([r"\b" + name + r"\b"
                                       for name in self.last_names])
        first_names_pattern += first_names_pattern.lower()
        last_names_pattern += last_names_pattern.lower()
        return re.sub(last_names_pattern, self.LASTNAME_PLACE_HOLDER,
                      re.sub(first_names_pattern, self.FIRSTNAME_PLACE_HOLDER,
                             sentence))

    def replace_all_names_with_placeholders(self):
        """
        Replaces all names in all sentences with placeholders and turns on the
        self.placeholders_for_names field
        :return: None
        """
        self.sentences = self.sentences.apply(
            self.replace_name_with_placeholder)
        self.placeholders_for_names = True

    def lower_all_sentences(self):
        """
        Lowers all sentences and turns on the self.sentences_lowered field
        :return: None
        """
        self.sentences = self.sentences.apply(lambda x: x.lower())
        self.sentences_lowered = True

    def find_identical_sentences_with_different_case(self,
                                                     dest_path="./double_case"
                                                               "_form_"
                                                               "sentences"
                                                               ".txt"):
        """
        Finds and counts all sentences that appear in both all-lower case and
        not-all-lower case forms. Used to determine how much data we will lose
        if we lower all sentences for training.
        Saves the results in dest_path.
        :param dest_path: destination path to save results
        :return: None
        """
        if self.sentences_lowered:
            raise RuntimeError("All sentences were already lowered")
        sentences_with_both_cases = set()
        for sentence in self.sentences:
            if re.match(r".*[A-Z].*", sentence):  # contains upper case chars
                if sentence.lower() in self.sentences.values:
                    sentences_with_both_cases.add(sentence)
        sentence_counts = self.sentences.value_counts()
        output_string = f"Sentences that exist in both upper and lower " \
                        f"case forms:\n\n" \
                        f"Total amount: {len(sentences_with_both_cases)}\n\n"
        for sentence in sentences_with_both_cases:
            output_string += f"Sentence:\n{sentence}" \
                             f"\nCount with upper case: " \
                             f"{sentence_counts[sentence]}" \
                             f"\nCount with lower case: " \
                             f"{sentence_counts[sentence.lower()]}\n\n"
        with open(dest_path, "w") as f:
            f.write(output_string)
        print(f"{len(sentences_with_both_cases)} unique sentences were found."
              f"\nFull results were saved in {dest_path}")

    def find_sentences_with_groups_of_words(self, dest_path,
                                            group_of_words=None, pattern=None,
                                            output_string_beginning=None):
        """
        Finds and counts all unique sentences that contain at least one word of
        the group or the pattern.
        Saves them in dest_path
        :param dest_path: destination path to save results
        :param group_of_words: list of strings
        :param pattern: regex pattern
        :param output_string_beginning: The requested beginning of the results
        file
        :return: None
        """
        # TODO there is a bug, because searching for "hey" gets also "they"
        # TODO but notice you can't just wrap each word with \b because then signs won't work
        # TODO should treat real words and signs differently! (maybe another flag)
        if not group_of_words and not pattern:
            raise RuntimeError("Method must get either group_of_words or "
                               "pattern")
        if group_of_words and pattern:
            warnings.warn("Both group_of_words and pattern were supplied,"
                          "so only pattern will be taken into account")
        if group_of_words:
            pattern = "|".join(group_of_words)
        sentences_with_words = set()
        all_words = defaultdict(int)
        for sentence in self.sentences:
            words = tuple(re.findall(pattern, sentence))
            if words:
                sentences_with_words.add((sentence, words))
                for word in words:
                    all_words[word] += 1
        if not output_string_beginning:
            output_string_beginning = f"All sentence with requested words:"
        output_string = output_string_beginning + f"\n\nTotal amount: " + \
                        f"{len(sentences_with_words)}\n\n" \
                        f"All words and their counts (sorted):\n"
        for word_count in sorted(all_words.items(),
                                 key=lambda item: item[1], reverse=True):
            output_string += f"{word_count[0]}: {word_count[1]}\n"
        output_string += "\nAll sentences: (Each sentence is followed by its" \
                         "requested words)\n\n"
        for sentence_and_words in sentences_with_words:
            output_string += sentence_and_words[0] + "\nWords: " + \
                             ", ".join(sentence_and_words[1]) + "\n\n"
        with open(dest_path, "w") as f:
            f.write(output_string)
        print(f"{len(sentences_with_words)} unique sentences were found."
              f"\nFull results were saved in {dest_path}")
        # TODO - make all other find-and-count methods more generic with no code duplication

    def find_sentences_with_all_upper_words(self, dest_path="./sentences_with"
                                                            "_upper_words."
                                                            "txt"):
        """
        Finds all unique sentences that contain all-upper case words.
        Saves them in dest_path
        :param dest_path: destination path to save results
        :return: None
        """
        if self.sentences_lowered:
            raise RuntimeError("All sentences were already lowered")
        sentences_with_upper_words = set()
        all_upper_words = defaultdict(int)
        for sentence in self.sentences:
            upper_words = tuple(re.findall(r"\b[A-Z][A-Z]+\b", sentence))
            if upper_words:
                sentences_with_upper_words.add((sentence, upper_words))
                for word in upper_words:
                    all_upper_words[word] += 1
        output_string = f"Sentences with all-upper case words:\n\n" \
                        f"Total amount: {len(sentences_with_upper_words)}" \
                        f"\n\nAll words and their counts (sorted):\n"
        for word_count in sorted(all_upper_words.items(),
                                 key=lambda item: item[1], reverse=True):
            output_string += f"{word_count[0]}: {word_count[1]}\n"
        output_string += "\nAll sentences: (Each sentence is followed by its" \
                         "all-upper case words)\n\n"
        for sentence_and_words in sentences_with_upper_words:
            output_string += sentence_and_words[0] + "\nWords: " + \
                             ", ".join(sentence_and_words[1]) + "\n\n"
        with open(dest_path, "w") as f:
            f.write(output_string)
        print(f"{len(sentences_with_upper_words)} unique sentences were found."
              f"\nFull results were saved in {dest_path}")

    def find_and_count_sentences_with_sequence(self, sequence, dest_path=None,
                                               prefix=False, suffix=False):
        """
        Finds and counts all unique sentences that contain sequence
        :param sequence: any requested string
        :param dest_path: destination path to save results
        :param prefix: whether to search pattern in beginning of sentences
        :param suffix: whether to search pattern in end of sentences
        :return: None
        """
        if prefix and suffix:
            raise RuntimeError("This method doesn't supports simultaneous"
                               "prefix and suffix search")
        if not dest_path:
            if sequence.isalpha():
                dest_path = f"./sentences_with_{sequence}_pattern.txt"
            else:
                raise RuntimeError("dest_path could not be automatically"
                                   "generated, should be given")
        if self.sentences_lowered and \
                re.match(r".*[A-Z].*", sequence):  # contains upper case chars
            warnings.warn("All sentence were lowered, but prefix contains "
                          "upper case letters.")
        if prefix:
            pattern = rf"\A{sequence}.*"
        elif suffix:
            pattern = rf".*{sequence}\Z"
        else:
            pattern = f".*{sequence}.*"
        sentences_with_pattern = defaultdict(int)
        for sentence in self.sentences:
            if re.match(pattern, sentence):
                sentences_with_pattern[sentence] += 1
        output_string = f"All sentences with the requested pattern of " \
                        f"{sequence}, preceded by their count (sorted):\n\n"
        for sentences_count in sorted(sentences_with_pattern.items(),
                                      key=lambda item: item[1], reverse=True):
            output_string += f"{sentences_count[1]}: {sentences_count[0]}\n"
        with open(dest_path, "w") as f:
            f.write(output_string)
        print(f"{len(sentences_with_pattern)} unique sentences were found."
              f"\nFull results were saved in {dest_path}")

    def cluster_sentences(self):
        """
        Clusters all sentences in the dataset, using todo complete chosen model
        :return: None
        """
        raise NotImplementedError()
