from chromadb import Client
from sentence_transformers import SentenceTransformer
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from typing import List, Dict, Any, Optional
import uuid


class ChromaChatSearchEngine:
    def __init__(
            self,
            collection_name="chat_messages",
            model_name="cointegrated/rubert-tiny2",
            similarity_threshold_lower: float = 0.9,
            similarity_threshold_upper: float = 0.65
    ):
        assert 0 <= similarity_threshold_lower <= 1
        assert 0 <= similarity_threshold_upper <= 1

        self.model = SentenceTransformer(model_name)
        self.tg_url_prefix = 'https://t.me'
        self.client = Client()
        self.similarity_threshold_lower = similarity_threshold_lower
        self.similarity_threshold_upper = similarity_threshold_upper
        self.embedding_function = SentenceTransformerEmbeddingFunction(
            model_name=model_name
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )

    def _embedding_function(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False
        )

        return embeddings.tolist()

    def add_chat_messages(self, messages: List[Dict]):
        """
        Добавление сообщений в векторную базу
        messages: список словарей с ключами 'text', 'sender', 'timestamp' и др.
        """
        try:
            if not messages:
                return

            documents = []
            metadatas = []
            ids = []
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
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
        except Exception as e:
            print(
                f'Произошла ошибка при сохранении сообщений в {self.collection.name}'
                f'Error: {repr(e)}'
            )
            raise e

    def search(
            self,
            key_words: List[str],
            top_k: int = 10000
    ) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Поиск по всем чатам с группировкой результатов и фильтрацией по порогу схожести

        Args:
            key_words: список ключевых слов для поиска
            top_k: максимальное количество результатов для каждого запроса
            similarity_threshold: порог схожести (0-1). Если None, используется значение по умолчанию

        Returns:
            Словарь с результатами, отфильтрованными по порогу схожести
        """
        try:
            results = self.collection.query(
                query_texts=key_words,
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )

            print(f"Найдено результатов до фильтрации: {len(results['documents'][0]) if results['documents'] else 0}")

            grouped_results = {}

            for i, key_word in enumerate(key_words):
                if not results['documents'] or not results['documents'][i]:
                    continue

                for doc, metadata, distance in zip(
                        results['documents'][i],
                        results['metadatas'][i],
                        results['distances'][i]
                ):
                    similarity = 1 - distance
                    if self.similarity_threshold_lower < similarity or similarity > self.similarity_threshold_upper:
                        continue

                    message_id = metadata.get('message_id')
                    chat_id = metadata['chat_id']
                    if not message_id:
                        continue

                    if chat_id not in grouped_results:
                        grouped_results[chat_id] = {}

                    # Если сообщение уже есть, выбираем вариант с большей схожестью
                    if message_id not in grouped_results[chat_id]:
                        grouped_results[chat_id][message_id] = {
                            'text': doc,
                            'similarity': similarity,
                            **metadata
                        }
                    else:
                        # Обновляем, если нашли более релевантный вариант
                        current_similarity = grouped_results[chat_id][message_id].get('similarity', 0)
                        if similarity > current_similarity:
                            grouped_results[chat_id][message_id] = {
                                'text': doc,
                                'similarity': similarity,
                                **metadata
                            }

            for chat_id in grouped_results:
                sorted_messages = sorted(
                    grouped_results[chat_id].items(),
                    key=lambda x: x[1].get('similarity', 0),
                    reverse=True
                )[:top_k]
                grouped_results[chat_id] = dict(sorted_messages)

            print(f"Найдено результатов после фильтрации: {sum(len(msgs) for msgs in grouped_results.values())}")
            return grouped_results

        except Exception as e:
            print(f"Ошибка при поиске по всем чатам: {repr(e)}")
            return {}