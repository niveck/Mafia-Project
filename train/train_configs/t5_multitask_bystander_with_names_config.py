from train_configs.default_config import DefaultConfig

class SummTrialConfig(DefaultConfig):
    def __init__(self):
        super().__init__(
            train_file='bystanders_training_data_with_names',
            validation_file='bystanders_val_data_with_names',
            input_column='accumulated_messages',
            target_column='current_turn_player_message',
            num_train_epochs='5',
            per_device_train_batch_size='1',
            gradient_accumulation_steps='8',
            max_source_length='2048',
            max_target_length='64',
            val_max_target_length='128',
            learning_rate='1e-4'
        )
