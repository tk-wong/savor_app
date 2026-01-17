import polars as pl
def main():
    dataset_path = "../dataset/RecipeNLG/dataset/full_dataset.csv"
    df = pl.read_csv(dataset_path)
    chosen_data = df['title', 'ingredients', 'directions'].sample(10000)

if __name__ == '__main__':
    main()