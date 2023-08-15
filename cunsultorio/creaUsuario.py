import hashlib
from flask import Flask
from flaskext.mysql import MySQL

programa = Flask(__name__)
mysql = MySQL()
programa.config['MYSQL_DATABASE_HOST']='localhost'
programa.config['MYSQL_DATABASE_PORT']=3306
programa.config['MYSQL_DATABASE_USER']='root'
programa.config['MYSQL_DATABASE_PASSWORD']=''
programa.config['MYSQL_DATABASE_DB']='consultorio'
mysql.init_app(programa)

idusuario = input("Digite id: ")
nombre = input("Digite nombre: ")
contrasena = input("Digite contraseña: ")
cifrada = hashlib.sha512(contrasena.encode("utf-8")).hexdigest()

sql = f"INSERT INTO usuarios (idusuario,nombre,contrasena,activo) VALUES ('{idusuario}','{nombre}','{cifrada}',1)"
con = mysql.connect()
cur = con.cursor()
cur.execute(sql)
con.commit()