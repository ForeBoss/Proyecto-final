from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
import sys
import qrcode
from io import BytesIO
import base64
import random
import string

app = Flask(__name__)

app.secret_key = 'abcd2123445'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'bdproyecto'

mysql = MySQL(app)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    mensaje = ''
    if request.method == 'POST' and 'correo' in request.form and 'contraseña' in request.form:
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM usuario WHERE correo = % s AND contraseña = % s', (correo, contraseña,))
        usuario = cursor.fetchone()
        if usuario:
            session['loggedin'] = True
            session['usuarioid'] = usuario['id']
            session['nombre'] = usuario['nombre']
            session['correo'] = usuario['correo']
            session['rol'] = usuario['rol']
            mensaje = 'Inicio de sesion correcto'
            return redirect(url_for('dashboard'))
        else:
            mensaje = '¡Ingrese un correo electrónico y una contraseña correcta!'
    return render_template('login.html', mesage=mensaje)


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute("SELECT COUNT(*) AS total_equipos FROM equipo")
        total_equipos = cursor.fetchone()['total_equipos']

        cursor.execute("SELECT COUNT(*) AS total_equipos_prestados FROM prestamo WHERE estatus = 'prestado'")
        total_equipos_prestados = cursor.fetchone()['total_equipos_prestados']

        cursor.execute("SELECT COUNT(*) AS total_equipos_devueltos FROM prestamo WHERE estatus = 'devuelto'")
        total_equipos_devueltos = cursor.fetchone()['total_equipos_devueltos']

        total_equipos_no_devueltos = total_equipos - total_equipos_devueltos

        return render_template("dashboard.html", total_equipos=total_equipos,
                               total_equipos_prestados=total_equipos_prestados,
                               total_equipos_devueltos=total_equipos_devueltos,
                               total_equipos_no_devueltos=total_equipos_no_devueltos)
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('usuarioid', None)
    session.pop('correo', None)
    return redirect(url_for('login'))


@app.route("/usuarios", methods=['GET', 'POST'])
def usuario():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM usuario')
        usuarios = cursor.fetchall()
        return render_template("usuarios.html", usuarios=usuarios)
    return redirect(url_for('login'))


@app.route("/detalles_usuario", methods=['GET', 'POST'])
def detalles_usuario():
    if 'loggedin' in session:
        viewUsaerioId = request.args.get('usuarioid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM usuario WHERE id = % s', (viewUsaerioId,))
        usuario = cursor.fetchone()
        return render_template("detallesUsuario.html", usuario=usuario)
    return redirect(url_for('login'))


@app.route("/editar_usuario", methods=['GET', 'POST'])
def editar_usuario():
    msg = ''
    if 'loggedin' in session:
        editarUsuaioId = request.args.get('usuarioid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM usuario WHERE id = % s', (editarUsuaioId,))
        usuarios = cursor.fetchall()
        return render_template("editar_usuario.html", usuarios=usuarios)
    return redirect(url_for('login'))


@app.route("/guardar_usuario", methods=['GET', 'POST'])
def guardar_usuario():
    msg = ''
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST' and 'rol' in request.form and 'nombre' in request.form and 'apellido' in request.form and 'correo' in request.form:

            nombre = request.form['nombre']
            apellido = request.form['apellido']
            correo = request.form['correo']
            rol = request.form['rol']
            action = request.form['action']

            if action == 'modificarUsuario':
                usuarioid = request.form['usuarioid']
                cursor.execute('UPDATE usuario SET nombre= %s, apellido= %s, correo= %s, rol= %s WHERE id = %s',
                               (nombre, apellido, correo, rol, (usuarioid,),))
                mysql.connection.commit()
            else:
                contraseña = request.form['contraseña']
                cursor.execute(
                    'INSERT INTO usuario (`nombre`, `apellido`, `correo`, `contraseña`, `rol`) VALUES (%s, %s, %s, %s, %s)',
                    (nombre, apellido, correo, contraseña, rol))
                mysql.connection.commit()

            return redirect(url_for('usuario'))
        elif request.method == 'POST':
            msg = 'Por favor rellena el formulario !'
        return redirect(url_for('usuario'))
    return redirect(url_for('login'))


