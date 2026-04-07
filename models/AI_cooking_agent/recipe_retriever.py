import kagglehub
import psycopg

from langchain_core.documents import Document
from langchain_postgres import PGVector
from sqlalchemy_utils import database_exists, create_database
import polars as pl
from db_utils import drop_pgvector_collection, should_drop_tables


class RecipeRetriever:
    def __init__(self, app, dataset_name, csv_name, embeddings_model, database_path, data_length=None):

        self.app = app
        self.embedding_model = embeddings_model
        self.dataset_name = dataset_name
        self.csv_name = csv_name
        self.data_length = data_length
        self.db_path = database_path

        self.app.logger.info(
            "[Init Step 1/8] RecipeRetriever initialization started.")
        self.app.logger.info(
            f"[Init Step 2/8] Configuration loaded: dataset={self.dataset_name}, csv={self.csv_name}, data_length={self.data_length}"
        )

        created_database = False
        self.app.logger.info(
            "[Init Step 3/8] Checking whether the target database exists...")
        if not database_exists(self.db_path):
            self.app.logger.info(
                "Database does not exist yet. Creating database...")
            create_database(self.db_path)
            created_database = True
            self.app.logger.info(
                "[Init Step 3/8] Database created successfully.")
        else:
            self.app.logger.info("[Init Step 3/8] Database already exists.")

        # Drop vector collection if needed for integration testing
        self.app.logger.info(
            "[Init Step 4/8] Checking DROP_TABLES_ON_INIT setting...")
        if should_drop_tables():
            self.app.logger.info(
                "DROP_TABLES_ON_INIT is enabled. Dropping vector collections...")
            try:
                db_connection = psycopg.connect(
                    conninfo=self.db_path, autocommit=True)
                drop_pgvector_collection(db_connection, "recipes")
                db_connection.close()
                self.app.logger.info(
                    "[Init Step 4/8] Vector collection drop completed.")
            except Exception as e:
                self.app.logger.error(f"Error dropping vector collection: {e}")
        else:
            self.app.logger.info(
                "[Init Step 4/8] DROP_TABLES_ON_INIT disabled. Keeping existing vector collections.")

        self.app.logger.info("[Init Step 5/8] Initializing PGVector client...")
        self.vector_db = PGVector(
            collection_name="recipes",
            embeddings=self.embedding_model,
            connection=self.db_path,
            use_jsonb=True,
        )

        self.app.logger.info(
            "[Init Step 6/8] Determining whether vector embeddings need to be rebuilt...")
        should_rebuild = created_database or should_drop_tables(
        ) or not self._collection_exists("recipes")
        if should_rebuild:
            self.app.logger.info(
                "Vector collection missing. Loading dataset into vector DB before API startup...")
            self.app.logger.info(
                "[Init Step 7/8] Triggering embedding creation...")
            self.create_embeddings()
        else:
            self.app.logger.info(
                "[Init Step 7/8] Existing vector collection found. Skipping embedding rebuild.")

        self.app.logger.info("[Init Step 8/8] Creating retriever interface...")
        self.retriever = self.vector_db.as_retriever(search_kwargs={"k": 5})
        self.app.logger.info("RecipeRetriever initialization completed.")

    def _collection_exists(self, collection_name: str) -> bool:
        """Return True when the pgvector collection metadata row exists."""
        self.app.logger.info(
            f"Checking collection existence for '{collection_name}'...")
        try:
            with psycopg.connect(conninfo=self.db_path) as db_connection:
                with db_connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT 1 FROM langchain_pg_collection WHERE name = %s LIMIT 1;",
                        (collection_name,),
                    )
                    exists = cursor.fetchone() is not None
                    self.app.logger.info(
                        f"Collection existence check complete for '{collection_name}': exists={exists}"
                    )
                    return exists
        except Exception as e:
            self.app.logger.info(
                f"Could not verify vector collection state: {e}")
            return False

    def create_embeddings(self):
        self.app.logger.info(
            "[Embedding Step 1/6] Loading dataset from Kaggle...")
        lazy_df = kagglehub.dataset_load(
            kagglehub.KaggleDatasetAdapter.POLARS,
            self.dataset_name,
            self.csv_name,
        )
        self.app.logger.info(
            "[Embedding Step 2/6] Decoding ingredients and directions JSON columns...")
        # path = kagglehub.dataset_download(self.dataset_name, "RecipeNLG_dataset.csv")
        df = lazy_df.with_columns(
            pl.col("ingredients").str.json_decode(
                pl.List(pl.String)).alias("ingredients"),
            pl.col("directions").str.json_decode(
                pl.List(pl.String)).alias("directions"),
        )

        self.app.logger.info(
            "[Embedding Step 3/6] Creating row index for stable document IDs...")
        index_df = df.with_row_index(name="index")
        if self.data_length:
            self.app.logger.info(
                f"[Embedding Step 4/6] Applying data length limit: first {self.data_length} rows."
            )
            index_df = index_df.head(self.data_length)
        else:
            self.app.logger.info(
                "[Embedding Step 4/6] No data length limit provided. Using full dataset.")
        documents = []
        ids = []
        self.app.logger.info(
            "[Embedding Step 5/6] Building document objects from dataset rows...")
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
        self.app.logger.info(
            f"[Embedding Step 6/6] Adding {len(documents)} documents to the vector database..."
        )
        self.vector_db.add_documents(documents=documents, ids=ids)
        self.app.logger.info(
            "Finished adding documents to the vector database.")

    def get_retriever(self):
        self.app.logger.info("Returning configured retriever instance.")
        return self.retriever
