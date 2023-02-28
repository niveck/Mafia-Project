class TrainConfig:

    def __init__(self,
        model_name_or_path='t5-large',
        cache_dir=None,
        dataset_name=None,
        dataset_config_name=None,
        input_column=None,
        target_column=None,
        train_file=None,
        validation_file=None,
        test_file=None,
        max_source_length=None,
        max_target_length=None,
        val_max_target_length=None,
        max_train_samples=None,
        max_eval_samples=None,
        max_predict_samples=None,
        num_beams=None,
        learning_rate=None,
        output_dir='train_output',
        num_train_epochs='5',
        per_device_train_batch_size='64',
        gradient_accumulation_steps='1',
        do_train='True',
        do_eval='False',
        predict_with_generate='True'
    ):
        self.model_name_or_path = model_name_or_path
        self.cache_dir = cache_dir
        self.dataset_name = dataset_name
        self.dataset_config_name = dataset_config_name
        self.input_column = input_column
        self.target_column = target_column
        self.train_file = train_file
        self.validation_file = validation_file
        self.test_file = test_file
        self.max_source_length = max_source_length
        self.max_target_length = max_target_length
        self.val_max_target_length = val_max_target_length
        self.max_train_samples = max_train_samples
        self.max_eval_samples = max_eval_samples
        self.max_predict_samples = max_predict_samples
        self.output_dir = output_dir
        self.num_beams = num_beams
        self.learning_rate = learning_rate
        if num_train_epochs is None:
            num_train_epochs = '5'
        if per_device_train_batch_size is None:
            per_device_train_batch_size = '64'
        if gradient_accumulation_steps is None:
            gradient_accumulation_steps = '1'
        self.num_train_epochs = num_train_epochs
        self.per_device_train_batch_size = per_device_train_batch_size
        self.gradient_accumulation_steps = gradient_accumulation_steps
        self.do_train = do_train
        self.do_eval = do_eval
        self.predict_with_generate = predict_with_generate
        
        assert input_column is not None, 'ERROR: please provide input column'
        assert target_column is not None, 'ERROR: please provide target column'

    def generate_flags_str(self):
        property_dict = vars(self)
        relevant_props = [x for x in property_dict.items() if x[1] is not None]

        res = ' '.join(['--' + x[0] + ' ' + x[1] for x in relevant_props])

        return res
