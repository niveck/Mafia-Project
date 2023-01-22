from train_configs.train_config import TrainConfig

class DefaultConfig(TrainConfig):
    def __init__(self,
        dataset_name=None,
        dataset_config_name=None,
        input_column=None,
        target_column=None,
        train_file=None,
        validation_file=None,
        test_file=None,
        max_train_samples=None,
        max_eval_samples=None,
        max_predict_samples=None,
        num_train_epochs=None,
        learning_rate=None,
        per_device_train_batch_size=None,
        gradient_accumulation_steps=None
        ):
        super().__init__(
            dataset_name=dataset_name,
            dataset_config_name=dataset_config_name,
            input_column=input_column,
            target_column=target_column,
            train_file=train_file,
            validation_file=validation_file,
            test_file=test_file,
            max_train_samples=max_train_samples,
            max_eval_samples=max_eval_samples,
            max_predict_samples=max_predict_samples,
            cache_dir='hf_cache',
            max_source_length='1024',
            max_target_length='64',
            val_max_target_length='128',
            num_beams='3',
            num_train_epochs=num_train_epochs,
            learning_rate=learning_rate,
            per_device_train_batch_size=per_device_train_batch_size,
            gradient_accumulation_steps=gradient_accumulation_steps
        )
