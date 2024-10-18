from pymongo.synchronous.collection import Collection
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

snow_stem = SnowballStemmer(language="english")


async def get_last_questions(collection: Collection, id: str, limit=15) -> dict:
    return collection.find({"_id": id}).limit(limit=limit).to_list()[0]


async def top_k(arr, k) -> np.array:
    kth_largest = (k + 1) * -1
    return np.argsort(arr)[:kth_largest:-1]


async def get_context(
    corpus: list[str],
    query: str,
    max_results: int = 5,
    similarity_threshold: float = 0.1,
) -> list[str]:
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
    tokens = word_tokenize(text.lower())
    return " ".join(
        [
            snow_stem.stem(word)
            for word in tokens
            if word not in stopwords.words("english")
        ]
    )
