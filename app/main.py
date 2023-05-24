from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from ast import literal_eval


app = FastAPI()
templates = Jinja2Templates(directory=".")

users = {"12345":("67890","1234567890")}


@app.get('/')
def register(request: Request):
    data=""
    return templates.TemplateResponse("auth.html", {"request": request,"data":data})

@app.post('/')
async def register(request:Request):
    form_data = await request.form()
    data=""
    username=form_data['username']
    password=form_data['password']
    if username in users.keys():
        data="This username already exists"
    elif len(username)<5 or len(password)<5:
        data="Username and password should consist of at least 5 characters"
    else:
        users[username]=(password,username+password)
        data="Registered correctly"
    response = templates.TemplateResponse("auth.html", {"request": request,"data":data})
    return response

# @app.post('/login')
# def login(request: Request):
#     if f:
#        response.set_cookie(key="token", value=form_data['username']+form_data['password'])
#     content = {"message": request.cookies}
#     response = JSONResponse(content=content)
#     return response

@app.get('/endpoint')
def list(request: Request):
    data = [
            {
                "id": 1,
                "title": "Task 1",
                "description": "Description 1",
                "dueDate": "2023-05-31",
                "status": "incomplete"
            }
        ]
    return templates.TemplateResponse("list.html", {"request": request,"data":data})

@app.post('/endpoint')
async def list(request:Request):
    data = await request.body()
    data = literal_eval(data.decode('utf-8'))
    print(data)
    return templates.TemplateResponse("list.html", {"request":request, "data":data})
