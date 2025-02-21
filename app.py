from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Crear la aplicación Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'  # Usamos SQLite
app.config['SECRET_KEY'] = 'secret_key'  # Clave secreta para sesiones y mensajes flash

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modelo User
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  # Contraseña cifrada

# Modelo Task
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Fecha de creación
    due_date = db.Column(db.DateTime, nullable=True)  # Fecha límite (opcional)
    priority = db.Column(db.String(20), default="Media")  # Prioridad: Baja, Media, Alta
    category = db.Column(db.String(50), nullable=True)  # Categoría (opcional)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Relación con User

# Crear la base de datos y las tablas
with app.app_context():
    db.create_all()

# Cargar usuario
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Ruta de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verificar si el usuario ya existe
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('El usuario ya existe', 'danger')
            return redirect(url_for('register'))

        # Cifrar la contraseña usando pbkdf2:sha256
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Crear un nuevo usuario
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registro exitoso. Inicia sesión con tus credenciales.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Ruta de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Buscar al usuario por nombre de usuario
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('index'))
        else:
            flash('Credenciales incorrectas', 'danger')

    return render_template('login.html')

# Ruta de cierre de sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('login'))

# Ruta principal (protegida con login_required)
@app.route('/')
@login_required
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).all()  # Filtrar tareas por usuario
    return render_template('index.html', tasks=tasks)

# Ruta para agregar una nueva tarea
@app.route('/add', methods=['POST'])
@login_required
def add_task():
    title = request.form['title']
    description = request.form.get('description', '')
    due_date_str = request.form.get('due_date', None)  # Opcional
    priority = request.form.get('priority', 'Media')  # Por defecto: "Media"
    category = request.form.get('category', None)  # Opcional

    # Convertir due_date_str a un objeto datetime si se proporciona
    due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M') if due_date_str else None

    new_task = Task(
        title=title,
        description=description,
        due_date=due_date,
        priority=priority,
        category=category,
        completed=False,
        user_id=current_user.id
    )
    db.session.add(new_task)
    db.session.commit()
    flash('Tarea agregada correctamente', 'success')
    return redirect(url_for('index'))

# Ruta para marcar una tarea como completada o pendiente
@app.route('/update/<int:id>', methods=['POST'])
@login_required
def update_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id == current_user.id:  # Verificar que la tarea pertenezca al usuario actual
        task.completed = not task.completed
        db.session.commit()
        flash('Tarea actualizada correctamente', 'success')
    else:
        flash('No tienes permiso para editar esta tarea', 'danger')
    return redirect(url_for('index'))

# Ruta para eliminar una tarea
@app.route('/delete/<int:id>')
@login_required
def delete_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id == current_user.id:  # Verificar que la tarea pertenezca al usuario actual
        db.session.delete(task)
        db.session.commit()
        flash('Tarea eliminada correctamente', 'success')
    else:
        flash('No tienes permiso para eliminar esta tarea', 'danger')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=False)