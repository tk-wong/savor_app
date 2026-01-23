import random

import polars as pl
import json

import tqdm


def main():
    dataset_path = "../dataset/RecipeNLG/dataset/full_dataset.csv"
    df = pl.read_csv(dataset_path)
    df = df.with_columns(
        pl.col("ingredients").str.json_decode(pl.List(pl.String)).alias("ingredients"),
        pl.col("directions").str.json_decode(pl.List(pl.String)).alias("directions"),
        pl.col("NER").str.json_decode(pl.List(pl.String)).alias("NER"),
    )
    print(f"data format (first 10):{df.head(10)}")
    print("Start sampling data...")
    seed = 42
    chosen_data = df['title', 'ingredients', 'directions','NER'].sample(5000,seed=seed)
    all_results = []
    for title, ingredients, directions,ner in chosen_data.iter_rows():
        user_prompt = f"create a recipe using {", ".join(ner)}."
        final_directions = ""
        for idx, step in enumerate(directions):
            final_directions += f"{idx+1}: {step}\n"
        model_response = \
            (f"Recipe title: {title}\nIngredients:\n{'\n'.join(ingredients)}\n"
             f"Directions:\n{final_directions}")
        all_results.append([
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": model_response}
        ])
    print("Writing results to sample_recipes.jsonl...")
    result_json = {
        "messages": all_results
    }
    with open("sample_recipes.jsonl", "w") as f:
        json.dump(result_json, f, indent=2)
    print("Done.")

if __name__ == '__main__':
    main()
