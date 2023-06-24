from train.train_configs.default_config import DefaultConfig


class T5MultitaskBystanderWithNamesWithoutVotesDividedToTurnsConfig(DefaultConfig):
    def __init__(self):
        super().__init__(
            train_file='training_data/training_by_all_messages_without_votes_divided_to_turns_june_2023/train_data.csv',
            validation_file='training_data/training_by_all_messages_without_votes_divided_to_turns_june_2023/validation_data.csv',
            input_column='game_data_until_now',
            target_column='player_message',
            num_train_epochs='10',
            per_device_train_batch_size='1',
            gradient_accumulation_steps='8',
            learning_rate='1e-4',
            output_dir='train_output_divided_to_turns_10_epochs'
        )
