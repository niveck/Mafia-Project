from transformers import AutoConfig, AutoModelForSeq2SeqLM, AutoTokenizer
from csv import reader
from train.train import smart_truncation
import json
import os

def load_dataset_from_csv(path):
    res = []
    with open(path, 'r') as fp:
        my_reader = reader(fp)
        first = True
        for line in my_reader:
            if first:
                first = False
                continue
            res.append((line[3], line[4], line[2]))

    return res

def load_game_from_csv(path, game_id):
    res = []
    with open(path, 'r') as fp:
        my_reader = reader(fp)
        first = True
        for line in my_reader:
            if first:
                first = False
                continue
            if line[1] == game_id:
                res.append((line[3], line[4], line[2]))

    return res

class Demonstrator:
    def __init__(self, model_path, max_source_length):
        self.model, self.tokenizer, = self.load_model(model_path)
        with open(os.path.join(model_path, 'config.json'), 'r') as fp:
            train_config = json.load(fp)
            self.model_name = train_config['_name_or_path']
        self.max_source_length = max_source_length
        with open(os.path.join(model_path, 'added_tokens.json'), 'r') as fp:
            added_tokens = json.load(fp)
            self.special_token_ids = list(added_tokens.values())

    def load_model(self, model_path):
        config = AutoConfig.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_path, config=config)
        
        return model, tokenizer

    def predict(self, input_text):
        inputs = self.tokenizer(input_text, return_tensors="pt")
        inputs = smart_truncation(inputs, self.max_source_length, self.special_token_ids, self.model_name)
        outputs = self.model.generate(**inputs)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
