from fastapi import FastAPI
from upload import upload_document

app = FastAPI(title="Document Intelligence & GenAI")

# include routes
app.include_router(upload_document.router, prefix="/doc-ai")

@app.get("/")
def root():
    return {"message": "Document Intelligence API running 🚀"}