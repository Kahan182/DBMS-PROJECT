# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # >>> ADD THIS IMPORT
from app.api.endpoints import auth, products, suppliers, orders, dashboard, reorders, predictions, chatbot, customers
from app.api.api import public_router, private_router
from app.database.session import engine
from app.models import model

model.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI-Powered Inventory Management System")

# This is the list of "origins" (your frontend URLs) that are allowed to make requests
origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5173",  
    "http://127.0.0.1:5173"  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Allow only the origins in the list
    allow_credentials=True,    # Allow cookies
    allow_methods=["*"],       # Allow all methods (GET, POST, PUT, etc.)
    allow_headers=["*"],       # Allow all headers
)

private_router.include_router(products.router, prefix="/products", tags=["Products"])
private_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
private_router.include_router(suppliers.router, prefix="/suppliers", tags=["Suppliers"])
private_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
private_router.include_router(reorders.router, prefix="/reorders", tags=["Reorders"])
private_router.include_router(customers.router, prefix="/customers", tags=["Customers"])

app.include_router(public_router, prefix="/auth", tags=["Authentication"])
app.include_router(private_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Inventory Management API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