@app.route("/borrar_usuario", methods=['GET'])
def borrar_usuario():
    if 'loggedin' in session:
        borrarUsuarioId = request.args.get('usuarioid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM usuario WHERE id = % s', (borrarUsuarioId,))
        mysql.connection.commit()
        return redirect(url_for('usuario'))
    return redirect(url_for('login'))


@app.route("/categoria", methods=['GET', 'POST'])
def categoria():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT categoriaid, nombre, estatus FROM categoria")
        categorias = cursor.fetchall()
        return render_template("categoria.html", categorias=categorias, agregarCategoríaForm=0)
    return redirect(url_for('login'))


@app.route("/guardar_categoria", methods=['GET', 'POST'])
def guardar_categoria():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if request.method == 'POST' and 'nombre' in request.form and 'estatus' in request.form:
            nombre = request.form['nombre']
            estatus = request.form['estatus']
            action = request.form['action']

            if action == 'editar_categoria':
                categoriaid = request.form['categoriaid']
                cursor.execute('UPDATE categoria SET nombre = %s, estatus = %s WHERE categoriaid =% s',
                               (nombre, estatus, (categoriaid,),))
                mysql.connection.commit()
            else:
                cursor.execute('INSERT INTO categoria (`nombre`, `estatus`) VALUES (%s, %s)', (nombre, estatus))
                mysql.connection.commit()
            return redirect(url_for('categoria'))
        elif request.method == 'POST':
            msg = 'Por favor rellena el formulario !'
        return redirect(url_for('categoria'))

    return redirect(url_for('login'))


@app.route("/editar_categoria", methods=['GET', 'POST'])
def editar_categoria():
    if 'loggedin' in session:
        categoriaid = request.args.get('categoriaid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT categoriaid, nombre, estatus FROM categoria WHERE categoriaid = %s', (categoriaid,))
        categorias = cursor.fetchall()
        return render_template("editar_categoria.html", categorias=categorias)
    return redirect(url_for('login'))


@app.route("/borrar_categoria", methods=['GET'])
def borrar_categoria():
    if 'loggedin' in session:
        categoriaid = request.args.get('categoriaid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM categoria WHERE categoriaid = % s', (categoriaid,))
        mysql.connection.commit()
        return redirect(url_for('categoria'))
    return redirect(url_for('login'))


@app.route("/estudiantes", methods=['GET', 'POST'])
def estudiantes():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT estudiantesid, nombre, estatus FROM estudiantes")
        estudiantes = cursor.fetchall()
        return render_template("estudiantes.html", estudiantes=estudiantes, agregarEstudianteForm=0)
    return redirect(url_for('login'))


@app.route("/guardar_estudiante", methods=['GET', 'POST'])
def guardar_estudiante():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if request.method == 'POST' and 'nombre' in request.form and 'estatus' in request.form:
            nombre = request.form['nombre']
            estatus = request.form['estatus']
            action = request.form['action']

            if action == 'editar_estudiante':
                estudianteid = request.form['estudianteid']
                cursor.execute('UPDATE estudiantes SET nombre = %s, estatus = %s WHERE estudiantesid =% s',
                               (nombre, estatus, (estudianteid,),))
                mysql.connection.commit()
            else:
                cursor.execute('INSERT INTO estudiantes (`nombre`, `estatus`) VALUES (%s, %s)', (nombre, estatus))
                mysql.connection.commit()
            return redirect(url_for('estudiantes'))
        elif request.method == 'POST':
            msg = 'Por favor rellena el formulario !'
        return redirect(url_for('estudiantes'))

    return redirect(url_for('login'))


@app.route("/editar_estudiante", methods=['GET', 'POST'])
def editar_estudiante():
    if 'loggedin' in session:
        estudianteid = request.args.get('estudianteid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT estudiantesid, nombre, estatus FROM estudiantes WHERE estudiantesid = %s',
                       (estudianteid,))
        estudiantes = cursor.fetchall()
        return render_template("editar_estudiante.html", estudiantes=estudiantes)
    return redirect(url_for('login'))


