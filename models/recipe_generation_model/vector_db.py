import tqdm
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_postgres import PGVector
from dotenv import load_dotenv
import polars as pl
import os


load_dotenv("./.env_dev")

db_user  = os.getenv("DB_USER")
db_password  = os.getenv("DB_PASSWORD")
db_host  = os.getenv("DB_HOST")
db_port  = os.getenv("DB_PORT")
db_name  = os.getenv("DB_NAME")
db_path = f"postgresql+psycopg://{db_user}:{db_password}@{db_host}:{db_port}"


dataset_path = "../dataset/RecipeNLG/dataset/full_dataset.csv"
df = pl.read_csv(dataset_path).head(1000)
df = df.with_columns(
    pl.col("ingredients").str.json_decode(pl.List(pl.String)).alias("ingredients"),
    pl.col("directions").str.json_decode(pl.List(pl.String)).alias("directions"),
    # pl.col("NER").str.json_decode(pl.List(pl.String)).alias("NER"),
)
embeddings = OllamaEmbeddings(model="qwen3-embedding:0.6b")
db_location = "./chroma_langchain_db"
db_exist = False
# db_exist = os.path.exists(db_location)
vector_db = PGVector(
    collection_name="recipes",
    embeddings=embeddings,
    connection=db_path,
    use_jsonb=True,
)
if not db_exist:
    documents = []
    ids = []
    indexed_df = df.with_row_index(name="index")
    for row in tqdm.tqdm(indexed_df.iter_rows(named=True), total=indexed_df.height, desc="Processing rows"):
        format_ingredient = "\n".join(row["ingredients"])
        format_directions = '\n'.join([f"Step {idx + 1}: {step}" for idx, step in enumerate(row["directions"])])
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
    vector_db.add_documents(documents=documents, ids=ids)

retriever = vector_db.as_retriever(search_type="similarity", search_kwargs={"k": 5})

# result = vector_db.similarity_search(
#     query="eggs, milk, flour",
#     k=5,
# )
# for doc in result:
#     print(f"Content: {doc.page_content}\n")




