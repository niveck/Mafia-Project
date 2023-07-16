from train_configs.default_config import DefaultConfig

class T5MultitaskBystanderWithNamesConfig(DefaultConfig):
    def __init__(self):
        super().__init__(
            train_file='bystanders_training_data_with_names.csv',
            validation_file='bystanders_val_data_with_names.csv',
            input_column='accumulated_messages',
            target_column='current_turn_player_message',
            num_train_epochs='5',
            per_device_train_batch_size='1',
            gradient_accumulation_steps='8',
            learning_rate='1e-4',
            output_dir='train_output_bystander_names'
        )
