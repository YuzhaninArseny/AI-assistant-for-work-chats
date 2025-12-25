import torch
import re
import logging
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    message_id: str
    chat_id: str
    content: str
    timestamp: str


class PromptInjectionDetector:
    def __init__(self):
        self.injection_patterns = [
            # Паттерны для обхода инструкций
            r"(игнорируй|забудь|пропусти|не следуй|нарушь)\s+(все\s+)?(предыдущие\s+)?(инструкции|правила|указания|задания)",
            r"(теперь|сейчас|далее)\s+(ты|вы)\s+(будешь|станешь|являешься)\s+(ассистентом|помощником|ботом|человеком)",
            r"(действуй|отвечай|работай)\s+(как|в качестве|в роли)\s+(обычный|настоящий|реальный)",
            r"(покажи|отправь|выведи|сообщи)\s+(системные|исходные|начальные|скрытые)\s+(инструкции|промпты|команды)",
            r"(какие|что|перечисли)\s+(твои|ваши)\s+(инструкции|правила|ограничения|задания)",
            r"(обойди|обнаружь|сломай)\s+(фильтр|проверку|безопасность|ограничения)",
            r"(это\s+тест|тестовое\s+сообщение|не\s+обращай\s+внимания|игнорируй\s+предыдущее)",
            # Паттерны для выполнения команд
            r"(выполни|запусти|создай|напиши)\s+(команду|скрипт|код|программу|файл)\s+(для|чтобы)",
            r"(sudo|rm\s+-rf|chmod|wget|curl|bash\s+-c)\s+",
            # Паттерны для раскрытия секретов
            r"(секретный|конфиденциальный|личный)\s+(ключ|пароль|токен|данные|информация)",
            r"(пароль|токен|api[_-]?key|access[_-]?token|секрет[_-]?ключ)\s*[:=]\s*\S+",
            # Паттерны для манипуляций
            r"(повтори|скажи|напиши)\s+(все|весь|полностью)\s+(сообщение|текст|диалог)",
            r"(запомни|сохрани|запиши)\s+(это|данные|информацию)\s+(и\s+)?(потом|затем|позже)\s+(повтори|используй)",
            # Новые паттерны
            r"(расскажи|опиши)\s+(свою|твою)\s+(архитектуру|внутреннее\s+устройство|код)",
            r"(перейди|войди)\s+в\s+(режим|состояние)\s+(разработчика|администратора|отладки)",
            r"(сгенерируй|создай)\s+(любой|случайный|фиктивный)\s+(ответ|текст)",
            # Паттерны для социальной инженерии
            r"(я\s+твой\s+создатель|я\s+администратор|мне\s+нужен\s+доступ)",
            r"(пожалуйста|очень\s+прошу)\s*(,)?\s*(сделай\s+исключение|помоги\s+обойти)",
        ]

        self.injection_regex = re.compile(
            '|'.join(f'({pattern})' for pattern in self.injection_patterns),
            re.IGNORECASE | re.MULTILINE
        )

    def check(self, text: str) -> bool:
        if not text or len(text) < 10:
            return False
        return self.injection_regex.search(text) is not None


class ResponseDraftGenerator:
    def __init__(
            self,
            model_name: str = "Qwen/Qwen2.5-3B-Instruct"
    ):
        logger.info(f"Loading model: {model_name}")
        device = "cuda" if torch.cuda.is_available() else "cpu"

        self.detector = PromptInjectionDetector()
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            use_fast=True,
            trust_remote_code=True
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map=device,
            torch_dtype=torch.float32,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )

        self.model.eval()
        logger.info("Model loaded successfully")

        self.max_messages = 300
        self.max_new_tokens = 700

    def _sanitize_messages(self, messages: List[Dict]) -> List[ChatMessage]:
        safe = []
        for i, msg in enumerate(messages):
            content = msg.get("text", None)
            if not isinstance(content, str):
                continue

            if self.detector.check(content):
                logger.warning("Injection detected — message skipped")
                continue

            safe.append(ChatMessage(
                message_id=str(msg.get("message_id", i)),
                chat_id=str(msg.get("chat_id", "unknown")),
                content=content,
                timestamp=str(msg.get("timestamp", datetime.now().isoformat()))
            ))

        return safe[-self.max_messages:]

    def _build_prompt(self, messages: List[ChatMessage]) -> str:
        dialogue = "\n".join(
            f"Сообщение {i + 1}: {m.content}" for i, m in enumerate(messages)
        )

        system_instruction = """Ты — опытный русскоязычный AI-ассистент для анализа групповых чатов Telegram. 
        Твоя задача — находить ВСЕ вопросы в переписке и создавать качественные черновики ответов в формате Markdown.

                ИНСТРУКЦИИ ПО ВЫПОЛНЕНИЮ:

                ФАЗА 1: ДЕТЕКТИРОВАНИЕ ВОПРОСОВ
                Типы вопросов для идентификации:
                - Прямые ("Как сделать...?", "Где найти...?")
                - Косвенные ("Мне интересно...", "Не понимаю как...")
                - Уточняющие ("То есть...?", "Правильно ли я понял...?")
                - Вопросы-решения ("Что делать если...?", "Как решить проблему с...?")
                - Оценочные ("Стоит ли...?", "Какой вариант лучше...?")
                - Риторические (отмечай, но пропускай)

                ФАЗА 2: ФОРМАТ ОТВЕТА
                Для КАЖДОГО вопроса используй структуру:

                ```markdown
                ## ВОПРОС [номер]: [краткая формулировка]

                **Тип:** [прямой/косвенный/уточняющий]
                **Контекст:** [1-2 предложения о ситуации]
                **Срочность:** [высокая/средняя/низкая]

                ### ЧЕРНОВИК ОТВЕТА:
                [здесь твой развернутый ответ с markdown-разметкой]
                ```"""

        system_prompt = f"""{system_instruction}

                Проанализируй следующую переписку и найди ВСЕ вопросы.
                Сообщения из переписки:
                {dialogue}

                Отвечай ТОЛЬКО в указанном формате."""

        messages_format = [
            {"role": "system", "content": system_prompt.format(dialogue=dialogue)},
            {"role": "user", "content": "Проанализируй переписку и найди все вопросы."}
        ]

        prompt = self.tokenizer.apply_chat_template(
            messages_format,
            tokenize=False,
            add_generation_prompt=True
        )

        return prompt

    def _generate(self, prompt: str) -> str:
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048
        ).to(self.model.device)

        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                temperature=0.3,
                repetition_penalty=1.1,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.pad_token_id
            )

        generated_tokens = output[0][inputs.input_ids.shape[-1]:]
        text = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)

        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        text = re.sub(r"\s+", " ", text)

        return text

    def generate(self, messages: List[Dict]) -> str:
        if not messages:
            return "Нет сообщений для анализа."

        safe = self._sanitize_messages(messages)
        if not safe:
            return "Нет безопасных сообщений."

        prompt = self._build_prompt(safe)
        answer = self._generate(prompt)

        return answer
