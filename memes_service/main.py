import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.meme import router as router_meme


app = FastAPI()

app.include_router(
    router_meme,
    prefix='/api/v1'
    )

origins = [
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

if __name__=="__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)