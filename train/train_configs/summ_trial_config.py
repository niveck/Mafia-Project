from train_configs.default_config import DefaultConfig

class SummTrialConfig(DefaultConfig):
    def __init__(self):
        super().__init__(
            dataset_name='cnn_dailymail',
            dataset_config_name='3.0.0',
            input_column='article',
            target_column='highlights',
            max_train_samples='100',
            max_eval_samples='100',
            max_predict_samples='100',
            num_train_epochs='1',
            per_device_train_batch_size='1',
            gradient_accumulation_steps='8'
        )
