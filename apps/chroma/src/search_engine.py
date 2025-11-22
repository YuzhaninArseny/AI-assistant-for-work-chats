from chromadb import Client
from sentence_transformers import SentenceTransformer
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from typing import List, Dict, Any
import uuid

# Потестить работу и качество rag-системы на бенчмарках

class ChromaChatSearchEngine:
    def __init__(
            self,
            collection_name="chat_messages",
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            ):
        self.model = SentenceTransformer(model_name)
        self.tg_url_prefix = 'https://t.me'
        self.client = Client()
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
                    'chat_id': str(msg['id']),
                    'link': f'{self.tg_url_prefix}/{msg["id"]}/{msg["message_id"]}',
                    'timestamp': msg['date'],
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
                f'Error: {e}'
            )
            raise e

    def search(self, key_words: List[str], top_k: int = 10000) \
            -> Dict[str, Dict[str, Dict[str, List[Any]]]]:
        """
        Поиск по всем чатам с группировкой результатов
        """
        try:
            results = self.collection.query(
                query_texts=key_words,
                n_results=top_k
            )

            print(results)

            grouped_results = {}
            for i, key_word in enumerate(key_words):
                if not results['documents'] or not results['documents'][i]:
                    continue

                for doc, metadata, distance in zip(
                        results['documents'][i],
                        results['metadatas'][i],
                        results['distances'][i]
                ):
                    message_id = metadata.get('message_id')
                    chat_id = metadata['chat_id']
                    if not message_id:
                        continue

                    if chat_id not in grouped_results:
                        grouped_results[chat_id] = {}

                    if message_id not in grouped_results[chat_id]:
                        grouped_results[chat_id][message_id] = {
                            'text': doc,
                            **metadata
                        }

            return grouped_results

        except Exception as e:
            print(f"Ошибка при поиске по всем чатам: {e}")
            return {}