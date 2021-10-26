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
        #validación de login instructor
        if request.form['usuario'] == "Instructor":
            session['pantalla']= "Instructor"
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT Email FROM '+base+'.Instructores')
            emailsValidos = []
            for result in cursor.fetchall():
                for email in result:
                    emailsValidos.append(email)
            cursor.execute('SELECT Contraseña FROM '+base+'.Instructores')
            passValidas = []
            for result in cursor.fetchall():
                for password in result:
                    passValidas.append(password)
            if request.form['email'] in emailsValidos:
                cursor.execute('SELECT Contraseña FROM '+base+'.Instructores WHERE Email = '+'"'+(request.form['email']+'"'))
                passValida = cursor.fetchall()[0][0]
                if request.form['pass'] == passValida:
                    #Buscar los examenes en la base para mostrar en pantalla
                    cursor.execute('SELECT * FROM '+base+'.Examen where Aprobado ="P"')
                    examenes = cursor.fetchall()
                    cursor.execute('SELECT Nombre, IdAlumno FROM '+base+'.Alumnos INER JOIN '+base+'.Examen USING(idAlumno)')
                    alumnos = cursor.fetchall()
                    cursor.execute('SELECT Nombre, idCurso FROM '+base+'.Curso INER JOIN '+base+'.Examen USING(idCurso)')
                    nombreCursos = cursor.fetchall()
                    cursor.execute('SELECT Nivel, idLeccion FROM '+base+'.Leccion INER JOIN '+base+'.Examen USING(idLeccion)')
                    niveles = cursor.fetchall()
                    cursor.execute('SELECT * FROM '+base+'.Curso')
                    curso = cursor.fetchall()
                    cursor.execute('SELECT Nombre, IdInstructor FROM '+base+'.Instructores WHERE Email = '+'"'+(request.form['email']+'"'))
                    resultados=cursor.fetchall()
                    nombre = resultados[0][0]
                    #Guardar en la sesión al instrructor y dirigirlo al inicio
                    session['idInstructor'] = resultados[0][1]
                    descripcion=""
                    return render_template('inicio.html', nombre=nombre, examenes=examenes, alumnos=alumnos, nombreCursos=nombreCursos, niveles=niveles, curso=curso, descripcion=descripcion)
                else:
                    flash("Usuario no registrado")
                    return redirect(url_for('login'))
            else:
                flash("Usuario no registrado")
                return redirect(url_for('login'))
#INSERT INTO Examen ( idLeccion, idAlumno, idInstructor, Aprobado, urlVideo, intentos, idCurso) VALUES ( 1, 11, 2, 'P', 'dasdsa', 0, 2)
#ALTER TABLE Examen AUTO_INCREMENT=6
        #validación de login alumno
        if request.form['usuario'] == "Alumno":
            session['pantalla']= "Alumno"
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
    cursor.execute('SELECT idAlumno FROM '+base+'.Alumno_Curso WHERE IdCurso={} AND IdAlumno={}'.format(session['idCurso'],session['idAlumno']))
    idAlumno= cursor.fetchall()[0][0]       
    cursor.execute('SELECT * FROM '+base+'.Leccion WHERE IdCurso={}'.format(session['idCurso']))
    lecciones=cursor.fetchall()
    return render_template('curso.html', curso=curso, nivel=nivel, lecciones=lecciones, idAlumno=idAlumno)

@app.route('/examen/<curso>/<nivel>/<idAlumno>', methods=["GET", "POST"])
def examen(curso, nivel, idAlumno): 
    if session['pantalla'] == "Instructor":
        pantalla='instructor'      
    else:
        pantalla='alumno'    

    cursor = mysql.connection.cursor()    
    cursor.execute('SELECT Descripcion, urlVideo, idLeccion FROM '+base+'.Leccion WHERE idCurso={} AND Nivel={}'.format(session['idCurso'], nivel))
    infoCurso = cursor.fetchall()[0]
    descripcion = infoCurso[0]
    video = infoCurso[1]
    leccion= infoCurso[2]
    cursor.execute('SELECT Aprobado FROM '+base+'.Examen WHERE idAlumno={} AND idLeccion={} AND idCurso={}'.format(idAlumno, leccion, session['idCurso']))
    if cursor.fetchall() == ():
        estado='' 
        #nota=''
        examen=''    
    else:
        cursor.execute('SELECT Aprobado, urlVideo FROM '+base+'.Examen WHERE idAlumno={} AND idLeccion={} AND idCurso'.format(idAlumno, leccion, session['idCurso']))
        examen= cursor.fetchall()[0]
        estado= examen[0]
        examen= examen[1]
        #nota= examen[3]
     
    archivo = '{}{}{}.jpg'.format(idAlumno, session['idCurso'], leccion )
    if request.method == "POST" and pantalla == 'alumno':
        if not "file" in request.files:
            flash("No hay ningun elemento de archivo!")
        f = request.files["file"]
        if f.filename == "":
            flash("Archivo no seleccionado!")
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(os.path.join(UPLOAD_FOLDER, archivo))
            flash("Examen entregado!")
        else:
            flash("Archivo no permitido!")
    if request.method == 'POST':
        if request.form['subida']=='Cargar':
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO '+base+'.Examen (idLeccion, idAlumno, Aprobado, urlVideo, idCurso) VALUES ("{}", "{}", "{}", "{}", "{}")'.format(leccion, idAlumno, 'P', archivo, session['idCurso']))
            mysql.connection.commit()
            return render_template('leccion.html', video=video, descripcion=descripcion, estado=estado, examen=examen, pantalla=pantalla)
    return render_template('leccion.html', video=video, descripcion=descripcion, estado=estado, examen=examen, pantalla=pantalla)

if __name__ == "__main__":
    app.run(debug=True)
