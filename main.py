from fastapi import FastAPI ,Request
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator

templates =Jinja2Templates(directory="templates")

import requests
import sqlite3

app = FastAPI()

class Meme(Model):
    id= fields.IntField(pk=True,unique=True,primary_key=True)
    name=fields.CharField(50)
    caption=fields.CharField(50)
    url=fields.CharField(2000)

Meme_Pydantic = pydantic_model_creator(Meme, name='Meme')
MemeIn_Pydantic = pydantic_model_creator(Meme, name='MemeIn', exclude_readonly=True)

@app.get('/',response_class=HTMLResponse)
async def home(request: Request):#,id: int,name: str,caption: str,url: str):
    return templates.TemplateResponse('layout.html',{"request":request})#"id": id,"name": name,"caption": caption,"url": url})

@app.get('/memes')
async def get_memes():
    return await Meme_Pydantic.from_queryset(Meme.all())

@app.get('/memes/{meme_id}')
async def get_meme(meme_id: int):
    return await Meme_Pydantic.from_queryset_single(Meme.get(id=meme_id))


@app.post('/memes')
async def create_meme(meme: MemeIn_Pydantic):
    meme_obj = await Meme.create(**meme.dict(exclude_unset=True))
    return await Meme_Pydantic.from_tortoise_orm(meme_obj)

@app.delete('/memes/{meme_id}')
async def delete_meme(meme_id: int):
    await Meme.filter(id=meme_id).delete()
    return {}

c = sqlite3.connect('db.sqlite3')
cur = c.cursor()
cur.execute("SELECT * from meme ")
test = cur.fetchall()

register_tortoise(
    app,
    db_url='sqlite://db.sqlite3',
    modules={'models': ['main']},
    generate_schemas=True,
    add_exception_handlers=True
)