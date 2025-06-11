from fastapi import FastAPI
from api.v1.endpoints.table_elements import router as items_router
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

# origins = [
#     "http://localhost",
#     "http://localhost:8080",
#     "http://localhost:3001",
#     "http://localhost:8080",
#     "http://127.0.0.1:3001",
# ]
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#     allow_headers=["*"],
# )
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Или конкретные домены
    allow_methods=["*"],  # Или ["GET", "POST"]
    allow_headers=["*"],
)

app.include_router(items_router, prefix="/items")
@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

