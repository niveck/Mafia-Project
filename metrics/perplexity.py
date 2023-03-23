import torch
from metrics.loss_per_token import extract_loss_per_token

def perplexity(model, tokenizer, prefix, text):
    loss_list = extract_loss_per_token(model, tokenizer, prefix, text)
    text_prob = 1
    for loss in loss_list:
        text_prob *= loss
    perplexity = torch.pow(text_prob, (-1)/len(text))
    return perplexity
