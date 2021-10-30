#!/usr/bin/env python
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = os.path.abspath("./static/examen_alumno")
ALLOWED_EXTENSIONS = set(["mp4", "mov", "avi", "mkv"])


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

@app.route('/ingresado', methods=['POST','GET'])
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
                    cursor.execute('''SELECT a.Nombre, a.idAlumno, c.Nombre, c.idCurso, l.Nivel FROM Examen e
                                    INNER JOIN Leccion l ON l.IdLeccion = e.IdLeccion
                                    INNER JOIN Curso c on l.IdCurso = c.IdCurso
                                    INNER JOIN Alumnos a on a.IdAlumno = e.IdAlumno
                                    WHERE e.Aprobado="P"''')
                    examenes=cursor.fetchall()
                    cursor.execute('SELECT Nombre, IdInstructor FROM '+base+'.Instructores WHERE Email = '+'"'+(request.form['email']+'"'))
                    resultados=cursor.fetchall()
                    nombre = resultados[0][0]
                    session['nombre']=nombre
                    #Guardar en la sesión al instrructor y dirigirlo al inicio
                    session['idInstructor'] = resultados[0][1]
                    descripcion=""
                    return render_template('inicio.html', nombre=nombre, examenes=examenes, curso=curso, descripcion=descripcion)
                else:
                    flash("Usuario no registrado")
                    return redirect(url_for('login'))
            else:
                flash("Usuario no registrado")
                return redirect(url_for('login'))
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
    if pantalla=='alumno':
        cursor.execute('SELECT Descripcion, urlVideo, idLeccion FROM '+base+'.Leccion WHERE idCurso={} AND Nivel={}'.format(session['idCurso'], nivel))
        infoCurso = cursor.fetchall()[0]
        descripcion = infoCurso[0]
        video = infoCurso[1]
        leccion= infoCurso[2]
        archivo = '{}{}{}.mp4'.format(idAlumno, session['idCurso'], leccion )
        cursor.execute('''SELECT e.Aprobado, e.urlVideo FROM Examen e 
                        INNER JOIN Leccion l ON l.idLeccion=e.idLeccion
                        INNER JOIN Curso c ON c.idCurso=l.idCurso
                        WHERE e.idAlumno={} AND c.idCurso={} AND l.Nivel={}
                        ORDER BY 1 DESC'''.format(idAlumno,session['idCurso'],nivel))
        resultados=cursor.fetchall()
        if len(resultados)== 0:
            estado=''
            videoExamen=''
        else:
            examen=resultados[0]
            estado=examen[0]
            videoExamen=examen[1]

    if pantalla=='instructor':
        cursor.execute('''SELECT e.Aprobado, e.urlVideo, e.idExamen FROM Examen e
                        INNER JOIN Leccion l ON l.IdLeccion = e.IdLeccion AND l.IdCurso={} AND l.Nivel = {}
                        WHERE e.IdAlumno = {}
                        ORDER BY 1 DESC'''.format(curso,nivel,idAlumno))
        examen= cursor.fetchall()[0]
        estado= examen[0]
        videoExamen= examen[1]
        idExamen = examen[2]
        video=''
        descripcion=''
     
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
        if request.form['subida']=='Cargar':
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO '+base+'.Examen (idLeccion, idAlumno, urlVideo, idCurso) VALUES ("{}", "{}", "{}", "{}")'.format(leccion, idAlumno, archivo, session['idCurso']))
            mysql.connection.commit()
            return redirect(url_for('ingresado'))
    elif request.method == "POST" and pantalla == 'instructor':
        if request.form['evaluacion'] == 'Aprobado':
            cursor.execute('UPDATE '+base+'.Examen SET Aprobado = "A" WHERE IdExamen = {}'.format(idExamen))
            mysql.connection.commit()
            cursor.execute('UPDATE '+base+'.Alumno_Curso SET Nivel = {} WHERE IdCurso = {} AND IdAlumno = {}'.format(str(int(nivel)+1),curso,idAlumno))
            mysql.connection.commit()
            cursor.execute('''SELECT a.Nombre, a.idAlumno, c.Nombre, c.idCurso, l.Nivel FROM Examen e
                                    INNER JOIN Leccion l ON l.IdLeccion = e.IdLeccion
                                    INNER JOIN Curso c on l.IdCurso = c.IdCurso
                                    INNER JOIN Alumnos a on a.IdAlumno = e.IdAlumno
                                    WHERE e.Aprobado="P"''')
            examenes=cursor.fetchall()
            return render_template('inicio.html', nombre=session['nombre'], examenes=examenes, curso=curso, descripcion=descripcion)
        elif request.form['evaluacion'] == 'Desaprobado':
            redirect(url_for('ingresado'))
            cursor.execute('UPDATE '+base+'.Examen SET Aprobado = "D" WHERE IdExamen = {}'.format(idExamen))
            mysql.connection.commit()
            cursor.execute('''SELECT a.Nombre, a.idAlumno, c.Nombre, c.idCurso, l.Nivel FROM Examen e
                                    INNER JOIN Leccion l ON l.IdLeccion = e.IdLeccion
                                    INNER JOIN Curso c on l.IdCurso = c.IdCurso
                                    INNER JOIN Alumnos a on a.IdAlumno = e.IdAlumno
                                    WHERE e.Aprobado="P"''')
            examenes=cursor.fetchall()
            return render_template('inicio.html', nombre=session['nombre'], examenes=examenes, curso=curso, descripcion=descripcion)
    return render_template('leccion.html', video=video, descripcion=descripcion, estado=estado, videoExamen=videoExamen, pantalla=pantalla)

if __name__ == "__main__":
    app.run(debug=True)
