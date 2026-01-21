import random

import polars as pl
import json


def main():
    dataset_path = "../dataset/RecipeNLG/dataset/full_dataset.csv"
    df = pl.read_csv(dataset_path)
    seed = 42
    random.seed = seed
    chosen_data = df['title', 'ingredients', 'directions'].sample(3000,seed=seed).lazy()
    all_results = []
    for title, ingredients, directions in chosen_data.collect().iter_rows():

        processed_ingredients = ingredients.replace("[", "").replace("]", "").replace('"', '')
        ingredient_list = processed_ingredients.split(", ")
        processed_directions = directions.replace("[", "").replace("]", "").replace('"', '').split(", ")
        user_prompt = f"create a recipe using {", ".join(ingredient_list[:len(ingredient_list)//2])}."
        final_directions = ""
        for idx, step in enumerate(processed_directions):
            final_directions += f"{idx+1}: {step}\n"
        model_response = \
            (f"Recipe title: {title}\nIngredients:\n{processed_ingredients}\n"
             f"Directions:\n{final_directions}")
        all_results.append([
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": model_response}
        ])
    result_json = {
        "messages": all_results
    }
    with open("sample_recipes.jsonl", "w") as f:
        json.dump(result_json, f, indent=2)


if __name__ == '__main__':
    main()
