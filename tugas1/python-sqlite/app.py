from flask import Flask, flash, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sqlite3
import secrets

app = Flask(__name__)
secret_key = secrets.token_hex(32)
app.secret_key = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

USER_CREDENTIALS = {
    "admin": "admin"
}

def login_required(f):
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/')
@login_required
def index():
    # students = db.session.execute(text('SELECT * FROM student')).fetchall()
    # return render_template('index.html', students=students)

    try:
        students = db.session.execute(text('SELECT * FROM student')).fetchall()
        return render_template('index.html', students=students)
    except Exception:
        return redirect(url_for('error', message="Error"))


@app.route('/add', methods=['POST'])
@login_required
def add_student():
    # name = request.form['name']
    # age = request.form['age']
    # grade = request.form['grade']

    # connection = sqlite3.connect('instance/students.db')
    # cursor = connection.cursor()
    # query = f"INSERT INTO student (name, age, grade) VALUES ('{name}', {age}, '{grade}')"
    # cursor.execute(query)
    # connection.commit()
    # connection.close()
    # return redirect(url_for('index'))

    name = request.form['name']
    age = request.form['age']
    grade = request.form['grade']

    try:
        connection = sqlite3.connect('instance/students.db')
        cursor = connection.cursor()
        query = f"INSERT INTO student (name, age, grade) VALUES ('{name}', {age}, '{grade}')"
        cursor.execute(query)
        connection.commit()
        connection.close()
        return redirect(url_for('index'))
    except Exception as e:
        return redirect(url_for('error', message="Error"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/delete/<int:id>')  
def delete_student(id):
    try:
        student = db.session.execute(text("SELECT * FROM student WHERE id=:id"), {'id': id}).fetchone()

        if student:
            db.session.execute(text("DELETE FROM student WHERE id=:id"), {'id': id})
            db.session.commit()
        else:
            return "Student not found", 404

        return redirect(url_for('index'))

    except Exception as e:
        db.session.rollback() 
        return f"An error occurred: {str(e)}", 500


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    # if request.method == 'POST':
    #     name = request.form['name']
    #     age = request.form['age']
    #     grade = request.form['grade']

    #     # RAW Query
    #     db.session.execute(text(f"UPDATE student SET name='{name}', age={age}, grade='{grade}' WHERE id={id}"))
    #     db.session.commit()
    #     return redirect(url_for('index'))
    # else:
    #     # RAW Query
    #     student = db.session.execute(text(f"SELECT * FROM student WHERE id={id}")).fetchone()
    #     return render_template('edit.html', student=student)

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']
        try :
            db.session.execute(text(f"UPDATE student SET name='{name}', age={age}, grade='{grade}' WHERE id={id}"))
            db.session.commit()
            return redirect(url_for('index'))
        except SQLAlchemyError as e:
            db.session.rollback()
            return redirect(url_for('error', message="Error"))
    else :
        student = db. session. execute(text(f"SELECT * FROM student WHERE id={id}") ).fetchone
        return render_template('edit.html', student=student)
    
@app.route('/error', methods=['GET' ])
def error():
    message = request.args.get( 'message', 'An error occured' )
    return render_template('error.html', message=message)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)

