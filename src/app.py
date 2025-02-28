from flask import Flask, redirect, url_for, render_template, request, flash
from config import Config
from flask_mysqldb import MySQL
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configuración de Config
app.config.from_object(Config)

# Inicialización de MySQL
mysql = MySQL(app)

# Inicialización Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modelo de usuario para Flask-Login
class User(UserMixin):
    def __init__(self, id, nombre, email, password):
        self.id = str(id)  
        self.nombre = nombre
        self.email = email
        self.password = password

@login_manager.user_loader
def loader_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()

    if user:
        return User(id=str(user[0]), nombre=user[1], email=user[2], password=user[3])
    return None

# Rutas
@app.route('/')
def home():
    return render_template('base.html')

# Ruta: Registro
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO users(nombre, email, password) VALUES(%s, %s, %s)', (nombre, email, hashed_password))
        mysql.connection.commit()
        cursor.close()

        flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

# Ruta: Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        print("Email ingresado:", email)
        print("Contraseña ingresada:", password)

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email= %s', (email,))
        user = cursor.fetchone()
        cursor.close()

        print("Usuario encontrado en DB:", user)

        if user:
            print("Contraseña hasheada en DB:", user[3])
            print("Coincide hash:", check_password_hash(user[3], password))

        if user and check_password_hash(user[3], password):
            user_obj = User(id=str(user[0]), nombre=user[1], email=user[2], password=user[3])
            login_user(user_obj)
            flash("Inicio de sesión exitoso.")
            return redirect(url_for('dashboard'))
        else:
            flash('Algo salio mal revisa tu correo o contraseña')
    
    return render_template('login.html')

#Crud de Productos 

@app.route('/productos', methods=['GET','POST'])
def productos():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM productos')
    productos = cursor.fetchall()
    cursor.close()
    return render_template('productos.html', productos=productos)

@app.route('/agregar_prodcuto', methods=['POST','GET'])
def agregar_ptoducto():
    if request.method == 'POST':
        nombre_producto = request.form.get('nombre')
        precio = request.form.get('precio')
        cantidad = request.form.get('cantidad')
        cursor= mysql.connection.cursor()
        cursor.execute('INSERT INTO productos(nombre, precio, cantidad) VALUES(%s, %s, %s)', (nombre_producto, precio, cantidad))
        mysql.connection.commit()
        cursor.close()
        flash("Producto agregado correctamente", "success")
        return redirect(url_for('agregar_producto'))
    return render_template('agregar_producto.html')

@app.route('/borrar_producto/<string:id>')
def borrar_producto(id):
    cursor=mysql.connection.cursor()
    cursor.execute('DELETE FROM produuctos WHERE id=%s')
    mysql.connection.commit()
    mysql.connection.commit()
    cursor.close()

#crud de usuarios 
@app.route('/agregar_usuario', methods=['GET','POST'])
def agregar_usuario():
    if request.method == 'POST':
        nombre= request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        cursor= mysql.connection.cursor()
        cursor.execute('INSERT INTO users(nombre, email, password) VALUES(%s, %s, %s)', (nombre, email, password))
        mysql.connection.commit()
        cursor.close()
        flash("Producto agregado correctamente", "success")
        return redirect(url_for('agregar_producto'))
    return render_template('agregar_producto.html')
@app.route('/')
# Ruta de acceso protegida
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('auth/dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente.', "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
