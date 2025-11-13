from django.core.wsgi import get_wsgi_application

# Fallback local implementation of vercel_wsgi.handle_request to avoid unresolved import
# This attempts to adapt a Vercel-style request/response to a Django WSGI application.
def handle_request(request, response, application):
    # Try to obtain a WSGI environ from the incoming request (common attributes used by adapters)
    environ = {}
    if hasattr(request, "environ"):
        environ = request.environ
    elif hasattr(request, "META"):
        environ = request.META.copy()
    else:
        # minimal WSGI environ
        environ = {
            "REQUEST_METHOD": getattr(request, "method", "GET"),
            "PATH_INFO": getattr(request, "path", "/"),
            "SERVER_NAME": "localhost",
            "SERVER_PORT": "80",
            "wsgi.version": (1, 0),
            "wsgi.url_scheme": "http",
            "wsgi.input": getattr(request, "body", b""),
            "wsgi.errors": None,
            "wsgi.multithread": False,
            "wsgi.multiprocess": False,
            "wsgi.run_once": False,
        }

    # Capture status and headers from the WSGI start_response callable
    status_headers = {}

    def start_response(status, headers, exc_info=None):
        status_headers["status"] = status
        status_headers["headers"] = headers
        return None

    result = application(environ, start_response)

    # Collect body bytes
    try:
        body = b"".join(result) if result is not None else b""
    except TypeError:
        # If result yields strings, encode them
        body = b"".join(
            (chunk.encode() if isinstance(chunk, str) else chunk) for chunk in result
        )

    # Apply status
    status = status_headers.get("status", "200 OK")
    try:
        response.status_code = int(status.split()[0])
    except Exception:
        # leave response.status_code unchanged if not settable
        pass

    # Apply headers
    for k, v in status_headers.get("headers", []):
        try:
            # common API on many serverless response objects
            response.set_header(k, v)
        except Exception:
            try:
                # alternative setter name
                response.headers[k] = v
            except Exception:
                # last resort: attach to response object
                setattr(response, k.replace("-", "_"), v)

    # Write body
    try:
        # common APIs: write or set body attribute
        if hasattr(response, "write"):
            response.write(body)
        else:
            response.body = body
    except Exception:
        # ignore write errors; caller may handle response differently
        response.body = body

    return response

# Ensure Django settings are loaded
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "leavesync_backend.settings")

application = get_wsgi_application()

def handler(request, response):
    return handle_request(request, response, application)
