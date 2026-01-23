from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

import polars as pl
import os

def main():
    dataset_path = "../dataset/RecipeNLG/dataset/full_dataset.csv"
    df = pl.read_csv(dataset_path)
    embeddings = OllamaEmbeddings(model="qwen3-embedding")
    db_location = "./chroma_langchain_db"
    db_exist = os.path.exists(db_location)
    if not db_exist:
        documents = []
        ids = []
        for i,row in df.iter_rows():
            document = Document(
                page_content=f"{row[1]} {row[2]} {row[3]}",
                metadata={"source": f"recipe_{i}"}
            )


if __name__ == '__main__':
    main()