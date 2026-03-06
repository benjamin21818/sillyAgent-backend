from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.backend.api import router



app = FastAPI()

# 解决跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


