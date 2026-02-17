import logging
from dotenv import load_dotenv
import os

import kagglehub

from langchain_core.documents import Document
from langchain_postgres import PGVector
from sqlalchemy_utils import database_exists, create_database
import polars as pl


class RecipeRetriever:
    def __init__(self, app,env_path, dataset_name, csv_name, embeddings_model, data_length=None):
        load_dotenv(env_path)
        self.app = app
        self.embedding_model = embeddings_model
        self.dataset_name = dataset_name
        self.csv_name = csv_name
        self.data_length = data_length
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_NAME")
        self.db_path = f"postgresql+psycopg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        self.vector_db = PGVector(
            collection_name="recipes",
            embeddings=self.embedding_model,
            connection=self.db_path,
            use_jsonb=True,
        )
        if not database_exists(self.db_path):
            create_database(self.db_path)
            self.create_embeddings()
        self.retriever = self.vector_db.as_retriever(search_kwargs={"k": 5})

    def create_embeddings(self):
        self.app.logger.info("Loading dataset and creating embeddings...")
        lazy_df = kagglehub.load_dataset(
                kagglehub.KaggleDatasetAdapter.POLARS,
                self.dataset_name,
                self.csv_name,

                )
        # path = kagglehub.dataset_download(self.dataset_name, "RecipeNLG_dataset.csv")
        df = lazy_df.with_columns(
            pl.col("ingredients").str.json_decode(
                pl.List(pl.String)).alias("ingredients"),
            pl.col("directions").str.json_decode(
                pl.List(pl.String)).alias("directions"),
        )
        
        index_df = df.with_row_index(name="index")
        if self.data_length:
            index_df = index_df.head(self.data_length)
        documents = []
        ids = []
        self.app.logger.info("Creating documents and adding to vector database...")
        for row in index_df.collect(engine="streaming").iter_rows(named=True):
            format_ingredient = "\n".join(row["ingredients"])
            format_directions = '\n'.join(
                [f"Step {idx + 1}: {step}" for idx, step in enumerate(row["directions"])])
            page_content = f"Title: {row['title']}\nIngredients:\n{format_ingredient}\nDirections:\n{format_directions}"
            document = Document(
                page_content=page_content,
                metadata={
                    'recipe_title': row['title'],
                    # 'recipe_id': str(row["index"])
                },
                id=str(row["index"]),
            )
            ids.append(str(row["index"]))
            documents.append(document)
        self.app.logger.info(f"Adding {len(documents)} documents to the vector database...")
        self.vector_db.add_documents(documents=documents, ids=ids)
        self.app.logger.info("Finished adding documents to the vector database.")

    def get_retriever(self):
        return self.retriever
