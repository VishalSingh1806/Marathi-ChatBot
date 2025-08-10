from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Test server working"}

@app.get("/test")
def test_endpoint():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)