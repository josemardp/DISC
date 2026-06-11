import sys
import traceback
import json

_backend = None
_load_error = None

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

async def _error_response(send, status, message, detail=""):
    body = json.dumps({"error": message, "detail": detail}).encode()
    await send({
        "type": "http.response.start", "status": status,
        "headers": [(b"content-type", b"application/json; charset=utf-8"),
                    (b"content-length", str(len(body)).encode())]
    })
    await send({"type": "http.response.body", "body": body})

async def app(scope, receive, send):
    # Carrega o backend na primeira chamada (lifespan ou http)
    _load()

    # Se o backend carregou, delega tudo — inclusive lifespan com startup event
    if _backend is not None:
        try:
            await _backend(scope, receive, send)
        except Exception as e:
            tb = traceback.format_exc()
            print("RUNTIME ERROR:", tb, file=sys.stderr)
            if scope["type"] == "http":
                await _error_response(send, 500, "runtime error", tb)
        return

    # Fallback: backend não carregou
    if scope["type"] == "lifespan":
        await send({"type": "lifespan.startup.complete"})
        msg = await receive()
        if msg["type"] == "lifespan.shutdown":
            await send({"type": "lifespan.shutdown.complete"})
        return

    if scope["type"] == "http":
        await _error_response(send, 500, "backend failed to load", _load_error)
