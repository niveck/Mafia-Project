from metrics.generate_outputs import generate_outputs
import torch

def calc_metrics(model, tokenizer, prefix, text, max_source_length, special_token_ids, model_name):
    outputs = generate_outputs(model, tokenizer, prefix, text, max_source_length, special_token_ids, model_name)

    # Loss
    loss = outputs.loss

    # Perplexity
    logits = outputs.logits[0, :, :]
    probs = torch.softmax(logits, dim=1)
    text_ids = tokenizer(text).input_ids[:-1]
    log_prob_sum = sum([torch.log(probs[i, text_ids[i]]) for i in range(len(text_ids))])
    log_perplexity = ((-1)/len(text_ids))*log_prob_sum
    perplexity = torch.exp(log_perplexity)

    return loss, perplexity
