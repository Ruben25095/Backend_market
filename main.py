# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, User, Product
from pydantic import BaseModel 
from passlib.context import CryptContext
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
#uvicorn main:app --reload --host 192.168.0.10 --port 8000
app = FastAPI()
#uvicorn main:app --reload 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes, o especifica los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Modelo Pydantic
class UserCreate(BaseModel):
    username: str
    password: str
    useremail: str


class UserLogin(BaseModel):
    useremail: str
    password: str
   
class ProductCreate(BaseModel):
    id: int
    title: str
    price: int
    description: str
    image: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Endpoint para registrar usuario
@app.post("/register")
def register(user:UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    db_email = db.query(User).filter(User.useremail == user.useremail).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, password=hashed_password, useremail=user.useremail)
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

# Endpoint para login
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.useremail == user.useremail).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"message": "Login successful"}


# Endpoint para agregar un producto
@app.post("/add_product")
def add_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product.id).first()
    if db_product:
        raise HTTPException(status_code=400, detail="Product with this ID already exists")
    new_product = Product(
        id=product.id,
        title=product.title,
        price=product.price,
        description=product.description,
        image=product.image
    )
    db.add(new_product)
    db.commit()
    return {"message": "Product added successfully"}

# Endpoint para consultar todos los productos
@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return {"products": products}

@app.delete("/delete_product")
def delete_product(product_id: int, db: Session = Depends(get_db)): 
    db_product = db.query(Product).filter(Product.id == product_id).first()  
    if not db_product: 
        raise HTTPException(status_code=404, detail="Product not found")      
    db.delete(db_product)                                                     
    db.commit()  
    return {"message": "Product deleted successfully"}