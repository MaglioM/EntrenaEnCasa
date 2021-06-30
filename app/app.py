#!/usr/bin/env python
from flask import Flask, render_template, request
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = '34.135.187.184'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'IFTS16MaccioMaglio'
app.config['MYSQL_DB'] = 'EntrenaEnCasa'
mysql = MySQL(app)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/register')
def login():
    return render_template('register.html')

@app.route('/registered', methods=['POST'])
def registrado():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        password = request.form['pass']
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO EntrenaEnCasa.Alumnos (Nombre, Apellido, Contraseña, Email) VALUES (%s, %s, %s, %s)',(nombre, apellido, password, email))
        mysql.connection.commit()
        return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
