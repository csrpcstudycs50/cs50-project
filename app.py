import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Execute table creation
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            image_filename TEXT NOT NULL,
            reference_object TEXT NOT NULL,
            reference_size TEXT NOT NULL,
            measured_value TEXT NOT NULL,
            unit TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    
    conn.commit()
    conn.close()

init_db()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    projects = conn.execute('SELECT * FROM projects ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('index.html', projects=projects)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        project_name = request.form.get('project_name')
        reference_object = request.form.get('reference_object')
        reference_size = request.form.get('reference_size')
        measured_value = request.form.get('measured_value')
        unit = request.form.get('unit')
        file = request.files.get('image')

        if file and file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            conn = get_db_connection()
            conn.execute('''
                INSERT INTO projects (project_name, image_filename, reference_object, reference_size, measured_value, unit)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (project_name, filename, reference_object, reference_size, measured_value, unit))
            conn.commit()
            conn.close()

            return redirect(url_for('index'))

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)