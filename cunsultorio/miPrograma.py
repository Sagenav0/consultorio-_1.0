from random import randint
from flask import Flask, render_template,request,redirect, session,send_from_directory
import os
from flaskext.mysql import MySQL
import hashlib
from datetime import timedelta,datetime

programa = Flask(__name__)
programa.secret_key = str(randint(10000,99999))
programa.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

mysql = MySQL()
programa.config['MYSQL_DATABASE_HOST']='localhost'
programa.config['MYSQL_DATABASE_PORT']=3306
programa.config['MYSQL_DATABASE_USER']='root'
programa.config['MYSQL_DATABASE_PASSWORD']=''
programa.config['MYSQL_DATABASE_DB']='consultorio'
mysql.init_app(programa)

carpeta_up = os.path.join('uploads')
programa.config['carpeta_up'] = carpeta_up

@programa.route('/uploads/<nombre>')
def uploads(nombre):
    return send_from_directory(programa.config['carpeta_up'],nombre)

@programa.route('/')
def index():
    mensaje = 'Esta es una primera prueba'
    return render_template('login.html')

@programa.route('/validaLogin', methods=['post'])
def validaLogin():
    id= request.form['txtId']
    contra = request.form['txtContra']
    cifrada = hashlib.sha512(contra.encode('utf-8')).hexdigest()
    sql = f"SELECT contrasena,nombre FROM usuarios WHERE idusuario='{id}'"
    cone = mysql.connect()
    cursor = cone.cursor()
    cursor.execute(sql)
    resultado = cursor.fetchall()
    cone.commit()
    
    if len(resultado) > 0:
        if(cifrada==resultado[0][0]):
            session["logueado"]=True
            session["user_id"]=id
            session["user_name"]=resultado[0][1]
            return redirect('/principal')
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')
    
@programa.route('/principal')
def principal():
    if session.get("logueado"):
        usuario = session.get("user_name")
        return render_template("principal.html",nombre_usuario = usuario)
    else:
        return render_template("login.html")

@programa.route("/medicos")
def medicos():
    if session.get("logueado"):
        sql = "SELECT * FROM medicos WHERE activo = 1"
        cone = mysql.connect()
        cursor = cone.cursor()
        cursor.execute(sql)
        resultado = cursor.fetchall()
        cone.commit()
        return render_template('/medicos.html', res = resultado )
    else:
        return render_template("login.html")

@programa.route('/agregamedico')
def agregamedico():
    if session.get("logueado"):
        return render_template('agregamedico.html')
    else:
        return render_template("login.html")

@programa.route('/guardamedico', methods=['post'])
def guardamedico():
    if session.get("logueado"):
        id = request.form['txtId']
        nombre = request.form['txtNombre']
        foto = request.files['txtFoto']
        especialidad = request.form['txtEspecialidad']
        sql = f"SELECT * FROM medicos WHERE idmedico='{id}'"
        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute(sql)
        resultado = cursor.fetchone()
        con.commit()
        
        if not resultado:
            
            ahora = datetime.now()
            tiempo = ahora.strftime("%Y%m%d%H%M%S")
            nom,extension = os.path.splitext(foto.filename)
            nombre_foto = "F" + tiempo + extension
            foto.save("uploads/"+nombre_foto)
            sql = f"INSERT INTO medicos (idmedico,nombre,especialidad,foto,activo) VALUES ('{id}','{nombre}','{especialidad}','{nombre_foto}',1)"
            cursor.execute(sql)
            con.commit()
            return redirect('/medicos')
        
        else:
            return render_template('agregamedico.html', men="ID de medico no disponible")
    else:
        return render_template("login.html")
    
@programa.route('/borramed/<id>')
def borramed(id):
    if session.get("logueado"):
        sql=f"UPDATE medicos SET activo=0 WHERE idmedico='{id}'"
        con = mysql.connect()
        cur = con.cursor()
        cur.execute(sql)
        con.commit()
        return redirect('/medicos')
    else:
        return render_template("login.html")
    
@programa.route('/editamed/<id>')
def editamed(id):
    if session.get("logueado"):
        sql = f"SELECT * FROM medicos WHERE idmedico = '{id}'"
        con = mysql.connect()
        cur = con.cursor()
        cur.execute(sql)
        resultado = cur.fetchall()
        con.commit()
        return render_template('editamedico.html', med = resultado[0])
    else:
        return render_template("login.html")

@programa.route('/actualizamedico', methods=['POST'])
def actualizamedico():
    if session.get("logueado"):
        id = request.form['txtId']
        nombre = request.form['txtNombre']
        especialidad = request.form['txtEspecialidad']
        foto = request.files['txtFoto']
        sql = f"UPDATE medicos SET nombre = '{nombre}', especialidad = '{especialidad}' WHERE idmedico = '{id}'"
        con = mysql.connect()
        cur = con.cursor()
        cur.execute(sql)
        con.commit()

        if foto.filename != '':
            ahora = datetime.now()
            tiempo = ahora.strftime("%Y%m%d%H%M%S")
            nom,extension = os.path.splitext(foto.filename)
            nombre_foto = "F" + tiempo + extension
            foto.save("uploads/"+nombre_foto)
            cur.execute( f"SELECT foto FROM medicos WHERE idmedico = '{id}' ")
            fotovieja = cur.fetchall()
            con.commit()
            os.remove(os.path.join(programa.config['carpeta_up'], fotovieja[0][0]))
            cur.execute(f"UPDATE medicos SET foto = '{nombre_foto}'")
            con.commit
        return redirect("/medicos")
    
    else:
        return render_template("login.html")

if __name__ == '__main__':
    programa.run(host='0.0.0.0',debug=True, port='8080')