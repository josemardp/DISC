from fastapi import FastAPI

app = FastAPI()

@app.get("/api/simple")
@app.get("/api/simple/{path:path}")
def test(path: str = ""):
    return {"ok": True, "path": path}
