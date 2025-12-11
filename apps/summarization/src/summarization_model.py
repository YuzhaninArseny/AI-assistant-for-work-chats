import torch
from transformers import GPT2Tokenizer, T5ForConditionalGeneration
import time


class SummarizationModel:
    def __init__(self, model_name='RussianNLP/FRED-T5-Summarizer'):
        self._print_banner()
        self._model_name = model_name

        print("🚀 Инициализация модели суммаризации...")
        print(f"📦 Модель: {model_name}")
        print(f"⚡ Устройство: {'GPU (CUDA)' if torch.cuda.is_available() else 'CPU'}")
        print("-" * 50)

        # Загрузка токенизатора с прогресс-баром
        print("🔤 Загрузка токенизатора...", end=" ")
        start_time = time.time()
        self._tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        print(f"✅ Готово! ({time.time() - start_time:.1f}с)")

        # Загрузка модели с прогресс-баром
        print("🧠 Загрузка модели...", end=" ")
        start_time = time.time()
        self._model = T5ForConditionalGeneration.from_pretrained(model_name)
        load_time = time.time() - start_time
        print(f"✅ Готово! ({load_time:.1f}с)")

        # Перемещение на устройство
        self._device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"📡 Перемещение модели на {self._device}...", end=" ")
        self._model.to(self._device)
        print("✅ Успешно!")

        self._print_success_message(load_time)

    def _print_banner(self):
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                   🎯 МОДЕЛЬ СУММАРИЗАЦИИ                   ║
║                     Инициализация в Docker                  ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)

    def _print_success_message(self, load_time):
        success_msg = f"""
╔══════════════════════════════════════════════════════════════╗
║                        🎉 УСПЕХ!                            ║
║           Модель успешно загружена и готова к работе!       ║
║                                                              ║
║  ⏱️  Время загрузки: {load_time:.1f} секунд                    ║
║  🎯 Устройство: {str(self._device).upper()}                          ║
║  📊 Память GPU: {self._get_gpu_memory() if torch.cuda.is_available() else 'N/A'}        ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(success_msg)

    def _get_gpu_memory(self):
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1024 ** 3
            reserved = torch.cuda.memory_reserved() / 1024 ** 3
            return f"{allocated:.1f}GB / {reserved:.1f}GB"
        return "N/A"

    def summarize(self, text):
        print(f"📝 Суммаризация текста ({len(text)} символов)...")

        input_ids = self._tokenizer(
            [text],
            max_length=1024,
            padding='max_length',
            truncation=True,
            return_tensors='pt',
        )['input_ids'].to(self._device)

        with torch.no_grad():
            output_ids = self._model.generate(
                input_ids,
                eos_token_id=self._tokenizer.eos_token_id,
                num_beams=5,
                min_new_tokens=17,
                max_new_tokens=300,
                do_sample=True,
                no_repeat_ngram_size=4,
                top_p=0.9
            )[0]

        summary = self._tokenizer.decode(
            output_ids,
            skip_special_tokens=True
        )

        print(f"✅ Суммаризация завершена! Результат: {len(summary)} символов")
        return summary
