from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from summarization_model import SummarizationModel
from request_models import SummarizeRequest

model = SummarizationModel()
app = FastAPI()


@app.post('/summarize')
def summarize(request: SummarizeRequest):
    try:
        summarize_text = model.summarize(request.prompt)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=summarize_text
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=e
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "summarization"}