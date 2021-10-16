#!/usr/bin/env python
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = os.path.abspath("./static/examen_alumno")
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpge"])

def allowed_file(filename):

    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

#conexion a la base
app.config['MYSQL_HOST'] = 'becridlgsxtglg0nm3o3-mysql.services.clever-cloud.com'
app.config['MYSQL_USER'] = 'u7gkzsbwlkpi4dik'
app.config['MYSQL_PASSWORD'] = 'ymU8g7Y4OiZC5xDn4tHx'
app.config['MYSQL_DB'] = 'becridlgsxtglg0nm3o3'
mysql = MySQL(app)

#settings
app.secret_key='secretkey'


#Variables
base='becridlgsxtglg0nm3o3'

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/proximamente')
def proximamente():
    return render_template('proximamente.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/registered', methods=['POST'])
def registered():
    if request.method == 'POST':
        if request.form['nombre'] == '' or request.form['apellido'] == '' or request.form['email'] == '' or request.form['pass'] == '' or request.form['pass2'] == '':
            flash("Todos los campos son obligatorios")
            return redirect(url_for('register'))
        elif not request.form['pass'] == request.form['pass2']:
            flash("Las contraseñas no coinciden")
            return redirect(url_for('register'))
        elif not "@" in request.form['email'] or not "." in request.form['email']:
            flash("Email inválido")
            return redirect(url_for('register'))
        else:
            try:
                nombre       = request.form['nombre']
                apellido     = request.form['apellido']
                email        = request.form['email']
                password     = request.form['pass']
                cursor = mysql.connection.cursor()
                if request.form['usuario'] == "Alumno":
                    cursor.execute('INSERT INTO '+base+'.Alumnos (Nombre, Apellido, Contraseña, Email) VALUES ("{}", "{}", "{}", "{}")'.format(nombre, apellido, password, email))
                    mysql.connection.commit()
                    cursor.execute('SELECT IdAlumno FROM '+base+'.Alumnos WHERE Email = "{}"'.format(email))
                    idAlumno=cursor.fetchall()[0][0]
                    cursor.execute('SELECT IdCurso FROM '+base+'.Curso')
                    cursos=cursor.fetchall()
                    for curso in cursos:
                        cursor.execute('INSERT INTO '+base+'.Alumno_Curso (IdAlumno, IdCurso) VALUES ({},{})'.format(idAlumno,curso[0]))
                        mysql.connection.commit()
                elif request.form['usuario'] == "Instructor":
                    cursor.execute('INSERT INTO '+base+'.Instructores (Nombre, Apellido, Contraseña, Email) VALUES ("{}", "{}", "{}", "{}")'.format(nombre, apellido, password, email))
                    mysql.connection.commit()
                return render_template('index.html')
            except Exception as e:
                print("Este fue el error:{}".format(e))
                flash("Ya hay un usuario registrado con ese Email")
                return redirect(url_for('register'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/ingresado', methods=['POST'])
def ingresado():
    if request.method == 'POST':
        #validación de login
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT Email FROM '+base+'.Alumnos')
        emailsValidos = []
        for result in cursor.fetchall():
            for email in result:
                emailsValidos.append(email)
        cursor.execute('SELECT Contraseña FROM '+base+'.Alumnos')
        passValidas = []
        for result in cursor.fetchall():
            for password in result:
                passValidas.append(password)
        if request.form['email'] in emailsValidos:
            cursor.execute('SELECT Contraseña FROM '+base+'.Alumnos WHERE Email = '+'"'+(request.form['email']+'"'))
            passValida = cursor.fetchall()[0][0]
            if request.form['pass'] == passValida:
                #Buscar los cursos en la base para mostrar en pantalla
                cursor.execute('SELECT * FROM '+base+'.Curso')
                cursos = cursor.fetchall()
                cursor.execute('SELECT Nombre, IdAlumno FROM '+base+'.Alumnos WHERE Email = '+'"'+(request.form['email']+'"'))
                resultados=cursor.fetchall()
                nombre = resultados[0][0]
                #Guardar en la sesión al alumno y dirigirlo al inicio
                session['idAlumno'] = resultados[0][1]
                return render_template('inicio.html',nombre=nombre,cursos=cursos)
            else:
                flash("Usuario no registrado")
                return redirect(url_for('login'))
        else:
            flash("Usuario no registrado")
            return redirect(url_for('login'))


@app.route('/curso/<id>')
def curso(id):    
    session['idCurso'] = id
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT Nombre FROM '+base+'.Curso WHERE IdCurso={}'.format(session['idCurso']))
    curso = cursor.fetchall()[0][0]
    cursor.execute('SELECT Nivel FROM '+base+'.Alumno_Curso WHERE IdCurso={} AND IdAlumno={}'.format(session['idCurso'],session['idAlumno']))
    nivel= cursor.fetchall()[0][0]
    cursor.execute('SELECT * FROM '+base+'.Leccion WHERE IdCurso={}'.format(session['idCurso']))
    lecciones=cursor.fetchall()
    return render_template('curso.html',curso=curso,nivel=nivel,lecciones=lecciones)

@app.route('/examen/<curso>/<nivel>', methods=["GET", "POST"])
def examen(curso, nivel):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT Descripcion, urlVideo FROM '+base+'.Leccion WHERE idCurso={} AND Nivel={}'.format(session['idCurso'],nivel))
    infoCurso = cursor.fetchall()[0]
    descripcion = infoCurso[0]
    video = infoCurso[1]
    if request.method == "POST":
        if not "file" in request.files:
            return "No file part in the form."
        f = request.files["file"]
        if f.filename == "":
            return "No file selected."
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(os.path.join(UPLOAD_FOLDER, filename))
            return "cargado correctamente"
        return "File not allowed."
    return render_template('leccion.html', video=video, descripcion=descripcion)

if __name__ == "__main__":
    app.run(debug=True)