@app.route("/borrar_estudiante", methods=['GET'])
def borrar_estudiante():
    if 'loggedin' in session:
        estudianteid = request.args.get('estudianteid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM estudiantes WHERE estudiantesid = %s', (estudianteid,))
        mysql.connection.commit()
        return redirect(url_for('estudiantes'))
    return redirect(url_for('login'))


@app.route("/equipos", methods=['GET', 'POST'])
def equipos():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT equipo.equipoid, equipo.nombre, equipo.imagen, equipo.identificador, equipo.disponibilidad, equipo.agregado, equipo.actualizadoen, categoria.nombre AS categoria FROM equipo JOIN categoria ON equipo.categoriaid = categoria.categoriaid")
        equipos = cursor.fetchall()

        cursor.execute("SELECT categoriaid, nombre, estatus FROM categoria")
        categorias = cursor.fetchall()

        cursor.close()
        return render_template("equipos.html", equipos=equipos, categorias=categorias)

    return redirect(url_for('login'))


@app.route("/guardar_equipo", methods=['POST'])
def guardar_equipo():
    msg = ''
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST':
            nombre = request.form['nombre']
            imagen = request.form['imagen']
            identificador = request.form['identificador']
            disponibilidad = request.form['disponibilidad']
            categoria = request.form['categoria']
            action = request.form['action']
            if action == 'update_equipo':
                equipoid = request.form['equipoid']
                cursor.execute(
                    'UPDATE equipo SET nombre = %s, imagen = %s, identificador = %s, disponibilidad = %s, categoriaid = %s WHERE equipoid = %s',
                    (nombre, imagen, identificador, disponibilidad, categoria, equipoid))
                mysql.connection.commit()
            else:
                cursor.execute(
                    'INSERT INTO equipo (nombre, imagen, identificador, disponibilidad, categoriaid) VALUES (%s, %s, %s,  %s, %s)',
                    (nombre, imagen, identificador, disponibilidad, categoria))
                mysql.connection.commit()
            cursor.close()
            return redirect(url_for('equipos'))
        else:
            msg = 'Por favor, complete el formulario.'
        return render_template("equipos.html", msg=msg)
    return redirect(url_for('login'))


@app.route("/editar_equipo", methods=['GET', 'POST'])
def editar_equipo():
    msg = ''
    if 'loggedin' in session:
        editarEquipoId = request.args.get('equipoid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM equipo WHERE equipoid = %s', (editarEquipoId,))
        equipos = cursor.fetchall()
        cursor.execute("SELECT categoriaid, nombre, estatus FROM categoria")
        categorias = cursor.fetchall()
        return render_template("editar_equipo.html", equipos=equipos, categorias=categorias)
    return redirect(url_for('login'))


@app.route("/eliminar_equipo", methods=['GET'])
def eliminar_equipo():
    if 'loggedin' in session:
        deleteEquipoId = request.args.get('equipoid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM equipo WHERE equipoid = %s', (deleteEquipoId,))
        mysql.connection.commit()
        return redirect(url_for('equipos'))
    return redirect(url_for('login'))

def generar_qr(texto):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(texto)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img


@app.route('/ver_codigo_qr/<codigo_qr>')
def ver_codigo_qr(codigo_qr):
    img = generar_qr(codigo_qr)
    return img


