from collections import defaultdict, Counter
import re

INCLUDE_VOTES_BY_ELIMINATED_PLAYERS = False
INCLUDE_MENTIONS_BY_ELIMINATED_PLAYERS = False
INCLUDE_TALKING_PERCENTAGE_OF_ELIMINATED_PLAYERS = False


class ConGameData:
    """
    Represents the non-textual data of a game from the Con dataset, like voting history and statistics
    Current used special tokens:
        <player name> (also used by the ConDataset class), <voting history>, <mention history>, <talking percentage>
    """

    def __init__(self, all_players, use_player_ids=False):
        """
        Initializes the game data object
        :param all_players: pandas DataFrame of all players in the game
        :param use_player_ids: whether the IDs of the players are used instead of their names
        """
        self.voting_history = defaultdict(list)
        self.mentioning_history = defaultdict(Counter)
        self.total_messages_counter = 0
        self.player_messages_counter = Counter()
        self.eliminated_players = set()
        if use_player_ids:
            self.players_names = {f"Player {num}": [f"Player {num}"]
                                  for num in all_players["id"] if num != 1}  # 1 is for source, not a player
        else:
            self.players_names = {f"{raw_name}": [raw_name] + raw_name.split()
                                  for raw_name in all_players["property1"].dropna()}

    def get_as_text(self):
        """
        Returns a textual representation of the game state's data
        """
        text = ""
        for player in self.voting_history:
            text += f"<player name> {player} <voting history> {', '.join(self.voting_history[player])} "
        for player in self.mentioning_history:
            player_mentioning_history = []
            for mentioned_player, count in self.mentioning_history[player].most_common():
                player_mentioning_history.append(f"{mentioned_player}: {count}")
            text += f"<player name> {player} <mention history> {', '.join(player_mentioning_history)} "
        text += f"<talking percentage> {self.get_talking_percentage_as_text()} "
        return text

    def update_game_data(self, turn_info, player_message):
        """
        Updates the game state's data fields
        """
        tokens = re.search("<(phase change|player name)> ([^<]+)(<(victim|vote|text)> ((.+) )?)?", turn_info)
        if tokens.group(4) == "victim":
            self.eliminated_players.add(tokens.group(6))
            if not INCLUDE_MENTIONS_BY_ELIMINATED_PLAYERS:
                if tokens.group(6) in self.mentioning_history:
                    del self.mentioning_history[tokens.group(6)]
            if not INCLUDE_VOTES_BY_ELIMINATED_PLAYERS:
                if tokens.group(6) in self.voting_history:
                    del self.voting_history[tokens.group(6)]
            if not INCLUDE_TALKING_PERCENTAGE_OF_ELIMINATED_PLAYERS:
                if tokens.group(6) in self.player_messages_counter:
                    del self.player_messages_counter[tokens.group(6)]
        elif tokens.group(4) == "vote":
            self.voting_history[tokens.group(2)].append(player_message.strip())
        elif tokens.group(4) == "text":
            self.total_messages_counter += 1
            self.player_messages_counter[tokens.group(2)] += 1
            self.update_mentioning_history(tokens.group(2), player_message)
        elif tokens.group(1) != "phase change":
            raise ValueError("Turn's info was in an invalid format")

    def update_mentioning_history(self, speaking_player_name, player_message):
        """
        Updates the mentioning_history dict by checking if the speaker player has mentioned one of the other
        players' names
        :param speaking_player_name: name of the speaking player
        :param player_message: message sent by the player (to check mentioning in)
        """
        for player, names in self.players_names.items():
            if re.search("(?i)" + "|".join([fr"\b{name}\b" for name in names]), player_message):
                self.mentioning_history[speaking_player_name][player] += 1

    def get_talking_percentage_as_text(self):
        """
        Returns a textual representation of the talking percentage of each active player in the game, sorted
        """
        all_percentages = []
        for player, count in self.player_messages_counter.most_common():
            all_percentages.append(f"{player}: {round(count / self.total_messages_counter) * 100}%")
        return ', '.join(all_percentages)
