from train.train_configs.default_config import DefaultConfig


class T5MultitaskBystanderDividedToTurnsWith2PassConfig(DefaultConfig):
    def __init__(self):
        super().__init__(
            train_file='training_data/training_without_votes_divided_to_turns_with_2_pass_july_2023/train_data.csv',
            validation_file='training_data/training_without_votes_divided_to_turns_with_2_pass_july_2023/validation_data.csv',
            input_column='game_data_until_now',
            target_column='player_message',
            num_train_epochs='10',
            per_device_train_batch_size='64',
            gradient_accumulation_steps='8',
            learning_rate='1e-4',
            output_dir='train_output_divided_to_turns_with_2_pass'
        )
