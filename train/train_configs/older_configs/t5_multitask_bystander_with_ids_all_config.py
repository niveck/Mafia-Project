from train_configs.default_config import DefaultConfig

class T5MultitaskBystanderWithIdsAllConfig(DefaultConfig):
    def __init__(self):
        super().__init__(
            train_file='training_data/training_by_all_data_with_or_without_votes_february_2023/train_data_without_votes_with_ids.csv',
            validation_file='training_data/training_by_all_data_with_or_without_votes_february_2023/validation_data_without_votes_with_ids.csv',
            input_column='accumulated_messages',
            target_column='current_turn_player_message',
            num_train_epochs='5',
            per_device_train_batch_size='1',
            gradient_accumulation_steps='8',
            learning_rate='1e-4',
            output_dir='train_output_bystander_ids'
        )
