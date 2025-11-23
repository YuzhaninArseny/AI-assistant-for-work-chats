from typing import Dict
from transformers import AutoModel, AutoTokenizer


class ResponseDraftGenerator:
    def __init__(self, model_name: str = ''):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def generate(self, messages: list[Dict]):
        formatted_messages = '\n'.join([f'{i + 1}) {msg["content"]}' for i, msg in enumerate(messages)])
        prompt = f"""
            # ЗАДАЧА: Анализ Telegram-переписки и генерация ответов
    
            ## РОЛЬ
            Ты — AI-ассистент для анализа групповых чатов. Твоя задача — находить ВСЕ вопросы в переписке и создавать качественные черновики ответов в формате Markdown.
    
            ## ИНСТРУКЦИИ ПО ВЫПОЛНЕНИЮ
    
            ### ФАЗА 1: ДЕТЕКТИРОВАНИЕ ВОПРОСОВ
            **Типы вопросов для идентификации:**
            - **Прямые** ("Как сделать...?", "Где найти...?")
            - **Косвенные** ("Мне интересно...", "Не понимаю как...")
            - **Уточняющие** ("То есть...?", "Правильно ли я понял...?")
            - **Вопросы-решения** ("Что делать если...?", "Как решить проблему с...?")
            - **Оценочные** ("Стоит ли...?", "Какой вариант лучше...?")
            - **Риторические** (отмечай, но пропускай)
    
            ### ФАЗА 2: ФОРМАТ ОТВЕТА
            Для КАЖДОГО вопроса используй структуру:
    
            ```markdown
            ## ВОПРОС [номер]: [краткая формулировка]
    
            **Тип:** [прямой/косвенный/уточняющий]
            **Контекст:** [1-2 предложения о ситуации]
            **Срочность:** [высокая/средняя/низкая]
            
            ### СООБЩЕНИЯ ДЛЯ АНАЛИЗА:
            {formatted_messages}
    
            ### ЧЕРНОВИК ОТВЕТА:
            ```markdown
            [здесь твой развернутый ответ с markdown-разметкой]
        """

        inputs = self.tokenizer(prompt, return_tensors='pt')
        output = self.model.generate(**inputs, num_beams=5)
        answer = self.tokenizer.decode(output[0], skip_special_tokens=True)

        return answer
