from abc import ABC, abstractmethod


class BaseDataset(ABC):
    """
    Father class representing a dataset with the general needed functions.
    """

    def __init__(self, folder_path):
        """
        Initializes primary fields
        :param folder_path: path to the folder containing the data of the
        dataset (can be arranged in different formats)
        :return: a new dataset object
        """
        self.folder_path = folder_path

    @abstractmethod
    def extract_players_names(self):
        """
        :return: todo decide what data structure of the names will be returned
        """
        raise NotImplementedError()

    @abstractmethod
    def extract_raw_sentences(self):
        """
        todo add explanation about the format of the sentences (with/without names, etc...)
        :return: todo decide what data structure of the sentences will be returned
        """
        raise NotImplementedError()

    @abstractmethod
    def cluster_sentences(self, number_of_clusters):
        """
        Clusters all sentences in the dataset, using todo complete chosen model
        :param number_of_clusters: requested number of clusters
        :return: None
        """
        raise NotImplementedError()




