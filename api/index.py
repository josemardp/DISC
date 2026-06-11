import sys
import traceback

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

async def app(scope, receive, send):
    if scope["type"] == "lifespan":
        await send({"type": "lifespan.startup.complete"})
        msg = await receive()
        if msg["type"] == "lifespan.shutdown":
            await send({"type": "lifespan.shutdown.complete"})
        return

    _load()

    if _backend is None:
        body = f'{{"error":"backend failed to load","detail":{repr(_load_error)}}}'.encode()
        await send({
            "type": "http.response.start", "status": 500,
            "headers": [(b"content-type", b"application/json; charset=utf-8")]
        })
        await send({"type": "http.response.body", "body": body})
        return

    await _backend(scope, receive, send)
