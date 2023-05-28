import streamlit as st
from transformers import AutoTokenizer, AutoModelWithLMHead
import torch

# Load the fine-tuned model
model_name = 'gpt2'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelWithLMHead.from_pretrained(model_name)

# Set maximum length for generated text
max_length = 100

# Streamlit app header
st.title("Language Model Interface")

# List to store former messages
message_history = []

# Text input box
input_text = st.text_area("Enter your input text here", "")

# Add input text to message history
if st.button("Send"):
    message_history.append(input_text)

    # Tokenize the input text
    input_ids = tokenizer.encode(input_text, return_tensors='pt')

    # Generate text from the model
    output = model.generate(input_ids, max_length=max_length, num_return_sequences=1)
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)

    # Add generated text to message history
    message_history.append(generated_text)

# Display message history
st.text("Message History:")
for message in message_history:
    st.text(message)

print(message_history)