@app.route("/prestamos", methods=['GET', 'POST'])
def prestamos():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT prestamo.prestamoid, prestamo.equipoid, prestamo.estudianteid, prestamo.fechadeprestamo, prestamo.fechadedevolucionesperada, prestamo.estatus, prestamo.codigo_qr, equipo.nombre AS nombre_equipo, estudiantes.nombre AS nombre_estudiante FROM prestamo  AS prestamo JOIN equipo ON prestamo.equipoid = equipo.equipoid JOIN estudiantes ON prestamo.estudianteid = estudiantes.estudiantesid")
        prestamos = cursor.fetchall()

        for prestamo in prestamos:
            qr = qrcode.make(prestamo['codigo_qr'])

            buf = BytesIO()
            qr.save(buf, format='PNG')
            qr_img = buf.getvalue()

            prestamo['qr_img'] = base64.b64encode(qr_img).decode('utf-8')

        cursor.execute("SELECT equipo.equipoid, equipo.nombre FROM equipo")
        equipos = cursor.fetchall()
        cursor.execute("SELECT estudiantesid, nombre, estatus FROM estudiantes")
        estudiantes = cursor.fetchall()

        cursor.close()
        return render_template("prestamos.html", prestamos=prestamos, equipos=equipos, estudiantes=estudiantes)
    return redirect(url_for('login'))


@app.route("/registrar_prestamo", methods=['GET', 'POST'])
def registrar_prestamo():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT prestamo.prestamoid, prestamo.equipoid, prestamo.estudianteid, prestamo.fechadeprestamo, prestamo.fechadedevolucionesperada, prestamo.codigo_qr, prestamo.estatus FROM prestamo")
        prestamos = cursor.fetchall()

        if request.method == 'POST' and 'equipoid' in request.form and 'estudianteid' in request.form and 'fechadeprestamo' in request.form and 'fechadedevolucionesperada' in request.form and 'estatus' in request.form:
            equipoid = request.form['equipoid']
            estudianteid = request.form['estudianteid']
            fechadeprestamo = request.form['fechadeprestamo']
            fechadedevolucionesperada = request.form['fechadedevolucionesperada']
            estatus = request.form['estatus']
            action = request.form['action']

            codigo_qr = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

            if action == 'updatePrestamo':
                prestamoid = request.form['prestamoid']
                cursor.execute(
                    'UPDATE prestamo SET equipoid = %s, estudianteid = %s, fechadeprestamo = %s, fechadedevolucionesperada = %s, estatus = %s WHERE prestamoid = %s',
                    (equipoid, estudianteid, fechadeprestamo, fechadedevolucionesperada, estatus, prestamoid))
            else:
                cursor.execute(
                    'INSERT INTO prestamo (equipoid, estudianteid, fechadeprestamo, fechadedevolucionesperada, codigo_qr, estatus) VALUES (%s, %s, %s, %s, %s, %s)',
                    (equipoid, estudianteid, fechadeprestamo, fechadedevolucionesperada, codigo_qr, estatus))
            mysql.connection.commit()
            return redirect(url_for('prestamos'))
        elif request.method == 'POST':
            msg = 'Por favor complete el formulario.'
        return redirect(url_for('prestamos'))
    return redirect(url_for('login'))


@app.route("/editar_prestamo", methods=['GET', 'POST'])
def editar_prestamo():
    msg = ''
    if 'loggedin' in session:
        prestamoid = request.args.get('prestamoid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT prestamo.prestamoid, prestamo.equipoid, prestamo.estudianteid, prestamo.fechadeprestamo, prestamo.fechadedevolucionesperada, prestamo.estatus FROM prestamo WHERE prestamo.prestamoid = %s',
            (prestamoid,))
        prestamo = cursor.fetchone()

        cursor.execute("SELECT equipoid, nombre FROM equipo")
        equipos = cursor.fetchall()

        cursor.execute("SELECT estudiantesid, nombre FROM estudiantes")
        estudiantes = cursor.fetchall()
        return render_template("editar_prestamo.html", prestamo=prestamo, equipos=equipos, estudiantes=estudiantes,
                               msg=msg)
    return redirect(url_for('login'))


@app.route("/eliminar_prestamo", methods=['GET'])
def eliminar_prestamo():
    if 'loggedin' in session:
        prestamoid = request.args.get('prestamoid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM prestamo WHERE prestamoid = %s', (prestamoid,))
        mysql.connection.commit()
        return redirect(url_for('prestamos'))
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()
    os.execv(__file__, sys.argv)
