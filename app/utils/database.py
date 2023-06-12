import psycopg2
from psycopg2 import sql
from .crypt import get_password_hash

# PGEND_POINT = os.environ['PGEND_POINT'] # End_point
# PGDATABASE_NAME = os.environ['PGDATABASE_NAME']
# PGUSER_NAME = os.environ['PGDATABASE_NAME']
# PGPASSWORD = os.environ['PGPASSWORD']
# PORT = os.environ['PORT']
PGEND_POINT = 'master-db.c6rqhjqgl56o.us-east-1.rds.amazonaws.com'
PGDATABASE_NAME = 'awesome-db'
PGUSER_NAME = 'HMS'
PGPASSWORD = 'DzieciPapierza'
PORT = '5432'

conn_string = "host="+ PGEND_POINT +" port="+ PORT +" dbname="+ PGDATABASE_NAME +" user=" + PGUSER_NAME \
                +" password="+ PGPASSWORD
conn = psycopg2.connect(conn_string)

def get_user(username):
    query = sql.SQL(f"""
    SELECT * FROM login
    WHERE "Username" = %s;
    """)
    cursor = conn.cursor()
    cursor.execute(query, (username,))
    result = cursor.fetchall()
    cursor.close()
    conn.commit()
    return result

def insert_user(username,password):
    h=get_password_hash(password)
    query = sql.SQL(f"""
    INSERT INTO login 
    VALUES (%s,%s,%s);""")
    cursor = conn.cursor()
    token = get_password_hash(h)
    cursor.execute(query, (username, h, token))
    cursor.close()
    conn.commit()
    return token

def delete_user(username):
    get_user(username)
    query = sql.SQL(f"""
    DELETE FROM tasks
    WHERE "Token" = %s;
    """)
    cursor = conn.cursor()
    cursor.execute(query, (get_user(username)[0][2],))
    cursor.close()
    conn.commit()
    query = sql.SQL(f"""
    DELETE FROM login
    WHERE "Username" = %s;
    """)
    cursor = conn.cursor()
    cursor.execute(query, (username,))
    cursor.close()
    conn.commit()

status_mapper = {0:'incomplete', 1:'in progress', 2:'completed'}
reverse_status_mapper = {v: k for k, v in status_mapper.items()}
data_mapper = lambda x:{
                "id": x[1],
                "title": x[2],
                "description": x[3],
                "dueDate": x[5].strftime('%Y-%m-%d'),
                "status": status_mapper[x[4]]
                }

def get_tasks(list_token):
    query = sql.SQL(f"""
    SELECT * FROM tasks
    WHERE "Token" = %s;
    """)
    cursor = conn.cursor()
    cursor.execute(query, (list_token,))
    result = cursor.fetchall()
    cursor.close()
    conn.commit()
    result = [data_mapper(i) for i in result]
    return result

def delete_tasks(token):
    query = sql.SQL(f"""DELETE FROM tasks WHERE "Token"=%s;""")
    cursor = conn.cursor()
    cursor.execute(query, (token,))
    cursor.close()
    conn.commit()

def insert_tasks(data,token):
    delete_tasks(token)
    cursor = conn.cursor()
    value_str=""
    if len(data)!=0:
        for id,record in enumerate(data):
            input_vals = (token,id, record['title'], record['description'], reverse_status_mapper[record['status']], record['dueDate'])
            value_str += cursor.mogrify("(%s,%s, %s, %s, %s, %s),", input_vals).decode('utf-8')
        query = sql.SQL(f"""INSERT INTO tasks
        VALUES {value_str[:-1]};""")
        cursor.execute(query)
        cursor.close()
        conn.commit()
