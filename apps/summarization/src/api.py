from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from summarization_model import SummarizationModel

model = SummarizationModel()
app = FastAPI()


@app.get('/summarize')
def summarize(prompt: str):
    try:
        summarize_text = model.summarize(prompt)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=summarize_text
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=e
        )
