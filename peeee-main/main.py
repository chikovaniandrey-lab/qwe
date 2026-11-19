from fastapi import FastAPI
import uvicorn
from jinja2 import Environment, FileSystemLoader
from starlette.templating import Jinja2Templates
from urllib import request
from starlette.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")



templates = Jinja2Templates(directory="templates")

@app.get("/")
def privet():
    return templates.TemplateResponse({"request":request}, "index.html")


@app.get("/catalog")
def catalog():
    return templates.TemplateResponse({"request":request}, name="catalog.html")



@app.get("/cart")
def cart():
    return templates.TemplateResponse({"request":request}, name="cart.html")



@app.get("/login")
def login():
    return templates.TemplateResponse({"request":request}, name="login.html")

@app.post("/login")
def login():
    return templates.TemplateResponse({"request":request}, name="login.html")



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)



