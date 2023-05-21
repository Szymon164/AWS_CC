from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates


app = FastAPI()
templates = Jinja2Templates(directory=".")

users = {}

@app.get('/')
def register(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post('/login')
async def register(request:Request):
    form_data = await request.form()

    content = {"message": "Done"}

    response = JSONResponse(content=content)
    response.set_cookie(key="login", value=form_data['login'])
    response.set_cookie(key="password", value=form_data['password'])
    
    return templates.TemplateResponse("login.html", {"request": request})

@app.post('/login')
def login(request: Request):
    content = {"message": request.cookies}
    response = JSONResponse(content=content)
    return response
