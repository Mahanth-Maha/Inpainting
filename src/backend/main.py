from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from api.endpoints import router as api_router
from api.v1.endpoints import router as router_v1

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(api_router)
app.include_router(router_v1, prefix="/v1")


@app.get("/")
def read_root():
    return {"message": "Welcome to the Inpainting API!"}
