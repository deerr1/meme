import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.storage import router as storage_router


app = FastAPI()

app.include_router(
    storage_router,
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
    uvicorn.run("main:app", host='0.0.0.0', port=8001, reload=True)