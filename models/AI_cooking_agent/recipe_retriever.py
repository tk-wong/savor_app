import kagglehub
import psycopg

from langchain_core.documents import Document
from langchain_postgres import PGVector
from sqlalchemy_utils import database_exists, create_database
import polars as pl
from db_utils import drop_pgvector_collection, should_drop_tables


class RecipeRetriever:
    def __init__(self, app, dataset_name, csv_name, embeddings_model, database_path ,data_length=None):

        self.app = app
        self.embedding_model = embeddings_model
        self.dataset_name = dataset_name
        self.csv_name = csv_name
        self.data_length = data_length
        self.db_path = database_path

        created_database = False
        if not database_exists(self.db_path):
            self.app.logger.info("Database does not exist yet. Creating database...")
            create_database(self.db_path)
            created_database = True

        # Drop vector collection if needed for integration testing
        if should_drop_tables():
            self.app.logger.info("DROP_TABLES_ON_INIT is enabled. Dropping vector collections...")
            try:
                db_connection = psycopg.connect(conninfo=self.db_path, autocommit=True)
                drop_pgvector_collection(db_connection, "recipes")
                db_connection.close()
            except Exception as e:
                self.app.logger.error(f"Error dropping vector collection: {e}")

        self.vector_db = PGVector(
            collection_name="recipes",
            embeddings=self.embedding_model,
            connection=self.db_path,
            use_jsonb=True,
        )
        if created_database or should_drop_tables():
            self.create_embeddings()
        self.retriever = self.vector_db.as_retriever(search_kwargs={"k": 5})

    def create_embeddings(self):
        self.app.logger.info("Loading dataset and creating embeddings...")
        lazy_df = kagglehub.dataset_load(
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
