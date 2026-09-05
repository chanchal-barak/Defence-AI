from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from backend.app.api.routes import router
from backend.app.database.database import Base, engine
from backend.app.database import models

Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="DefenceDoc AI",
    description="Public/unclassified document analysis and anomaly detection API",
    version="0.1.0",
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )

    components = schema.get("components", {}).get("schemas", {})

    for component in components.values():

        properties = component.get("properties", {})

        for prop in properties.values():

            # Array of uploaded files
            if (
                prop.get("type") == "array"
                and isinstance(prop.get("items"), dict)
            ):
                items = prop["items"]

                if items.get("contentMediaType") == "application/octet-stream":
                    items.pop("contentMediaType", None)
                    items["format"] = "binary"

            # Single uploaded file
            if (
                prop.get("type") == "string"
                and prop.get("contentMediaType") == "application/octet-stream"
            ):
                prop.pop("contentMediaType", None)
                prop["format"] = "binary"

    app.openapi_schema = schema

    return app.openapi_schema


app.openapi = custom_openapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)


@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": "DefenceDoc AI"
    }