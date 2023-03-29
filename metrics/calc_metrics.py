from metrics.generate_outputs import generate_outputs
import torch

def calc_metrics(model, tokenizer, prefix, text):
    outputs = generate_outputs(model, tokenizer, prefix, text)

    # Loss
    loss = outputs.loss

    # Perplexity
    logits = outputs.logits[0, :, :]
    probs = torch.softmax(logits, dim=1)
    text_ids = tokenizer(text).input_ids[:-1]
    seq_prob = 1
    cur_ind = 0
    while cur_ind < len(text_ids):
        cur_id = text_ids[cur_ind]
        seq_prob *= probs[cur_ind, cur_id]
        cur_ind += 1
    perplexity = (1/seq_prob)**(1/len(text_ids))

    return loss, perplexity
