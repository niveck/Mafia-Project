from train.train import smart_truncation
import torch

def generate_outputs(model, tokenizer, prefix, text, max_source_length, special_token_ids, model_name):
    inputs = tokenizer(prefix, return_tensors="pt")
    inputs = {'input_ids': inputs.input_ids[0, :], 'attention_mask': inputs.attention_mask[0, :]}
    inputs = smart_truncation(inputs, max_source_length, special_token_ids, model_name)
    inputs = {'input_ids': torch.unsqueeze(inputs['input_ids'], 0), 'attention_mask': torch.unsqueeze(inputs['attention_mask'], 0)}
    prefix_ids = inputs.input_ids
    text_ids = tokenizer(text, return_tensors="pt").input_ids
    outputs = model(input_ids=prefix_ids, labels=text_ids)

    return outputs
