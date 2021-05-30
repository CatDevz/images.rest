# pylint: disable=no-name-in-module
# pylint: disable=no-self-argument

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routes.image import router as image_router


app = FastAPI(
    title="images.rest",
    description="Simple yet powerful REST API for modifing images.",
    version="1.0.0",
    docs_url='/',
    redoc_url=None,

    openapi_tags=[
        {"name": "Main"}
    ]
)

# Adding CORS middleware allowing API access
# from any domain on the internet
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adding the routers
app.include_router(image_router, tags=["Main"])
