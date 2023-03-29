def generate_outputs(model, tokenizer, prefix, text):
    prefix_ids = tokenizer(prefix, return_tensors="pt").input_ids
    text_ids = tokenizer(text, return_tensors="pt").input_ids[0, :]
    outputs = model(input_ids=prefix_ids, labels=text_ids)

    return outputs
