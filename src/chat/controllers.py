from pymongo.synchronous.collection import Collection
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

snow_stem = SnowballStemmer(language="english")


async def get_last_questions(collection: Collection, id: str, limit=15) -> dict:
    """
    Retrieve the last questions from a specified collection based on ID.

    Args:
        collection (Collection): MongoDB collection object to query from
        id (str): Unique identifier to search for in the collection
        limit (int, optional): Maximum number of results to return. Defaults to 15

    Returns:
        dict: Dictionary containing the matched document from the collection
    """
    chat = collection.find({"_id": id}).limit(limit=limit).to_list()
    return chat[0] if chat else []


async def get_chat_history(collection: Collection, id: str) -> dict:
    """
    Args:
        collection (Collection): MongoDB collection object to query from
        id (str): Unique identifier to search for in the collection

    Returns:
        dict: Chat history document if found, empty list if not found
    """
    chat = collection.find({"_id": id}).to_list()
    return chat[0] if chat else []


async def top_k(arr, k) -> np.array:
    """
    Args:
        arr: Array-like input to find top k indices
        k (int): Number of top values to return

    Returns:
        np.array: Indices of top k values in descending order
    """
    kth_largest = (k + 1) * -1
    return np.argsort(arr)[:kth_largest:-1]


async def get_context(
    corpus: list[str],
    query: str,
    max_results: int = 5,
    similarity_threshold: float = 0.1,
) -> list[str]:
    """
    Args:
        corpus (list[str]): List of documents to search through
        query (str): Query string to find similar documents
        max_results (int, optional): Maximum number of results to return. Defaults to 5
        similarity_threshold (float, optional): Minimum similarity score required. Defaults to 0.1

    Returns:
        list[str]: List of documents from corpus that match the query above the similarity threshold
    """
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(corpus)
    user_query_tfidf = vectorizer.transform([query])
    cosine_similarities = cosine_similarity(X, user_query_tfidf).flatten()
    top_related_indices = await top_k(cosine_similarities, max_results)

    related_docs = []

    for i in top_related_indices:
        if cosine_similarities[i] > similarity_threshold:
            related_docs.append(corpus[i])

    return related_docs


async def preprocess_text(text: str) -> str:
    """
    Args:
        text (str): Raw text input to preprocess

    Returns:
        str: Preprocessed text with stopwords removed and words stemmed
    """
    tokens = word_tokenize(text.lower())
    return " ".join(
        [
            snow_stem.stem(word)
            for word in tokens
            if word not in stopwords.words("english")
        ]
    )
