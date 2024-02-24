from transformers import AutoConfig, AutoModelForSeq2SeqLM, AutoTokenizer
from csv import reader
from train.train import smart_truncation, add_special_tokens_to_tokenizer_and_get_ids
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
            # line == [0. i, 1. game_id, 2. player_name, 3. game_data_until_now, 4. player_message]
            if line[1] == game_id:
                res.append((line[3], line[4], line[2]))
    return res


class Demonstrator:
    def __init__(self, max_source_length, model_path=None, pretrained_model_name=None):
        self.max_source_length = max_source_length
        if model_path:
            self.model, self.tokenizer = self.load_model_from_path(model_path)
            with open(os.path.join(model_path, 'config.json'), 'r') as fp:
                train_config = json.load(fp)
                self.model_name = train_config['_name_or_path']
            with open(os.path.join(model_path, 'special_tokens_map.json'), 'r') as fp:
                added_tokens = json.load(fp)['additional_special_tokens']
                self.special_token_ids = [x
                                          for x in self.tokenizer(' '.join(added_tokens)).input_ids
                                          if self.tokenizer.decode(x) in added_tokens]
        elif pretrained_model_name:
            self.model_name = pretrained_model_name
            self.model, self.tokenizer, self.special_token_ids = \
                self.load_pretrained_model_from_name(pretrained_model_name)

        else:
            raise ValueError("Missing either model_path or pretrained_model_name")

    def load_model_from_path(self, model_path):
        config = AutoConfig.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_path, config=config)
        model.eval()
        
        return model, tokenizer

    def load_pretrained_model_from_name(self, pretrained_model_name):
        tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name)
        special_token_ids = add_special_tokens_to_tokenizer_and_get_ids(tokenizer)
        model = AutoModelForSeq2SeqLM.from_pretrained(pretrained_model_name)
        model.eval()

        return model, tokenizer, special_token_ids

    def predict(self, input_text):
        inputs = self.tokenizer(input_text, return_tensors="pt")
        inputs = {'input_ids': inputs.input_ids[0, :], 'attention_mask': inputs.attention_mask[0, :]}
        inputs = smart_truncation(inputs, self.max_source_length, self.special_token_ids, self.model_name)
        inputs = {'input_ids': torch.unsqueeze(inputs['input_ids'], 0), 'attention_mask': torch.unsqueeze(inputs['attention_mask'], 0)}
        outputs = self.model.generate(**inputs, num_beams=4)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
