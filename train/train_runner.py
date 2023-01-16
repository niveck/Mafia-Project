import os
import sys
import importlib

class TrainRunner:
    def __init__(self, train_config_path):
        train_config_path_parts = train_config_path.split('.')
        file_path_list = ['train_configs'] + train_config_path_parts[:-1]
        train_config_file_path = '.'.join(file_path_list)
        train_config_class_name = train_config_path_parts[-1]
        train_config_class = getattr(importlib.import_module(train_config_file_path), train_config_class_name)
        self.train_config = train_config_class()

    def run(self):
        inter_path = sys.executable
        exec_path = os.path.join('train', 'train.py')
        flags_str = self.train_config.generate_flags_str()
        cmd_to_run = inter_path + ' ' + exec_path + ' ' + flags_str
        print('Running command:')
        print(cmd_to_run)
        es = os.system(cmd_to_run)
        print('Got exit status ' + str(es))

config_path = sys.argv[1]
runner = TrainRunner(config_path)
runner.run()
