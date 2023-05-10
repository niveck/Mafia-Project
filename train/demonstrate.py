from transformers import AutoConfig, AutoModelForSeq2SeqLM, AutoTokenizer
from csv import reader
from train.train import smart_truncation
import json
import os
import torch

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
        with open(os.path.join(model_path, 'special_tokens_map.json'), 'r') as fp:
            added_tokens = json.load(fp)['additional_special_tokens']
            self.special_token_ids = [x for x in self.tokenizer(' '.join(added_tokens)).input_ids if self.tokenizer.decode(x) in added_tokens]

    def load_model(self, model_path):
        config = AutoConfig.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_path, config=config)
        model.eval()
        
        return model, tokenizer

    def predict(self, input_text):
        inputs = self.tokenizer(input_text, return_tensors="pt")
        inputs = {'input_ids': inputs.input_ids[0, :], 'attention_mask': inputs.attention_mask[0, :]}
        inputs = smart_truncation(inputs, self.max_source_length, self.special_token_ids, self.model_name)
        inputs = {'input_ids': torch.unsqueeze(inputs['input_ids'], 0), 'attention_mask': torch.unsqueeze(inputs['attention_mask'], 0)}
        outputs = self.model.generate(**inputs, num_beams=4)  # , num_return_sequence=1)  # TODO: remove this if unnecessary
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
