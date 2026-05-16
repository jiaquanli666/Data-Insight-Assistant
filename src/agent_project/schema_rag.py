"""
RAG module for database schema + query example retrieval.
Uses DashScope for embeddings and Chroma as the vector store.
"""
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from agent_project.config import DASHSCOPE_API_KEY, EMBEDDING_MODEL, CHROMA_PERSIST_DIR
from agent_project.database import SCHEMA_DOC, QUERY_EXAMPLES

COLLECTION_NAME = "schema_rag"


def _build_documents() -> list[Document]:
    docs: list[Document] = []

    # Schema doc as one document
    docs.append(Document(
        page_content=SCHEMA_DOC.strip(),
        metadata={"type": "schema", "source": "database_schema"}
    ))

    # Each query example as a separate document
    for line in QUERY_EXAMPLES.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("示例"):
            current_example = line
        elif line.startswith("SQL:"):
            docs.append(Document(
                page_content=current_example + "\n" + line,
                metadata={"type": "query_example"}
            ))

    return docs


def create_vector_store() -> Chroma:
    embeddings = DashScopeEmbeddings(
        dashscope_api_key=DASHSCOPE_API_KEY,
        model=EMBEDDING_MODEL,
    )
    docs = _build_documents()

    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PERSIST_DIR,
    )
    return vectorstore


def load_vector_store() -> Chroma:
    embeddings = DashScopeEmbeddings(
        dashscope_api_key=DASHSCOPE_API_KEY,
        model=EMBEDDING_MODEL,
    )
    return Chroma(
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PERSIST_DIR,
    )


def get_vector_store() -> Chroma:
    """Get vector store, creating it if it doesn't exist."""
    try:
        return load_vector_store()
    except Exception:
        return create_vector_store()


def retrieve_schema_context(query: str, k: int = 3) -> str:
    """Retrieve relevant schema / query-example context for a user question."""
    vs = get_vector_store()
    docs = vs.similarity_search(query, k=k)
    return "\n\n---\n\n".join(d.page_content for d in docs)


if __name__ == "__main__":
    vs = create_vector_store()
    print(f"Vector store created with {vs._collection.count()} documents")
    result = retrieve_schema_context("上个月哪个品类卖得最好")
    print("=== Retrieved context ===")
    print(result)
