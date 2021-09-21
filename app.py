#!/usr/bin/env python
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL

app = Flask(__name__)

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


@app.route('/curso/<id>')
def curso(id):    
    session['idCurso']=id
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT Nombre FROM '+base+'.Curso WHERE IdCurso='+id)
    curso = cursor.fetchall()[0][0]
    cursor.execute('SELECT * FROM '+base+'.Leccion WHERE IdCurso='+id)
    lecciones= cursor.fetchall()
    return render_template('curso.html',curso=curso,lecciones=lecciones)


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
                cursor       = mysql.connection.cursor()
                if request.form['usuario'] == "Alumno":
                    cursor.execute('INSERT INTO '+base+'.Alumnos (Nombre, Apellido, Contraseña, Email) VALUES (%s, %s, %s, %s)',(nombre, apellido, password, email))
                elif request.form['usuario'] == "Instructor":
                    cursor.execute('INSERT INTO '+base+'.Instructores (Nombre, Apellido, Contraseña, Email) VALUES (%s, %s, %s, %s)',(nombre, apellido, password, email))
                mysql.connection.commit()
                return render_template('index.html')
            except:
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

if __name__ == "__main__":
    app.run(debug=True)
