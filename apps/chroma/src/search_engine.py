from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer, CrossEncoder
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from typing import List, Dict, Any
import uuid
import numpy as np


class ChromaChatSearchEngine:
    def __init__(
            self,
            collection_name="chat_messages",
            bi_encoder_model="all-MiniLM-L6-v2",
            cross_encoder_model="cross-encoder/ms-marco-MiniLM-L-12-v2",
            top_n_rerank: int = 100,
            similarity_threshold_lower: float = 0.5,
            similarity_threshold_upper: float = 1.0,
            rerank_threshold: float = 0.85
    ):
        assert 0 <= similarity_threshold_lower <= 1
        assert 0 <= similarity_threshold_upper <= 1
        assert 0 <= rerank_threshold <= 1

        self.bi_encoder = SentenceTransformer(bi_encoder_model)
        self.cross_encoder = CrossEncoder(cross_encoder_model)
        self.tg_url_prefix = 'https://t.me'
        self.client = PersistentClient(
            path="/data/chromadb"
        )
        self.similarity_threshold_lower = similarity_threshold_lower
        self.similarity_threshold_upper = similarity_threshold_upper
        self.top_n_rerank = top_n_rerank
        self.rerank_threshold = rerank_threshold

        self.embedding_function = SentenceTransformerEmbeddingFunction(
            model_name=bi_encoder_model
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )

    def _embedding_function(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        embeddings = self.bi_encoder.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        return embeddings.tolist()

    def add_chat_messages(self, messages: List[Dict]):
        if not messages:
            return

        documents, metadatas, ids = [], [], []
        for msg in messages:
            documents.append(msg['text'])
            metadatas.append({
                'message_id': str(msg['message_id']),
                'chat_id': str(msg['chat_id']),
                'link': f'{self.tg_url_prefix}/{msg["chat_id"]}/{msg["message_id"]}',
                'timestamp': msg['timestamp'],
            })
            ids.append(str(uuid.uuid4()))

        if documents:
            self.collection.add(documents=documents, metadatas=metadatas, ids=ids)

    def search(
            self,
            key_words: List[str],
            top_k: int = 10_000
    ) -> Dict[str, Dict[str, Dict[str, Any]]]:
        results = self.collection.query(
            query_texts=key_words,
            n_results=self.top_n_rerank,
            include=['documents', 'metadatas', 'distances']
        )

        grouped_results = {}

        for i, key_word in enumerate(key_words):
            if not results['documents'] or not results['documents'][i]:
                continue

            docs = results['documents'][i]
            metadatas = results['metadatas'][i]
            distances = results['distances'][i]

            candidates = [
                (doc, metadata, 1 - dist)
                for doc, metadata, dist in zip(docs, metadatas, distances)
                if self.similarity_threshold_lower <= 1 - dist <= self.similarity_threshold_upper
            ]
            if not candidates:
                continue

            # Реранкинг
            cross_inputs = [(key_word, doc) for doc, _, _ in candidates]
            rerank_scores = np.array(self.cross_encoder.predict(cross_inputs))

            if len(rerank_scores) > 1:
                rerank_scores = (rerank_scores - rerank_scores.min()) / (rerank_scores.max() - rerank_scores.min())
            else:
                rerank_scores = np.array([1.0])

            filtered_candidates = [
                (doc, metadata, similarity, float(score))
                for (doc, metadata, similarity), score in zip(candidates, rerank_scores)
                if score >= self.rerank_threshold
            ]

            for doc, metadata, similarity, score in sorted(filtered_candidates, key=lambda x: x[3], reverse=True)[:top_k]:
                message_id = metadata.get('message_id')
                chat_id = metadata['chat_id']
                if not message_id:
                    continue

                if chat_id not in grouped_results:
                    grouped_results[chat_id] = {}

                existing = grouped_results[chat_id].get(message_id)
                if not existing or score > existing.get('score', 0):
                    grouped_results[chat_id][message_id] = {
                        'text': doc,
                        'similarity': similarity,
                        'score': score,
                        **metadata
                    }

        return grouped_results
