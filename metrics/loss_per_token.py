import torch

def extract_loss_per_token(model, tokenizer, text):
    cur_ids_list = []
    loss_list = []
    all_input_ids = tokenizer(text, return_tensors="pt").input_ids
    while len(cur_ids_list) < all_input_ids.shape[1]:
        cur_input_ids = torch.tensor([cur_ids_list])
        next_token = all_input_ids[0, len(cur_ids_list)].item()
        cur_labels = torch.tensor([next_token])
        outputs = model(input_ids=cur_input_ids, labels=cur_labels)
        loss = outputs.loss.item()
        loss_list.append(loss)
        cur_ids_list.append(next_token)

    return loss_list
