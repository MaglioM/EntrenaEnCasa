#!/usr/bin/env python
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL

app = Flask(__name__)

#conexion a la base
app.config['MYSQL_HOST'] = '34.135.187.184'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'IFTS16MaccioMaglio'
app.config['MYSQL_DB'] = 'EntrenaEnCasa'
mysql = MySQL(app)

#settings
app.secret_key='secretkey'

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/registered', methods=['POST'])
def registered():
    if request.method == 'POST':
        if not request.form['pass'] == request.form['pass2']:
            flash("Las contraseñas no coinciden")
            return redirect(url_for('register'))
        elif not "@" in request.form['email'] or not "." in request.form['email']:
            flash("Email inválido")
            return redirect(url_for('register'))
        else:
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            email = request.form['email']
            password = request.form['pass']
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO EntrenaEnCasa.Alumnos (Nombre, Apellido, Contraseña, Email) VALUES (%s, %s, %s, %s)',(nombre, apellido, password, email))
            mysql.connection.commit()
            return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/ingresado', methods=['POST'])
def ingresado():
    if request.method == 'POST':
        #saca campos de la base
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT Email FROM EntrenaEnCasa.Alumnos')
        emailsValidos = []
        for result in cursor.fetchall():
            for email in result:
                emailsValidos.append(email)
        cursor.execute('SELECT Contraseña FROM EntrenaEnCasa.Alumnos')
        passValidas = []
        for result in cursor.fetchall():
            for password in result:
                passValidas.append(password)
        #validacion
        if request.form['email'] in emailsValidos and request.form['pass'] in passValidas:
            return render_template('index.html')
        else:
            flash("Usuario no registrado")
            return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True, PORT=33507)
