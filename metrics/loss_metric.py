from metrics.loss_per_token import extract_loss_per_token

def loss_metric(model, tokenizer, text):
    loss_list = extract_loss_per_token(model, tokenizer, text)
    return sum(loss_list)/len(loss_list)
