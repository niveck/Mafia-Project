from base_dataset import BaseDataset
import re
import os
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans

MODEL_NAME = "all-MiniLM-L6-v2"


class MafiascumDataset(BaseDataset):
    """
    Dataset object, designated to represent the dataset from the Mafiascum article
    https://arxiv.org/pdf/1811.07851.pdf
    It is a collection of 685 games of Mafia, with over 9676 lines,
    each one contains all messages written by a single player in a single game.
    """
    SAME_PLAYER_SENTENCE_DELIMITER = ' /!@ '
    NICKNAME_PLACE_HOLDER = "nameplaceholder"

    def __init__(self, folder_path):
        """
        Initializes primary fields
        :param folder_path: path to the folder containing the data of the
        dataset (can be arranged in different formats)
        :return: a new dataset object
        """
        super().__init__(folder_path)
        self.raw_dataset = pd.read_pickle(folder_path + "/src/docs.pkl", compression="gzip")
        self.raw_sentences = self.extract_raw_sentences()
        self.language_model = None
        self.embedding = None
        self.sentences_with_clusters = None
        self.all_names = self.extract_players_names()
        self.sentences_lowered = False
        self.sentences = self.raw_sentences  # might be changed in the future
        self.placeholders_for_names = False
        """
        Important impressions about the dataset - they use the word scum for mafia, and town for bystander.
        It appears to have a role of a mason.
        They use free text for: 'vote: ___' / 'VOTE: ___' / 'unvote: ___' / '@<player's name> ___' in an
        informal manner, instead of waiting for a day to end and then vote
        The nicknames are sometimes to long/difficult, so the players use shortnames and nicknames 
        Most players start a new games with "confirm" or with a typo
        Some sentences are really long with a lot of strategy and explanations, 
        since games could last 2 weeks. Many players use a lot of '\\n'.
        """

    def extract_players_names(self):
        """
        :return: an array of all player's usernames.
        """
        return self.raw_dataset["author"].unique()

    def extract_raw_sentences(self):
        """
        :return: pandas Series of all raw sentences of dataset
        """
        raw_sentences = []

        def split_to_sentences_and_add_to_list(player_full_text):
            for sentence in re.split(self.SAME_PLAYER_SENTENCE_DELIMITER + "|\n", player_full_text):
                if sentence:
                    raw_sentences.append(sentence)

        self.raw_dataset["content"].apply(split_to_sentences_and_add_to_list)
        return pd.Series(raw_sentences)

    @staticmethod
    def names_pattern(names):  # todo maybe make it a method of BaseDataset (also in Con)
        """
        :param names: list of strings representing names
        :return: a regex pattern for all case versions of all names
        """
        return "|".join([rf"\b{name}\b|\b{name.lower()}\b|\b{name.upper()}\b" for name in names])

    def replace_name_with_placeholder(self, sentence):
        """
        :param sentence: a string of text said by a player
        :return: a placeholder instead of a name reference
        (with distinction between first and last name)
        """
        nicknames_pattern = MafiascumDataset.names_pattern(self.all_names)  # todo - problematic since some of them are english words (like "main")
        return re.sub(nicknames_pattern, self.NICKNAME_PLACE_HOLDER, sentence)

    def replace_all_names_with_placeholders(self):
        """
        Replaces all names in all sentences with placeholders and turns on the
        self.placeholders_for_names field
        :return: None
        """
        self.sentences = self.sentences.apply(self.replace_name_with_placeholder)
        self.placeholders_for_names = True

    def lower_all_sentences(self):  # todo maybe make it a method of BaseDataset (also in Con)
        """
        Lowers all sentences and turns on the self.sentences_lowered field
        :return: None
        """
        self.sentences = self.sentences.apply(lambda x: x.lower())
        self.sentences_lowered = True

    def embed_sentences(self):  # todo maybe make it a method of BaseDataset (also in Con)
        """
        Downloads a language model (if not already downloaded) and
        saves an embedding of all sentences by self.language_model.
        :return: None
        """
        if self.language_model is None:
            print("Language Model is being downloaded...")
            self.language_model = SentenceTransformer(MODEL_NAME)
            print("Language Model downloaded successfully")
        self.embedding = self.language_model.encode(self.sentences.to_list())

    def cluster_sentences(self, number_of_clusters, export_to_csv=True):   # todo maybe make it a method of BaseDataset (also in Con)
        """
        Clusters all sentences by their embedding,
        using number_of_clusters-Means clustering
        :param number_of_clusters: requested number of clusters
        :param export_to_csv: whether to export the cluster of each sentence to
        csv, including distance from cluster's center
        :return: clustering of the sentences (into number_of_clusters clusters)
        """
        if self.embedding is None:
            self.embed_sentences()
        kmeans_model = KMeans(n_clusters=number_of_clusters, random_state=0)
        kmeans_model.fit(self.embedding)
        sentences_with_clusters = pd.concat([self.sentences.reset_index(drop=True),
                                             pd.Series(kmeans_model.labels_)],
                                            axis=1,
                                            ignore_index=True)
        sentences_with_clusters.columns = ["sentence", "cluster"]

        # calculate distance from cluster center of each sentence:
        sentences_with_clusters["distance_from_cluster_center"] = \
            np.linalg.norm(self.embedding - kmeans_model.cluster_centers_[kmeans_model.labels_], axis=1)
            # np.apply_along_axis(np.linalg.norm, 1,
            #                     self.embedding[sentences_with_clusters.index]
            #                     - all_centers[kmeans_model.labels_
            #                     [sentences_with_clusters.index]])

        # add the average distance of each cluster as another column for convenience:
        sentences_with_clusters["cluster_average_distance_from_center"] = \
            sentences_with_clusters.groupby("cluster")["distance_from_cluster_center"].mean()[
                sentences_with_clusters["cluster"]].values

        # add the standard deviation of the distance from cluster center
        # of each cluster as another column for convenience:
        sentences_with_clusters["cluster_distance_std_from_center"] = \
            sentences_with_clusters.groupby("cluster")["distance_from_cluster_center"].std()[
                sentences_with_clusters["cluster"]].values

        self.sentences_with_clusters = sentences_with_clusters

        if export_to_csv:
            sentences_with_clusters.to_csv(f"{number_of_clusters}_clusters_mafiascum.csv")

        return kmeans_model.labels_

    def cluster_sentences(self, number_of_clusters):
        """
        Clusters all sentences in the dataset, using todo complete chosen model
        :param number_of_clusters: requested number of clusters
        :return: None
        """
        raise NotImplementedError()
