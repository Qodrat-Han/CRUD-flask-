from flask_bcrypt import Bcrypt 
import mysql.connector

bcrypt = Bcrypt()
password_plain = "password123"
hashed_password = bcrypt.generate_password_hash(password_plain).decode('utf-8')

# Tambahkan ke database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="hewan"
)
cursor = db.cursor()
cursor.execute("INSERT INTO pasar (username, email, password) VALUES (%s, %s, %s)", 
               ("user1", "user1@example.com", hashed_password))
db.commit()
cursor.close()
db.close()
