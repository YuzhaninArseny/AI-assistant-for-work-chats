


class ResponseDraftGenerator:
    def __init__(self):
        pass





# # -------------------------------------------------

# Промпт:
# напиши пожалуйста небольшой пайплайн, который будет непосредственно 
# получать сообщения и на выходе отдавать пример черновика. 
# То есть реализуй полноценный такой сервер с функциями и 
# подходящими моделями нейросетей

# from flask import Flask, request, jsonify
# from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
# import torch
# from typing import List, Dict
# import re

# app = Flask(__name__)

# class ResponseGenerator:
#     def __init__(self):
#         # Модель для анализа тональности
#         self.sentiment_analyzer = pipeline(
#             "sentiment-analysis",
#             model="blanchefort/rubert-base-cased-sentiment"
#         )
        
#         # Модель для генерации текста (русскоязычная)
#         self.tokenizer = AutoTokenizer.from_pretrained("inkoziev/saiga_llama3_8b")
#         self.model = AutoModelForCausalLM.from_pretrained(
#             "inkoziev/saiga_llama3_8b",
#             torch_dtype=torch.float16,
#             device_map="auto"
#         )
        
#         # Системный промпт для модели
#         self.system_prompt = """Ты - помощник для генерации ответов на сообщения. 
#         Анализируй историю переписки и создавай уместный, естественный ответ.
#         Ответ должен быть кратким (1-3 предложения) и соответствовать контексту."""
        
#         self.ton_mapping = {
#             'POSITIVE': 'дружелюбный',
#             'NEGATIVE': 'вежливый но сдержанный',
#             'NEUTRAL': 'нейтральный деловой'
#         }

#     def analyze_conversation(self, messages: List[str]) -> Dict:
#         """Анализирует тон и содержание последних сообщений"""
#         if not messages:
#             return {"tone": "NEUTRAL", "key_topics": []}
        
#         # Анализ тональности последнего сообщения
#         last_message = messages[-1]
#         sentiment = self.sentiment_analyzer(last_message)[0]
        
#         # Простой анализ ключевых слов (можно заменить на NER)
#         key_words = self._extract_key_words(" ".join(messages[-3:]))
        
#         return {
#             "tone": sentiment['label'],
#             "confidence": sentiment['score'],
#             "key_topics": key_words,
#             "last_message": last_message
#         }

#     def _extract_key_words(self, text: str) -> List[str]:
#         """Извлекает ключевые слова (упрощенная версия)"""
#         # Удаляем стоп-слова и выделяем значимые слова
#         stop_words = {'привет', 'здравствуйте', 'спасибо', 'пожалуйста', 'можно', 'хочу'}
#         words = re.findall(r'\b[а-яёa-z]{4,}\b', text.lower())
#         return [word for word in words if word not in stop_words][:5]

#     def generate_response(self, conversation_history: List[str]) -> str:
#         """Генерирует черновик ответа на основе истории переписки"""
#         analysis = self.analyze_conversation(conversation_history)
        
#         # Формируем промпт для модели
#         prompt = f"""
#         {self.system_prompt}
        
#         Контекст разговора:
#         {' '.join(conversation_history[-3:])}
        
#         Тон общения: {self.ton_mapping.get(analysis['tone'], 'нейтральный')}
#         Ключевые темы: {', '.join(analysis['key_topics'])}
        
#         Сгенерируй подходящий ответ:
#         """
        
#         # Токенизация и генерация
#         inputs = self.tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True)
        
#         with torch.no_grad():
#             outputs = self.model.generate(
#                 **inputs,
#                 max_new_tokens=150,
#                 temperature=0.7,
#                 do_sample=True,
#                 pad_token_id=self.tokenizer.eos_token_id
#             )
        
#         response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
#         # Извлекаем только сгенерированный ответ (последний абзац)
#         generated_text = response.split("Сгенерируй подходящий ответ:")[-1].strip()
        
#         # Очищаем ответ от возможных артефактов
#         clean_response = self._clean_response(generated_response)
        
#         return clean_response

#     def _clean_response(self, text: str) -> str:
#         """Очищает сгенерированный текст"""
#         # Удаляем повторяющиеся фразы и обрезаем до разумной длины
#         sentences = text.split('.')
#         unique_sentences = []
#         seen = set()
        
#         for sentence in sentences:
#             clean_sentence = sentence.strip()
#             if clean_sentence and clean_sentence not in seen:
#                 seen.add(clean_sentence)
#                 unique_sentences.append(clean_sentence)
                
#             if len(unique_sentences) >= 3:  # Максимум 3 предложения
#                 break
                
#         return '. '.join(unique_sentences) + '.'

# # Инициализация генератора
# response_generator = ResponseGenerator()

# @app.route('/generate-reply', methods=['POST'])
# def generate_reply():
#     """API endpoint для генерации ответа"""
#     try:
#         data = request.json
        
#         # Валидация входных данных
#         if not data or 'messages' not in data:
#             return jsonify({"error": "No messages provided"}), 400
            
#         messages = data['messages']
        
#         if not isinstance(messages, list) or len(messages) == 0:
#             return jsonify({"error": "Messages should be a non-empty list"}), 400
        
#         # Генерация ответа
#         draft_response = response_generator.generate_response(messages)
        
#         # Анализ контекста для метаданных
#         context_analysis = response_generator.analyze_conversation(messages)
        
#         return jsonify({
#             "draft_response": draft_response,
#             "context_analysis": {
#                 "detected_tone": context_analysis["tone"],
#                 "confidence": context_analysis["confidence"],
#                 "key_topics": context_analysis["key_topics"]
#             },
#             "status": "success"
#         })
        
#     except Exception as e:
#         return jsonify({"error": str(e), "status": "error"}), 500

# @app.route('/health', methods=['GET'])
# def health_check():
#     """Проверка работоспособности сервера"""
#     return jsonify({"status": "healthy", "service": "AI Response Generator"})

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)