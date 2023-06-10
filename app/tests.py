import unittest
import psycopg2
from psycopg2 import sql
from passlib.context import CryptContext
from main import insert_user, get_user, delete_tasks, insert_tasks, delete_user, get_tasks

class TestDatabase(unittest.TestCase):

    PGEND_POINT = 'master-db.c6rqhjqgl56o.us-east-1.rds.amazonaws.com'
    PGDATABASE_NAME = 'awesome-db'
    PGUSER_NAME = 'HMS'
    PGPASSWORD = 'DzieciPapierza'
    PORT = '5432'
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

if __name__ == '__main__':
    unittest.main()