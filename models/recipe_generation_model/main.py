

from transformers import AutoModelForCausalLM, AutoTokenizer


# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def main():

    # model_name = "unsloth/Qwen3-4B-unsloth-bnb-4bit"  # path to the fine-tuned model_name

    # model_name = "./qwen3-4b-finetuned-recipes"  # path to the fine-tuned model
    model_name = "Qwen/Qwen3-4B"  # base model
    # load the tokenizer and the model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        dtype="auto",
        device_map="auto"
    )

    # prepare the model input
    prompt = ('You are a professional chef and trying to teach a beginner to cook. '
              'Please state the detailed portions of all ingredients In Ingredients section, '
              'add more ingredients and seasonings with portions if needed, '
              ' and detailed instructions required for the recipe in Directions section.'
              'Please create a recipe using eggs, milk, and chicken.'
              )
    print(prompt)
    generate_response(model, prompt, tokenizer)
    # generate_response(model, "How to make Chicken And Egg Casserole", tokenizer)


def generate_response(model, prompt, tokenizer):
    messages = [
        {"role": "user", "content": prompt}
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    # conduct text completion
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=32768
    )
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
    # parsing thinking content
    try:
        # rindex finding 151668 (</think>)
        index = len(output_ids) - output_ids[::-1].index(151668)
    except ValueError:
        index = 0
    thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
    content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")
    print("thinking content:", thinking_content)  # no opening <think> tag
    print("content:\n", content)


if __name__ == "__main__":
    main()
    