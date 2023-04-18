from base_dataset import BaseDataset
from con_game_data import ConGameData
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
from matplotlib.colors import BoundaryNorm
# import streamlit as st

UPPER_WORDS_PATTERN = r"\b[A-Z][A-Z]+\b"
MODEL_NAME = "all-MiniLM-L6-v2"
MARKER_SIZE = 2
COLOR_MAP = plt.cm.gist_rainbow
NUMBER_OF_CLUSTERS = 100


def get_training_format_message(message):
    """
    :param message: a pandas Series with "contents" in one of the following formats:
        type: "info", contents: "Phase Change to Nighttime/Daytime[: Victim - {player name}]"
        type: "vote", contents: "{player name}: {other player name}"
        type: "text", contents: "{player name}: {message}"
    :return: tuple of current turn's (info, player's message) in the following formats:
        "<phase change> {Nighttime/Daytime} [<victim> {player name} ]", ""
        "<player name> {player name} <vote> ", "{other player name} "
        "<player name> {player name} <text> ", "{message} "
    """
    if message["type"] == "info":
        tokens = re.search("(Phase Change) to (Nighttime|Daytime)(: Victim - (.*))?", message["contents"])
        tokened_message = f"<{tokens.group(1).lower()}> {tokens.group(2)} "
        if tokens.group(3):
            return tokened_message + f"<victim> {tokens.group(4)} ", ""
        else:
            return tokened_message, ""
    else:  # message["type"] in ("text", "vote")
        tokens = re.search("(.*?): (.*)", message["contents"])
        return f"<player name> {tokens.group(1)} <{message['type']}> ", f"{tokens.group(2)} "


def create_player_ids_dicts(all_players):
    """
    :param all_players: dataframe of all players in a specific game
    :return: dict of 3 keys: "full", "first", "last",
             each one has a dict as value, with keys of all possible names (in the relevant format) as a
             case-insensitive regex, and their ids
    """
    player_id_dict_full = dict()
    player_id_dict_first = dict()
    player_id_dict_last = dict()
    for player_id in all_players["id"]:
        if player_id == 1:  # no name, only network info
            continue
        player_name = all_players[all_players['id'] == player_id]['property1'].values.item()
        player_id_dict_full[fr"(?i)\b{player_name}\b"] = f"Player {player_id}"
        names = player_name.split()
        player_id_dict_first[fr"(?i)\b{names[0]}\b"] = f"Player {player_id}"
        if len(names) > 1:
            player_id_dict_last[fr"(?i)\b{names[1]}\b"] = f"Player {player_id}"
    return {"full": player_id_dict_full, "first": player_id_dict_first, "last": player_id_dict_last}


def replace_names_with_player_ids(message, player_id_dicts):
    """
    :param message: string representing a turn in the game
    :param player_id_dicts: dict of the format described in the documentation of create_player_ids_dicts
    :return: message, with names replaces with
    """
    for name_format in ["full", "first", "last"]:
        for name_pattern in player_id_dicts[name_format]:
            message = re.sub(name_pattern, player_id_dicts[name_format][name_pattern], message)
    return message


