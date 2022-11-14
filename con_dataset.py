from base_dataset import BaseDataset
import os
import pandas as pd


class ConDataset(BaseDataset):
    """
    Dataset object, designated to represent the dataset from the Con article
    """
    NAME_PLACE_HOLDER = "NAME"

    def __init__(self, folder_path):
        """
        Initializes primary fields
        :param folder_path: path to the folder containing the data of the
        dataset (can be arranged in different formats)
        :return: a new dataset object
        """
        super().__init__(folder_path)  # todo make sure right syntax
        self.game_dirs = [os.path.join(folder_path, subdir)
                          for subdir in os.listdir(folder_path)
                          if os.path.isdir(os.path.join(folder_path, subdir))]
        self.sentences = self.extract_all_sentences()
        self.all_unique_names

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
        :return: todo decide what data structure of the names will be returned
        """
        raise NotImplementedError()

    def extract_all_sentences(self):
        """
        todo add explanation about the format of the sentences (with/without names, etc...)
        :return: todo decide what data structure of the sentences will be returned
        """
        info = self.extract_table_from_all_games("info")
        return info[info.type == "text"]["contents"].apply(
            self.remove_name_from_sentence)
        # todo finish when you return the right data structure

    @staticmethod
    def remove_name_from_sentence(sentence):
        """
        :param sentence: string in the format of "<Full Name>: <content>"
        :return: slicing of only "<content>"
        """
        return sentence[sentence.find(":") + 1:]

    def replace_name_with_placeholder(self, sentence):
        """
        :param sentence: a string of text said by a player
        :return: a placeholder instead of a name reference
        """
        #todo use re.sub or re.search and string.punctuation


    def cluster_sentences(self):
        """
        Clusters all sentences in the dataset, using todo complete chosen model
        :return: None
        """
        raise NotImplementedError()
