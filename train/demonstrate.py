from transformers import AutoConfig, AutoModelForSeq2SeqLM, AutoTokenizer

class Demonstrator:
    def __init__(self, model_path):
        self.model, self.tokenizer = self.load_model(model_path)

    def load_model(self, model_path):
        config = AutoConfig.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_path, config=config)
        
        return model, tokenizer

    def predict(self, input_text):
        inputs = self.tokenizer(input_text)
        return inputs
