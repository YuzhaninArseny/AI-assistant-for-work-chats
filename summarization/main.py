from summarization_model import SummarizationModel
from fastapi import FastAPI

model = SummarizationModel()
app = FastAPI()

@app.get('get-summarization')
def get_summarization(user_id, chat_id):
    # здесь можно отдать власть Димуле, чтобы он составил хороший промпт
    messages = db_client.get_messages(user_id, chat_id)

    text = f"""{" ".join(messages)}"""
    summarize_text = model.summarize(text)

    return summarize_text
