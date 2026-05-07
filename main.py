import os

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.limiter import limiter
from app.api.user import router as user_router

app = FastAPI(title="Something API")

origins = [
    "http://localhost",
    "http://localhost:8000",
]

ALLOWED_HOSTS = {"localhost", "127.0.0.1"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def ignore_favicon(request: Request, call_next):
    host = request.headers.get("host", "").split(":")[0]

    if host not in ALLOWED_HOSTS:
        return Response(status_code=403)

    if request.url.path == "/favicon.ico":
        return Response(content="", media_type="image/x-icon")

    return await call_next(request)


# @app.get("/faivicon.ico", include_in_schema=False)
# async def favicon():
#     return Response(status_code=204)


@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return """
    <html>
        <head>
            <title>Test</title>
        </head>
        <style>
            h1 {
                color: white;
                text-align: center;
            }

            body {
                margin: 0;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                background-color: black; 
            }
        </style>
        <body>
            <h1>Hello Bitchass</h1>
        </body>
    </html>
    """


app.include_router(user_router)
