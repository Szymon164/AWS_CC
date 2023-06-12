from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ast import literal_eval
import starlette.status as status
from mangum import Mangum
import os
from utils.database import *
from utils.crypt import *

app = FastAPI()
templates = Jinja2Templates(directory=os.path.dirname(__file__))

### REGISTER AND LOGIN

@app.get('/')
def register(request: Request):
    data=""
    return templates.TemplateResponse("login.html", {"request": request,"data":data})

@app.get('/login')
def register(request: Request):
    data=""
    return templates.TemplateResponse("login.html", {"request": request,"data":data})

@app.get('/register')
def register(request: Request):
    data=""
    return templates.TemplateResponse("login.html", {"request": request,"data":data})

@app.post('/register')
async def register(request:Request):
    form_data = await request.form()
    data=""
    username=form_data['username']
    password=form_data['password']
    user = get_user(username)

    if len(user)>0:
        data="This username already exists"
        response = templates.TemplateResponse("register.html", {"request": request,"data":data},status_code=401)
        return response
    elif len(username)<5 or len(password)<5:
        data="Username and password should consist of at least 5 characters"
        response = templates.TemplateResponse("register.html", {"request": request,"data":data},status_code=401)
        return response
    else:
        insert_user(username,password)
        data="Registered correctly"
    response = templates.TemplateResponse("register.html", {"request": request,"data":data})
    return response


@app.post("/login")
async def login(request: Request):
    form_data = await request.form()
    data=""
    username=form_data['username']
    password=form_data['password']
    user = get_user(username)
    if len(user)==0:
        data="This username doesn't exists"
        return templates.TemplateResponse("login.html", {"request": request,"data":data},status_code=401)

    if not verify_password(password,user[0][1]):
        data="Wrong password"
        return templates.TemplateResponse("login.html", {"request": request,"data":data},status_code=401)
    response = RedirectResponse("/list",status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="list_token", value=user[0][2])
    return response

### LIST

@app.get('/list')
def list(request: Request):
    list_token = request.cookies["list_token"]
    data = get_tasks(list_token)
    return templates.TemplateResponse("list.html", {"request": request,"data":data})

@app.post('/list')
async def list(request:Request):
    data = await request.body()
    data = literal_eval(data.decode('utf-8'))
    list_token = request.cookies["list_token"]
    insert_tasks(data,list_token)
    return templates.TemplateResponse("list.html", {"request":request, "data":data})

handler = Mangum(app)
