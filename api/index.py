import sys
import traceback
import json

_backend = None
_load_error = None
_initialized = False

def _load():
    global _backend, _load_error
    if _backend is not None or _load_error is not None:
        return
    try:
        from backend.app.main import app as backend_app
        _backend = backend_app
    except Exception as e:
        _load_error = str(e)
        print("IMPORT ERROR:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

def _init_db():
    """Cria tabelas e seed uma vez por instância, de forma não-fatal."""
    global _initialized
    if _initialized:
        return
    _initialized = True
    try:
        from backend.app.database import engine, Base, SessionLocal
        Base.metadata.create_all(bind=engine)
        from backend.app.seed import seed_db
        db = SessionLocal()
        try:
            seed_db(db)
        finally:
            db.close()
        print("[init_db] tabelas e seed OK", flush=True)
    except Exception as e:
        print(f"[init_db] erro não-fatal: {e}", flush=True)
        traceback.print_exc()

async def _error_response(send, status, message, detail=""):
    body = json.dumps({"error": message, "detail": detail}).encode()
    await send({
        "type": "http.response.start", "status": status,
        "headers": [(b"content-type", b"application/json; charset=utf-8"),
                    (b"content-length", str(len(body)).encode())]
    })
    await send({"type": "http.response.body", "body": body})

async def app(scope, receive, send):
    # Lifespan gerenciado pelo proxy — não delega ao backend
    # (evita que o startup event trave na conexão ao Postgres)
    if scope["type"] == "lifespan":
        _load()
        await send({"type": "lifespan.startup.complete"})
        msg = await receive()
        if msg["type"] == "lifespan.shutdown":
            await send({"type": "lifespan.shutdown.complete"})
        return

    if scope["type"] != "http":
        return

    _load()

    if _backend is None:
        await _error_response(send, 500, "backend failed to load", _load_error)
        return

    # Lazy init do banco na primeira request
    _init_db()

    try:
        await _backend(scope, receive, send)
    except Exception as e:
        tb = traceback.format_exc()
        print("RUNTIME ERROR:", tb, file=sys.stderr)
        await _error_response(send, 500, "runtime error", tb)
