# модели для эмбеддингов 
# paraphrase-multilingual-MiniLM-L12-v2

import chromadb
from sentence_transformers import SentenceTransformer
import re
from typing import List, Tuple, Dict
import uuid
from datetime import datetime

class ChromaChatSearchEngine:
    def __init__(self, collection_name="chat_messages", persist_directory="./chroma_messages_db"):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Хранилище сообщений чатов для поиска"}
        )
        
    def add_chat_messages(self, chat_name: str, messages: List[Dict]):
        """
        Добавление сообщений в векторную базу
        messages: список словарей с ключами 'text', 'sender', 'timestamp' и др.
        """
        if not messages:
            return
            
        # Подготовка данных для добавления
        documents = []
        metadatas = []
        ids = []
        
        for msg in messages:
            if 'text' not in msg:
                continue
                
            doc_id = str(uuid.uuid4())
            documents.append(msg['text'])
            metadatas.append({
                'chat_name': chat_name,
                'sender': msg.get('sender', 'unknown'),
                'timestamp': msg.get('timestamp', str(datetime.now())),
                'message_id': msg.get('message_id', doc_id)
            })
            ids.append(doc_id)
        
        # Добавление в коллекцию Chroma
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
    
    def search(self, chat_name: str, query: str, top_k: int = 5, 
               similarity_threshold: float = 0.3) -> List[Tuple[Dict, float]]:
        """
        Поиск релевантных сообщений в указанном чате
        """
        try:
            # Выполнение поиска с фильтром по названию чата
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where={"chat_name": chat_name}
            )
            
            # Форматирование результатов
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    # Преобразование расстояния в схожесть (1 - distance)
                    similarity = 1 - distance
                    if similarity >= similarity_threshold:
                        result_item = {
                            'text': doc,
                            'metadata': metadata,
                            'similarity': similarity
                        }
                        formatted_results.append((result_item, similarity))
            
            return formatted_results
            
        except Exception as e:
            print(f"Ошибка при поиске: {e}")
            return []
    
    def search_across_all_chats(self, query: str, top_k: int = 10) -> Dict[str, List]:
        """
        Поиск по всем чатам с группировкой результатов
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            grouped_results = {}
            
            if results['documents'] and results['documents'][0]:
                for doc, metadata, distance in zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                ):
                    chat_name = metadata['chat_name']
                    similarity = 1 - distance
                    
                    if chat_name not in grouped_results:
                        grouped_results[chat_name] = []
                    
                    grouped_results[chat_name].append({
                        'text': doc,
                        'metadata': metadata,
                        'similarity': similarity
                    })
            
            # Сортировка результатов внутри каждой группы по схожести
            for chat in grouped_results:
                grouped_results[chat].sort(key=lambda x: x['similarity'], reverse=True)
                
            return grouped_results
            
        except Exception as e:
            print(f"Ошибка при поиске по всем чатам: {e}")
            return {}
    
    def get_chat_stats(self, chat_name: str = None) -> Dict:
        """
        Получение статистики по сообщениям
        """
        try:
            if chat_name:
                # Получаем все сообщения конкретного чата
                results = self.collection.get(
                    where={"chat_name": chat_name}
                )
            else:
                # Получаем все сообщения
                results = self.collection.get()
            
            return {
                'total_messages': len(results['ids']),
                'unique_chats': len(set([m['chat_name'] for m in results['metadatas']])) if results['metadatas'] else 0,
                'unique_senders': len(set([m.get('sender', 'unknown') for m in results['metadatas']])) if results['metadatas'] else 0
            }
            
        except Exception as e:
            print(f"Ошибка при получении статистики: {e}")
            return {}

# Сервис для обработки команд
class ChatSearchService:
    def __init__(self):
        self.search_engine = ChromaChatSearchEngine()
    
    def process_command(self, command: str) -> Dict:
        """
        Обработка команды поиска
        Формат: /search @название_чата "ключевые слова"
        """
        # Парсинг команды
        pattern = r'/search @(\w+)\s+"([^"]*)"'
        match = re.match(pattern, command)
        
        if not match:
            return {
                'error': 'Неверный формат команды. Используйте: /search @chatname "keywords"'
            }
        
        chat_name = match.group(1)
        query = match.group(2)
        
        # Выполнение поиска
        results = self.search_engine.search(chat_name, query)
        
        return {
            'chat_name': chat_name,
            'query': query,
            'results': results,
            'results_count': len(results)
        }
    
    def add_messages_to_chat(self, chat_name: str, messages: List[Dict]):
        """Добавление сообщений в чат"""
        self.search_engine.add_chat_messages(chat_name, messages)

# Пример использования и тестирования
def setup_test_data(service: ChatSearchService):
    """Настройка тестовых данных"""
    
    # Тестовые сообщения для разных чатов
    devops_messages = [
        {
            'text': 'Обсуждаем архитектуру микросервисов и их преимущества',
            'sender': 'alex',
            'timestamp': '2024-01-15 10:00:00',
            'message_id': 'msg1'
        },
        {
            'text': 'Проблемы с развертыванием в Kubernetes кластере',
            'sender': 'maria', 
            'timestamp': '2024-01-15 11:30:00',
            'message_id': 'msg2'
        },
        {
            'text': 'Как настроить мониторинг приложения с помощью Prometheus?',
            'sender': 'ivan',
            'timestamp': '2024-01-16 09:15:00',
            'message_id': 'msg3'
        }
    ]
    
    python_messages = [
        {
            'text': 'Лучшие практики асинхронного программирования в Python',
            'sender': 'sophia',
            'timestamp': '2024-01-14 14:20:00',
            'message_id': 'msg4'
        },
        {
            'text': 'Оптимизация производительности Django приложений',
            'sender': 'maxim',
            'timestamp': '2024-01-14 16:45:00', 
            'message_id': 'msg5'
        },
        {
            'text': 'Использование FastAPI для создания REST API',
            'sender': 'anna',
            'timestamp': '2024-01-15 13:10:00',
            'message_id': 'msg6'
        }
    ]
    
    # Добавление тестовых данных
    service.add_messages_to_chat("devops", devops_messages)
    service.add_messages_to_chat("python", python_messages)

def main():
    # Инициализация сервиса
    service = ChatSearchService()
    
    # Настройка тестовых данных
    setup_test_data(service)
    
    # Тестовые запросы
    test_commands = [
        '/search @devops "мониторинг приложения"',
        '/search @python "асинхронное программирование"',
        '/search @devops "Kubernetes развертывание"',
        '/search @nonexistent "test"'
    ]
    
    print("=== ТЕСТИРОВАНИЕ ПОИСКА ПО ЧАТАМ ===\n")
    
    for command in test_commands:
        print(f"🔍 Запрос: {command}")
        result = service.process_command(command)
        
        if 'error' in result:
            print(f"❌ Ошибка: {result['error']}")
        else:
            print(f"📊 Найдено результатов: {result['results_count']}")
            for item, similarity in result['results']:
                print(f"   📝 [Сходство: {similarity:.3f}] {item['text']}")
                print(f"   👤 От: {item['metadata']['sender']}")
        print("-" * 80)
    
    # Поиск по всем чатам
    print("\n=== ПОИСК ПО ВСЕМ ЧАТАМ ===\n")
    all_results = service.search_engine.search_across_all_chats("программирование")
    
    for chat_name, messages in all_results.items():
        print(f"💬 Чат: {chat_name}")
        for msg in messages[:3]:  # Показываем топ-3 результата для каждого чата
            print(f"   📝 [Сходство: {msg['similarity']:.3f}] {msg['text']}")
        print()
    
    # Статистика
    print("\n=== СТАТИСТИКА ===\n")
    stats = service.search_engine.get_chat_stats()
    print(f"Всего сообщений: {stats['total_messages']}")
    print(f"Уникальных чатов: {stats['unique_chats']}")
    print(f"Уникальных отправителей: {stats['unique_senders']}")

if __name__ == "__main__":
    main()