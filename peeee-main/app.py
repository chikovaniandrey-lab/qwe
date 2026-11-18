from contextlib import asynccontextmanager
from decimal import Decimal
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from database import async_session, init_models, Product, Order


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_models()
    
    async with async_session() as session:
        existing = await session.execute(select(Product))
        if not existing.scalars().first():
            session.add_all([
                Product(name="Бананы", description="1 кг", price=Decimal("99.00")),
                Product(name="Лук репчатый", description="1 кг", price=Decimal("45.00")),
            ])
            await session.commit()
    yield


app = FastAPI(lifespan=lifespan)

class CartItemIn(BaseModel):
    name: str
    price: float


@app.get("/")
async def get_index():
    return FileResponse("index.html")


@app.get("/api/cart")
async def get_cart():
    async with async_session() as session:
        result = await session.execute(
            select(Order)
            .options(selectinload(Order.product))
            .where(Order.status == "in_cart")
        )
        orders = result.scalars().all()
        
        return [
            {
                "id": order.id,
                "name": order.product.name,
                "price": float(order.product.price),
                "qty": order.quantity,
                "total": float(order.total_price),
            }
            for order in orders
        ]


@app.post("/api/cart")
async def add_to_cart(item: CartItemIn):
    async with async_session() as session:
        res_prod = await session.execute(select(Product).where(Product.name == item.name))
        product = res_prod.scalar_one_or_none()
        if not product:
            product = Product(name=item.name, price=Decimal(str(item.price)))
            session.add(product)
            await session.flush()

        res_order = await session.execute(
            select(Order).where(Order.product_id == product.id, Order.status == "in_cart")
        )
        order = res_order.scalar_one_or_none()

        if order:
            order.quantity += 1
            order.total_price = product.price * order.quantity
        else:
            order = Order(
                product_id=product.id,
                status="in_cart",
                quantity=1,
                total_price=product.price
            )
            session.add(order)

        await session.commit()
        return {"status": "ok"}


@app.delete("/api/cart/{order_id}")
async def remove_from_cart(order_id: int):
    async with async_session() as session:
        res = await session.execute(select(Order).where(Order.id == order_id))
        order = res.scalar_one_or_none()
        if order:
            await session.delete(order)
            await session.commit()
        return {"status": "deleted"}


@app.post("/api/checkout")
async def checkout():
    async with async_session() as session:
        await session.execute(
            update(Order)
            .where(Order.status == "in_cart")
            .values(status="ordered")
        )
        await session.commit()
        return {"status": "ordered"}

app.mount("/", StaticFiles(directory="."), name="static")