class ConDataset(BaseDataset):
    """
    Dataset object, designated to represent the dataset from the Con article.

    Current used special tokens:
        <phase change>, <victim>, <player name>, <vote>, <text> and additional tokens used by the ConGameData class.
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
        self.game_dirs = [os.path.join(folder_path, subdir) for subdir in os.listdir(folder_path)
                          if os.path.isdir(os.path.join(folder_path, subdir))]
        self.raw_sentences = self.extract_raw_sentences()
        self.all_names, self.first_names, self.last_names = self.extract_players_names()
        self.sentences_lowered = False
        self.sentences = self.remove_speaker_names_from_all_sentences()
        self.placeholders_for_names = False

    def extract_table_from_all_games(self, table_name):
        """
        Merges into one pandas-dataframe all the tables with the same name from
        all game dirs.
        :param table_name: 'info' / 'network' / 'node' (without .csv suffix)
        :return: Merged tables as dataframe
        """
        return pd.concat([pd.read_csv(os.path.join(game, table_name + ".csv"))
                          for game in self.game_dirs], ignore_index=True)

    def get_data_of_winning_players_by_role(self, role, use_player_ids=False):
        """
        Gets all the games' data where players with `role` have won, for all of those players
        :param role: either 'mafia' / 'mafioso' or 'bystanders' / 'bystander'
        :param use_player_ids: whether to use players' ids instead of names
        :return: the requested data as a dataframe
        """
        training_data_records = []
        player_id_dicts = dict()
        team = "mafia" if role in ("mafia", "mafioso") else "bystanders"
        role = "mafioso" if role in ("mafia", "mafioso") else "bystander"
        for game in self.game_dirs:
            game_id = os.path.basename(game)
            # column of "property2" in network.csv (which has only 1 rows) is the group who won
            if pd.read_csv(os.path.join(game, "network.csv")).loc[0]["property2"] == team:
                all_messages = pd.read_csv(os.path.join(game, "info.csv")).sort_values("id")
                all_players = pd.read_csv(os.path.join(game, "node.csv"))
                if use_player_ids:
                    player_id_dicts = create_player_ids_dicts(all_players)
                winning_players_ids = all_players[(all_players.type == role) & all_players.property2]["id"]
                for player_id in winning_players_ids:
                    # "property1" in node.csv is the player name
                    player_name = all_players[all_players.id == player_id]["property1"].values.item()
                    accumulated_messages = ""
                    is_it_nighttime = True
                    for index, message in all_messages.iterrows():
                        if message["type"] == "info":
                            if "Nighttime" in message["contents"]: is_it_nighttime = True
                            elif "Daytime" in message["contents"]: is_it_nighttime = False
                        if is_it_nighttime and role == "bystander":
                            continue
                        turn_info, player_message = get_training_format_message(message)
                        if use_player_ids:
                            turn_info = replace_names_with_player_ids(turn_info, player_id_dicts)
                            player_message = replace_names_with_player_ids(player_message, player_id_dicts)
                            player_name = replace_names_with_player_ids(player_name, player_id_dicts)
                        accumulated_messages += turn_info
                        if message["origin_id"] == player_id:
                            training_data_records.append({"game_id": game_id, "player_name": player_name,
                                                          "accumulated_messages": accumulated_messages,
                                                          "player_message": player_message})
                        accumulated_messages += player_message  # empty str if only info
        return pd.DataFrame.from_records(training_data_records)

    def get_data_for_all_players(self, include_votes=True, use_player_ids=False, add_structured_data=False):
        """
        Gets all the games' data in a training-suitable format
        :param include_votes: whether to include votes or just text
        :param use_player_ids: whether to use players' ids instead of names
        :param add_structured_data: whether to add structured data to each row
        :return: the requested data as a dataframe
        """
        training_data_records = []
        player_id_dicts = dict()
        for game in self.game_dirs:
            game_id = os.path.basename(game)
            all_messages = pd.read_csv(os.path.join(game, "info.csv")).sort_values("id")
            all_players = pd.read_csv(os.path.join(game, "node.csv"))
            if use_player_ids:
                player_id_dicts = create_player_ids_dicts(all_players)
            for player_id in all_players["id"]:
                # "property1" in node.csv is the player name
                player_name = all_players[all_players.id == player_id]["property1"].values.item()
                if type(player_name) != str:  # probably the network's main node, not a real player
                    continue
                game_data = ConGameData(all_players, use_player_ids) if add_structured_data else None
                accumulated_messages = ""
                for index, message in all_messages.iterrows():
                    turn_info, player_message = get_training_format_message(message)
                    if use_player_ids:
                        turn_info = replace_names_with_player_ids(turn_info, player_id_dicts)
                        player_message = replace_names_with_player_ids(player_message, player_id_dicts)
                        player_name = replace_names_with_player_ids(player_name, player_id_dicts)
                    if message["origin_id"] == player_id and player_message and \
                            (include_votes or "<vote>" not in turn_info):
                        structured_data = game_data.get_as_text() if add_structured_data else ""
                        training_data_records.append({
                            "game_id": game_id, "player_name": player_name,
                            "game_data_until_now": accumulated_messages + structured_data + turn_info,
                            "player_message": player_message})
                    if add_structured_data:
                        game_data.update_game_data(turn_info, player_message)
                    accumulated_messages += turn_info + player_message  # player_message is empty if only info
        return pd.DataFrame.from_records(training_data_records)

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
        return "|".join([rf"\b{name}\b|\b{name.lower()}\b|\b{name.upper()}\b" for name in names])

    def replace_name_with_placeholder(self, sentence):
        """
        :param sentence: a string of text said by a player
        :return: a placeholder instead of a name reference
        (with distinction between first and last name)
        """
        first_names_pattern = ConDataset.names_pattern(self.first_names)
        last_names_pattern = ConDataset.names_pattern(self.last_names)
        return re.sub(last_names_pattern, self.LASTNAME_PLACE_HOLDER,
                      re.sub(first_names_pattern, self.FIRSTNAME_PLACE_HOLDER, sentence))

    def replace_all_names_with_placeholders(self):
        """
        Replaces all names in all sentences with placeholders and turns on the
        self.placeholders_for_names field
        :return: None
        """
        self.sentences = self.sentences.apply(self.replace_name_with_placeholder)
        self.placeholders_for_names = True

    def lower_all_sentences(self):
        """
        Lowers all sentences and turns on the self.sentences_lowered field
        :return: None
        """
        self.sentences = self.sentences.apply(lambda x: x.lower())
        self.sentences_lowered = True

    def find_identical_sentences_with_different_case(self, dest_path="./double_case_form_sentences.txt"):
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

    def find_sentences_with_str_from_group(self, dest_path, pattern=None, group_of_strs=None,
                                           strs_are_words=False, output_string_beginning=None):
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
            raise RuntimeError("Method must get either group_of_strs or  pattern")
        if not group_of_strs and strs_are_words:
            warnings.warn("strs_are_words=True has no meaning when group_of_strs is None")
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
        output_string = output_string_beginning + f"\n\nTotal amount: {amount}\n\nAll strings and their " \
                                                  f"counts (sorted):\n"
        for word_count in sorted(all_words.items(),
                                 key=lambda item: item[1], reverse=True):
            output_string += f"{word_count[0]}: {word_count[1]}\n"
        output_string += "\nAll sentences: (Each sentence is followed by its requested strings)\n\n"
        for sentence_and_words in sentences_with_words:
            output_string += sentence_and_words[0] + "\nStrings: " + \
                             ", ".join(sentence_and_words[1]) + "\n\n"
        with open(dest_path, "w") as f:
            f.write(output_string)
        print(f"{amount} unique sentences were found.\nFull results were saved in {dest_path}")

    def find_sentences_with_all_upper_words(self, dest_path="./sentences_with_upper_words.txt"):
        """
        Finds all unique sentences that contain all-upper case words.
        Saves them in dest_path
        :param dest_path: destination path to save results
        :return: None
        """
        if self.sentences_lowered:
            raise RuntimeError("All sentences were already lowered")
        output_string_beginning = "Sentences with all-upper case words:"
        self.find_sentences_with_str_from_group(dest_path, pattern=UPPER_WORDS_PATTERN,
                                                output_string_beginning=output_string_beginning)

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

    def cluster_sentences(self, number_of_clusters, export_to_csv=True):
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
            sentences_with_clusters.to_csv(f"{number_of_clusters}_clusters.csv")

        return kmeans_model.labels_

    def reduce_dimension_and_plot_clusters(self, dimension):  # todo maybe make it a method of BaseDataset (also in Con)
        """
        Reduces dimension and plots the clusters
        :param dimension: either 3 or 2
        :return: None
        """
        if self.sentences_with_clusters is None:
            self.cluster_sentences(number_of_clusters=NUMBER_OF_CLUSTERS,
                                   export_to_csv=False)
        if dimension not in (2, 3):
            raise ValueError("dimension must be either 2 or 3")
        pca = PCA(n_components=dimension)
        reduced_dimension_embedding = pca.fit_transform(self.embedding)
        fig = plt.figure()
        # norm = BoundaryNorm(np.arange(self.sentences_with_clusters.cluster.max() + 1),
        #                     COLOR_MAP.N)
        if dimension == 3:
            ax = fig.gca(projection='3d')
            ax.scatter(reduced_dimension_embedding[:, 0],
                       reduced_dimension_embedding[:, 1],
                       reduced_dimension_embedding[:, 2],
                       s=MARKER_SIZE,
                       c=self.sentences_with_clusters.cluster.values,
                       # cmap=COLOR_MAP,
                       # norm=norm
                       )
        else:  # dimension == 2
            plt.scatter(reduced_dimension_embedding[:, 0],
                        reduced_dimension_embedding[:, 1],
                        s=MARKER_SIZE,
                        c=self.sentences_with_clusters.cluster.values)
        plt.show()
        # st.write(fig)
