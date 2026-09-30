import logging
import os

from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_qdrant import Qdrant
from langchain_text_splitters import CharacterTextSplitter
from qdrant_client import AsyncQdrantClient, QdrantClient
from qdrant_client.models import Distance, VectorParams

logger = logging.getLogger(__name__)

embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "shipping_knowledge_base"


async def init_vector_store() -> None:
    client = QdrantClient(url=QDRANT_URL, check_compatibility=False)

    if client.collection_exists(collection_name=COLLECTION_NAME):
        logger.info(
            f"Векторная коллекция '{COLLECTION_NAME}' уже существует. "
            "Пропускаем инициализацию."
        )
        return

    logger.info("Векторная коллекция не найдена. Начинаем индексацию базы знаний...")

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

    kb_path = os.path.join(os.getcwd(), "knowledge_base.txt")
    if not os.path.exists(kb_path):
        logger.error(f"Файл базы знаний не найден по пути: {kb_path}")
        return

    with open(kb_path, "r", encoding="utf-8") as f:
        text = f.read()

    text_splitter = CharacterTextSplitter(
        separator="\n\n", chunk_size=400, chunk_overlap=0
    )
    docs = text_splitter.create_documents([text])

    Qdrant.from_documents(
        documents=docs,
        embedding=embeddings,
        url=QDRANT_URL,
        collection_name=COLLECTION_NAME,
    )

    logger.info(f"База знаний успешно векторизована! Загружено чанков: {len(docs)}")


async def search_knowledge_base(query: str) -> str:
    async_client = AsyncQdrantClient(url=QDRANT_URL, check_compatibility=False)
    query_vector = embeddings.embed_query(query)

    response = await async_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=3,
        with_payload=True,
    )

    chunks = []
    for point in response.points:
        if point.payload and "page_content" in point.payload:
            chunks.append(str(point.payload["page_content"]))

    if not chunks:
        return ""

    return "\n".join(chunks)
