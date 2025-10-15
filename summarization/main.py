from fastapi import FastAPI
from transformers import MBartTokenizer, MBartForConditionalGeneration
from typing import List

# моделька весит около 3.5Гб (867М параметров)
model_name = "IlyaGusev/mbart_ru_sum_gazeta"
tokenizer = MBartTokenizer.from_pretrained(model_name)
model = MBartForConditionalGeneration.from_pretrained(model_name)



app = FastAPI()

@app.get('get-summarization')
def get_summarization(messages: List[str]):
    # здесь можно отдать власть Димуле, чтобы он составил хороший промпт
    prompt = f"""
            сообщения:
                {" ".join(messages)}
        """