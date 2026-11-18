from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, init_models, Product

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_models()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_index():
    return FileResponse("index.html")

@app.get("/api/products")
async def get_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    return result.scalars().all()

class ButtonAction(BaseModel):
    item_id: int | None = None
    action: str
    promo_code: str | None = None

@app.post("/api/button-click")
async def handle_button_click(data: ButtonAction):
    if data.action == "activate_promo":
        return {"status": "success", "message": f"Промокод «{data.promo_code}» активирован!"}
    
    if data.action == "add_to_cart":
        return {"status": "success", "message": f"Товар #{data.item_id} добавлен в корзину!"}

    return {"status": "error", "message": "Неизвестное действие"}

# 4. Раздаем style.css и картинки (карусель1.webp и др.) прямо из корня
# Важно: эта строка должна быть в самом конце файла!
app.mount("/", StaticFiles(directory="."), name="static")
