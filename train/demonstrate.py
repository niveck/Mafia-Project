from transformers import AutoConfig, AutoModelForSeq2SeqLM, AutoTokenizer
from csv import reader

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
                res.append((line[3], line[4]))

    return res

class Demonstrator:
    def __init__(self, model_path):
        self.model, self.tokenizer = self.load_model(model_path)

    def load_model(self, model_path):
        config = AutoConfig.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_path, config=config)
        
        return model, tokenizer

    def predict(self, input_text):
        input_ids = self.tokenizer(input_text, return_tensors="pt").input_ids
        outputs = self.model.generate(input_ids)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
