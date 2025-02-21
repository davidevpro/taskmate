import unittest
from app import app, db, Task

class TaskMateTestCase(unittest.TestCase):
    def setUp(self):
        # Configurar la aplicación en modo de prueba
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Base de datos en memoria
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        # Limpiar la base de datos después de cada prueba
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_task(self):
        # Probar agregar una tarea
        response = self.app.post('/add', data={'title': 'Test Task', 'description': 'This is a test'})
        self.assertEqual(response.status_code, 302)  # Redirección esperada
        with app.app_context():
            task = db.session.get(Task, 1)  # Usar db.session.get() en lugar de Task.query.get()
            self.assertIsNotNone(task)
            self.assertEqual(task.title, 'Test Task')

    def test_update_task(self):
        # Probar actualizar una tarea
        with app.app_context():
            task = Task(title='Test Task', description='This is a test')
            db.session.add(task)
            db.session.commit()

            # Usar db.session.get() para obtener la tarea
            response = self.app.post(f'/update/{task.id}')
            self.assertEqual(response.status_code, 302)  # Redirección esperada

            updated_task = db.session.get(Task, task.id)  #