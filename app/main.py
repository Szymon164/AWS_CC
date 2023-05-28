from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ast import literal_eval
import starlette.status as status
import psycopg2
from psycopg2 import sql
from passlib.context import CryptContext

PGEND_POINT = 'master-db.c6rqhjqgl56o.us-east-1.rds.amazonaws.com' # End_point
PGDATABASE_NAME = 'awesome-db' # Database Name example: youtube_test_db
PGUSER_NAME = 'HMS' # UserName
PGPASSWORD = 'DzieciPapierza' # Password
PORT = '5432'


### CRYPT
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

### DATABASE
conn_string = "host="+ PGEND_POINT +" port="+ PORT +" dbname="+ PGDATABASE_NAME +" user=" + PGUSER_NAME \
                +" password="+ PGPASSWORD
conn = psycopg2.connect(conn_string)

def get_user(username):
    query = sql.SQL(f"""
    SELECT * FROM login
    WHERE "Username" = '{username}';
    """)
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    conn.commit()
    return result

def insert_user(username,password):
    h=get_password_hash(password)
    query = sql.SQL(f"""
    INSERT INTO login 
    VALUES ('{username}','{h}','{get_password_hash(h)}');""")
    cursor = conn.cursor()
    cursor.execute(query)
    cursor.close()
    conn.commit()

def status_mapper(x):
    if x==0:
        return 'incomplete'
    if x==1:
        return 'in progress'
    
    return 'completed'

data_mapper = lambda x:{
                "id": x[1],
                "title": x[2],
                "description": x[3],
                "dueDate": x[5].strftime('%Y-%m-%d'),
                "status": status_mapper(x[4])
                }

def get_tasks(list_token):
    query = sql.SQL(f"""
    SELECT * FROM tasks
    WHERE "Token" = '{list_token}';
    """)
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    conn.commit()
    result = [data_mapper(i) for i in result]
    return result

def insert_tasks(data,token):
    value_str=""
    for record in data:
        value_str+=f"('{token}','{record['id']}', '{record['title']}', '{record['description']}', '{record['status']}', '{record['dueDate']}',"
    query = sql.SQL(f"""INSERT INTO tasks
    VALUES {value_str[:-1]};""")
    cursor = conn.cursor()
    cursor.execute(query)
    cursor.close()
    conn.commit()

app = FastAPI()
templates = Jinja2Templates(directory=".")


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
    elif len(username)<5 or len(password)<5:
        data="Username and password should consist of at least 5 characters"
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
        return templates.TemplateResponse("login.html", {"request": request,"data":data})

    if not verify_password(password,user[0][1]):
        data="Wrong password"
        return templates.TemplateResponse("login.html", {"request": request,"data":data})
    response = RedirectResponse("/list",status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="list_token", value=user[0][2])
    return response

### LISTA

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
