import mysql.connector

# Connect to MySQL server and create a new database
cnx = mysql.connector.connect(
    host='localhost',
    user='root',
    password=''
)

cursor = cnx.cursor()
cursor.execute("CREATE DATABASE notion_app")
cnx.commit()
cursor.close()
cnx.close()

# Connect to the newly created database and create a table
cnx = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='notion_app'
)

cursor = cnx.cursor()

create_table_query_1 = """
CREATE TABLE events (
    date date not null,
    description text not null,
    complete boolean not null default 0
)
"""

cursor.execute(create_table_query_1)
cnx.commit()

create_table_query_2 = """
CREATE TABLE tasks (
    subjects varchar(25) not null,
    time_spent time,
    date date
)
"""

cursor.execute(create_table_query_2)
cnx.commit()
cursor.close()
cnx.close()