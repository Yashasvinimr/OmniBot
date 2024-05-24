from flask import Flask, render_template, jsonify, request
import os
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    HfArgumentParser,
    TrainingArguments,
    pipeline,
    logging,
)
from peft import LoraConfig, PeftModel
import re

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template("index.html")

################################################################################
# QLoRA parameters
################################################################################

# LoRA attention dimension
lora_r = 64

# Alpha parameter for LoRA scaling
lora_alpha = 16

# Dropout probability for LoRA layers
lora_dropout = 0.1

################################################################################
# bitsandbytes parameters
################################################################################

# Activate 4-bit precision base model loading
use_4bit = True

# Compute dtype for 4-bit base models
bnb_4bit_compute_dtype = "float16"

# Quantization type (fp4 or nf4)
bnb_4bit_quant_type = "nf4"

# Activate nested quantization for 4-bit base models (double quantization)
use_nested_quant = False

################################################################################
# TrainingArguments parameters
################################################################################

# Output directory where the model predictions and checkpoints will be stored
output_dir = "./results"

# Number of training epochs
num_train_epochs = 1

# Enable fp16/bf16 training (set bf16 to True with an A100)
fp16 = False
bf16 = False

# Batch size per GPU for training
per_device_train_batch_size = 4

# Batch size per GPU for evaluation
per_device_eval_batch_size = 4

# Number of update steps to accumulate the gradients for
gradient_accumulation_steps = 1

# Enable gradient checkpointing
gradient_checkpointing = True

# Maximum gradient normal (gradient clipping)
max_grad_norm = 0.3

# Initial learning rate (AdamW optimizer)
learning_rate = 2e-4

# Weight decay to apply to all layers except bias/LayerNorm weights
weight_decay = 0.001

# Optimizer to use
optim = "paged_adamw_32bit"

# Learning rate schedule
lr_scheduler_type = "cosine"

# Number of training steps (overrides num_train_epochs)
max_steps = -1

# Ratio of steps for a linear warmup (from 0 to learning rate)
warmup_ratio = 0.03

# Group sequences into batches with same length
# Saves memory and speeds up training considerably
group_by_length = True

# Save checkpoint every X updates steps
save_steps = 0

# Log every X updates steps
logging_steps = 25

################################################################################
# SFT parameters
################################################################################

# Maximum sequence length to use
max_seq_length = None

# Pack multiple short examples in the same input sequence to increase efficiency
packing = False

# Load the entire model on the GPU 0
device_map = {"": 0}

conversation_history = []

def remove_text_between(string, start_marker, end_marker):
    # Create a regex pattern to match text between start and end markers
    pattern = re.escape(start_marker) + r'.*?' + re.escape(end_marker)

    # Use re.sub to replace the matched pattern with an empty string
    cleaned_string = re.sub(pattern, '', string)

    return cleaned_string

# Generate text function
def generate_text(tokenizer, model, prompt, max_length=200, max_new_tokens=50, num_return_sequences=1):

    # prev_history = " ".join(conversation_history)
    # conversation_history.append(prompt)
    conversation_history.append(f"[USER]: {prompt}")


    combined_input = " ".join(conversation_history)

    logging.set_verbosity(logging.CRITICAL)

    # Run text generation pipeline with our next model
    pipe = pipeline(task="text-generation", model=model, tokenizer=tokenizer, max_length=max_length, truncation=True, max_new_tokens=max_new_tokens)
    result = pipe(f"<s>[INST] {combined_input} [/INST]")

    generated_text = result[0]['generated_text']



    # Extract the new response from the generated text
    # response_start = generated_text.find(f"{prompt}") + len(f"{prompt}")
    response_start = generated_text.find(f"[USER]: {prompt}") + len(f"[USER]: {prompt}")


    response = generated_text[response_start:].strip()


    #dynamically increase text generated based on whether or not a sentence has completed
    last_sentence_end = max(response.rfind('.'), response.rfind('!'), response.rfind('?'))
    if last_sentence_end != -1:
        # Truncate the text at the last sentence end punctuation
        response = response[:last_sentence_end + 1]
    else:
        # If no sentence end punctuation is found, just truncate at max_length
        response = response[:max_length]

    # remove unneeded part of the generated text
    # response = remove_text_between(response, "<s>", "[/INST]")

    # Add the new response to the conversation history
    # conversation_history.append(f"{response}")
    conversation_history.append(f"[AI]: {response}")



    # response = response.replace("[/INST]", "")


    return response

# LOAD THE MODEL

def load_model(model_name):
    # compute_dtype = getattr(torch, bnb_4bit_compute_dtype)

    # bnb_config = BitsAndBytesConfig(
    #     load_in_4bit=use_4bit,
    #     bnb_4bit_quant_type=bnb_4bit_quant_type,
    #     bnb_4bit_compute_dtype=compute_dtype,
    #     bnb_4bit_use_double_quant=use_nested_quant,
    # )

    # Check GPU compatibility with bfloat16
    # if compute_dtype == torch.float16 and use_4bit:
        # major, _ = torch.cuda.get_device_capability()
        # if major >= 8:
        #     print("=" * 80)
        #     print("Your GPU supports bfloat16: accelerate training with bf16=True")
        #     print("=" * 80)

    # Load base model
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        # quantization_config=bnb_config,
        device_map=device_map
    )
    model.config.use_cache = False
    model.config.pretraining_tp = 1

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    return tokenizer, model

model_name2 = "hidingbehindrainbows/Llama-2-7b-chat-finetune"
to, mo = load_model(model_name2)

# while True:
#   input_text = input("What is your prompt?\n")
#   generated_text = generate_text(to, mo, input_text)
#   print(generated_text)  # This print can be removed, it's just for checking the output


@app.route("/api", methods=["GET", "POST"])
def qa():
    while True:
        if request.method=="POST":
            print(request.json )
            question = request.json.get("question")
            generated_text = generate_text(to, mo, question)

            data = {"result":f"{generated_text}"}
            return jsonify(data)
        data={"result":"Thank you! I'm just a machine learning model designed to respond to the questions and generate text based model"}
        return jsonify(data)
app.run(debug=True)


