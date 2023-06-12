import unittest
import psycopg2
from passlib.context import CryptContext
from utils.database import insert_user, get_user, delete_tasks, insert_tasks, delete_user, get_tasks
from fastapi.testclient import TestClient
from main import app
import os

class TestDatabase(unittest.TestCase):

    PGEND_POINT = os.environ['PGEND_POINT'] # End_point
    PGDATABASE_NAME = os.environ['PGDATABASE_NAME']
    PGUSER_NAME = os.environ['PGDATABASE_NAME']
    PGPASSWORD = os.environ['PGPASSWORD']
    PORT = os.environ['PORT']
    conn_string = "host="+ PGEND_POINT +" port="+ PORT +" dbname="+ PGDATABASE_NAME +" user=" + PGUSER_NAME \
            +" password="+ PGPASSWORD

    def setUp(self):
        self.conn = psycopg2.connect(TestDatabase.conn_string)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def tearDown(self):
        self.conn.close()

    def test_create_connection(self):
        try:
            conn = psycopg2.connect(TestDatabase.conn_string)
            self.assertIsNotNone(conn)
        except psycopg2.Error as e:
            self.fail(f"Connection error: {e}")

    def test_user(self):
        try:
            insert_user("testusername","testpassword")
        except psycopg2.Error as e:
            self.fail(f"Insert user error: {e}")
        try:
            result = get_user("testusername")
        except psycopg2.Error as e:
            self.fail(f"Get user error: {e}")
        self.assertEqual(len(result),1)
        try:
            delete_user("testusername")
        except psycopg2.Error as e:
            self.fail(f"Delete user error: {e}")

    def test_tasks(self):
        token = insert_user("testusername","testpassword")
        delete_tasks(token)
        data = [{'id': 1, 'title': 'TestTitle1', 'description': 'TestDesc1', 'dueDate': '2023-06-10', 'status': 'completed'}]
        try:
            insert_tasks(data,token)
        except psycopg2.Error as e:
            self.fail(f"Insert tasks error: {e}")
        try:
            result = get_tasks(token)
        except psycopg2.Error as e:
            self.fail(f"Get tasks error: {e}")
        self.assertEqual(len(result),1)
        try:
            delete_tasks("testusername")
        except psycopg2.Error as e:
            self.fail(f"Delete tasks error: {e}")
        delete_user("testusername")

class TestEndpoints(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.conn = psycopg2.connect(TestDatabase.conn_string)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def test_get(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code,200)

    def test_get_login(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code,200)

    def test_get_register(self):
        response = self.client.get("/register")
        self.assertEqual(response.status_code,200)

    def test_get_list(self):
        self.client.post("/register",data={"username": "testusername", "password":"testpassword"})
        self.client.post("/login",data={"username": "testusername", "password":"testpassword"})
        response = self.client.get("/list")
        self.assertEqual(response.status_code,200)
        delete_user("testusername")

    def test_post_register_invalid(self):
        response = self.client.post("/register",data={"username": "a", "password":"b"})
        self.assertEqual(response.status_code,401)

    def test_post_register_existing(self):
        response = self.client.post("/register",data={"username": "abcdef", "password":"123456"})
        self.assertEqual(response.status_code,401)

    def test_post_register(self):
        response = self.client.post("/register",data={"username": "testusername", "password":"testpassword"})
        self.assertEqual(response.status_code,200)
        delete_user("testusername")

    def test_post_login_invalid(self):
        self.client.post("/register",data={"username": "testusername", "password":"testpassword"})
        response = self.client.post("/login",data={"username": "testusername", "password":"wrong_testpassword"})
        self.assertEqual(response.status_code,401)
        delete_user("testusername")

    def test_post_login_nonexisting(self):
        self.client.post("/register",data={"username": "testusername", "password":"testpassword"})
        response = self.client.post("/login",data={"username": "randomusername", "password":"testpassword"})
        self.assertEqual(response.status_code,401)
        delete_user("testusername")

    def test_post_login_token(self):
        self.client.post("/register",data={"username": "testusername", "password":"testpassword"})
        response = self.client.post("/login",data={"username": "testusername", "password":"testpassword"},follow_redirects=False)
        self.assertEqual(response.status_code,302)
        self.assertNotEqual(len(response.cookies["list_token"]),0)
        delete_user("testusername")

    def test_post_login(self):
        self.client.post("/register",data={"username": "testusername", "password":"testpassword"})
        response = self.client.post("/login",data={"username": "testusername", "password":"testpassword"})
        self.assertEqual(response.status_code,200)
        delete_user("testusername")

    def test_post_list(self):
        self.client.post("/register",data={"username": "testusername", "password":"testpassword"})
        self.client.post("/login",data={"username": "testusername", "password":"testpassword"})
        response = self.client.post("/list",json=[{"description":"d1","dueDate":"2023-06-18","id":1,"status":"in progress","title":"t1"}])
        self.assertEqual(response.status_code,200)
        delete_user("testusername")

if __name__ == '__main__':
    unittest.main()