from fastapi import FastAPI
from backend.api.routes import router

app = FastAPI(
    title="NaviX API",
    description="Safety-aware route recommendation system using explainable geospatial metrics.",
    version="0.1.0"
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "NaviX backend is running."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
