from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

# Crear la aplicación Flask
app = Flask(__name__)

# Configurar la URI de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SECRET_KEY'] = 'secret_key'  # Clave secreta para usar mensajes flash

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# Definir el modelo Task
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    completed = db.Column(db.Boolean, default=False)

# Crear la base de datos y la tabla tasks
with app.app_context():
    db.create_all()

# Ruta principal: Mostrar todas las tareas
@app.route('/')
def index():
    tasks = Task.query.all()  # Obtener todas las tareas
    return render_template('index.html', tasks=tasks)

# Ruta para agregar una nueva tarea
@app.route('/add', methods=['POST'])
def add_task():
    title = request.form['title']
    description = request.form.get('description', '')  # Opcional
    new_task = Task(title=title, description=description, completed=False)
    db.session.add(new_task)
    db.session.commit()
    flash('Tarea agregada correctamente', 'success')
    return redirect(url_for('index'))

# Ruta para marcar una tarea como completada o pendiente
@app.route('/update/<int:id>', methods=['POST'])
def update_task(id):
    task = Task.query.get_or_404(id)
    task.completed = not task.completed
    db.session.commit()
    flash('Tarea actualizada correctamente', 'success')
    return redirect(url_for('index'))

# Ruta para eliminar una tarea
@app.route('/delete/<int:id>')
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    flash('Tarea eliminada correctamente', 'success')
    return redirect(url_for('index'))

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)