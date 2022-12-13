from base_dataset import BaseDataset
import re
import os
import pandas as pd
import numpy as np
from collections import defaultdict
import warnings
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

UPPER_WORDS_PATTERN = r"\b[A-Z][A-Z]+\b"
MODEL_NAME = "all-MiniLM-L6-v2"
MARKER_SIZE = 2


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
        self.language_model = None
        self.embedding = None
        self.sentences_with_clusters = None
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

    @staticmethod
    def names_pattern(names):
        """
        :param names: list of strings representing names
        :return: a regex pattern for all case versions of all names
        """
        return "|".join([rf"\b{name}\b|\b{name.lower()}\b|\b{name.upper()}\b"
                         for name in names])

    def replace_name_with_placeholder(self, sentence):
        """
        :param sentence: a string of text said by a player
        :return: a placeholder instead of a name reference
        (with distinction between first and last name)
        """
        first_names_pattern = ConDataset.names_pattern(self.first_names)
        last_names_pattern = ConDataset.names_pattern(self.last_names)
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

    def find_sentences_with_str_from_group(self, dest_path, pattern=None,
                                           group_of_strs=None,
                                           strs_are_words=False,
                                           output_string_beginning=None):
        """
        Finds and counts all unique sentences that contain at least one string
        of the group or the pattern. Saves them in dest_path
        :param dest_path: destination path to save results
        :param pattern: regex pattern
        :param group_of_strs: list of strings
        :param strs_are_words: whether to treat group_of_strs as words
        :param output_string_beginning: The requested beginning of the results
        file
        :return: None
        """
        if not group_of_strs and not pattern:
            raise RuntimeError("Method must get either group_of_strs or "
                               "pattern")
        if not group_of_strs and strs_are_words:
            warnings.warn("strs_are_words=True has no meaning when"
                          "group_of_strs is None")
        if group_of_strs and pattern:
            warnings.warn("Both group_of_strs and pattern were supplied,"
                          "so only group_of_strs will be taken into account")
        if group_of_strs:
            if strs_are_words:
                group_of_strs = [fr"\b{word}\b" for word in group_of_strs]
            pattern = "|".join(group_of_strs)
        sentences_with_words = set()
        all_words = defaultdict(int)
        for sentence in self.sentences:
            words = tuple(re.findall(pattern, sentence))
            if words:
                sentences_with_words.add((sentence, words))
                for word in words:
                    all_words[word] += 1
        if not output_string_beginning:
            output_string_beginning = "All sentence with requested strings:"
        amount = len(sentences_with_words)
        output_string = output_string_beginning + f"\n\nTotal amount: " \
                                                  f"{amount}\n\nAll strings " \
                                                  f"and their counts " \
                                                  f"(sorted):\n"
        for word_count in sorted(all_words.items(),
                                 key=lambda item: item[1], reverse=True):
            output_string += f"{word_count[0]}: {word_count[1]}\n"
        output_string += "\nAll sentences: (Each sentence is followed by its" \
                         " requested strings)\n\n"
        for sentence_and_words in sentences_with_words:
            output_string += sentence_and_words[0] + "\nStrings: " + \
                             ", ".join(sentence_and_words[1]) + "\n\n"
        with open(dest_path, "w") as f:
            f.write(output_string)
        print(f"{amount} unique sentences were found."
              f"\nFull results were saved in {dest_path}")

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
        output_string_beginning = "Sentences with all-upper case words:"
        self.find_sentences_with_str_from_group(dest_path,
                                                pattern=UPPER_WORDS_PATTERN,
                                                output_string_beginning=
                                                output_string_beginning)

    def embed_sentences(self):
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

    def cluster_sentences(self, number_of_clusters=NUMBER_OF_CLUSTERS,
                          export_to_csv=True):
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
        sentences_with_clusters = pd.concat([self.sentences.reset_index(),
                                            pd.Series(kmeans_model.labels_)],
                                            axis=1,
                                            ignore_index=True).loc[:, 1:2]
        sentences_with_clusters.columns = ["sentence", "cluster"]

        # calculate center of each cluster:
        all_centers = np.zeros((number_of_clusters, self.embedding.shape[1]))
        clusters_count = np.unique(kmeans_model.labels_, return_counts=True)[1]
        for i, sentence_embedding in enumerate(self.embedding):
            all_centers[kmeans_model.labels_[i]] += sentence_embedding
        for i, cluster_count in enumerate(clusters_count):
            all_centers[kmeans_model.labels_[i]] /= cluster_count

        # calculate distance from cluster center of each sentence:
        sentences_with_clusters["distance_from_cluster_center"] = \
            np.apply_along_axis(np.linalg.norm, 1,
                                self.embedding[sentences_with_clusters.index]
                                - all_centers[kmeans_model.labels_
                                              [sentences_with_clusters.index]])

        # # add the average distance of each cluster as another column for convenience:
        # sentences_with_clusters["cluster_average_distance_from_center"] = \
        #     sentences_with_clusters.groupby("cluster")[
        #         "distance_from_cluster_center"].mean()[
        #         sentences_with_clusters["cluster"]].values

        # add the deviation of the distance from cluster center of each
        # sentence, from the cluster's average distance
        sentences_with_clusters["deviation_from_mean_dist_from_center"] = \
            np.abs(sentences_with_clusters.groupby("cluster")[
                       "distance_from_cluster_center"].mean()[
                       sentences_with_clusters["cluster"]].values
                   - sentences_with_clusters["distance_from_cluster_center"])

        # add the standart deviation of the distance from cluster center
        # of each cluster as another column for convenience:
        sentences_with_clusters["cluster_distance_std_from_center"] = \
            sentences_with_clusters.groupby("cluster")[
                "distance_from_cluster_center"].std()[
                sentences_with_clusters["cluster"]].values

        self.sentences_with_clusters = sentences_with_clusters

        if export_to_csv:
            sentences_with_clusters.to_csv(
                f"{number_of_clusters}_clusters.csv")

        return kmeans_model.labels_

    def reduce_dimension_and_plot_clusters(self,
                                           dimension=REDUCED_DIMENSION_3D):
        """
        Reduces dimension and plots the clusters
        :param dimension: either 3 or 2
        :return: None
        """
        if self.sentences_with_clusters is None:
            self.cluster_sentences(export_to_csv=False)
        if dimension not in (2, 3):
            raise ValueError("dimension must be either 2 or 3")
        pca = PCA(n_components=dimension)
        reduced_dimension_embedding = pca.fit_transform(self.embedding)
        fig = plt.figure()
        if dimension == 3:
            ax = fig.gca(projection='3d')
            ax.scatter(reduced_dimension_embedding[:, 0],
                       reduced_dimension_embedding[:, 1],
                       reduced_dimension_embedding[:, 2],
                       s=MARKER_SIZE,
                       c=self.sentences_with_clusters.cluster.values)
        else:  # dimension == 2
            plt.scatter(reduced_dimension_embedding[:, 0],
                        reduced_dimension_embedding[:, 1],
                        s=MARKER_SIZE,
                        c=self.sentences_with_clusters.cluster.values)
        plt.show()
