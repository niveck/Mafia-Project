import torch

def extract_loss_per_token(model, tokenizer, prefix, text):
    loss_list = []
    prefix_ids_list = tokenizer(prefix, return_tensors="pt").input_ids[0, :-1].tolist()
    text_ids_list = tokenizer(text, return_tensors="pt").input_ids[0, :].tolist()
    cur_ids_list = prefix_ids_list + [text_ids_list[0]]
    while len(cur_ids_list) < len(prefix_ids_list) + len(text_ids_list):
        cur_input_ids = torch.tensor([cur_ids_list])
        next_token = text_ids_list[len(cur_ids_list) - len(prefix_ids_list)]
        cur_labels = torch.tensor([[next_token]])
        outputs = model(input_ids=cur_input_ids, labels=cur_labels)
        loss = outputs.loss.item()
        loss_list.append(loss)
        cur_ids_list.append(next_token)

    return loss_list
