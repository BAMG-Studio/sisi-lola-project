from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Sisi Lola Test API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Sisi Lola API is running!", "status": "success"}

@app.get("/demo")
async def demo():
    return {"message": "Demo endpoint working!", "status": "success"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
