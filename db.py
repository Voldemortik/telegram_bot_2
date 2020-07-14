import pyodbc

import bot
import config

from string import Template
from bot import user_dict

user = user_dict

name = "Bitch"

cursor.execute("SELECT Name FROM Profiles WHERE Name = '{name}'")
def db_save():
    conn = pyodbc.connect("Driver={SQL Server};Server=DESKTOP-59BIPOH;Database=mydb;Trusted_Connection=yes;")

    cursor = conn.cursor()

    cursor.execute("SELECT Name FROM Profiles WHERE Name = '{name}'")
    cursor.execute("INSERT INTO Profiles VALUES ( ?, ?, ?, ?)", (name, user.city, user.male, user.age))
    conn.commit()