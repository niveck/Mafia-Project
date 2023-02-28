from abc import ABC, abstractmethod

NUMBER_OF_BINS = 25


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
        self.sentences = None

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

    def sentence_length_histogram(self):
        """
        Presents a histogram for lengths of sentences in dataset, by number of words
        """
        self.sentences.apply(lambda sentence: len(sentence.split(" "))).plot.hist(bins=NUMBER_OF_BINS)

    @abstractmethod
    def cluster_sentences(self, number_of_clusters):
        """
        Clusters all sentences in the dataset, using todo complete chosen model
        :param number_of_clusters: requested number of clusters
        :return: None
        """
        raise NotImplementedError()




