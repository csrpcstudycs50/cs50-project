import os
import sqlite3
from flask import Flask, request, render_template, g

app = Flask(__name__)

# Configuration & Constants
DATABASE = 'database.db'
UPLOAD_FOLDER = './static/uploads'

# Ensure local file upload directory exists on startup
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ==========================================
# DATABASE MANAGEMENT
# ==========================================

def get_db():
    """
    Retrieves or establishes a SQLite database connection for the current request context.
    Enforces foreign key constraints and configures dictionary-like row access.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.execute('PRAGMA foreign_keys = ON;')
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    """Closes the database connection automatically when the request completes."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def reset_db():
    """Drops all relational tables to allow a clean schema reset."""
    db = get_db()
    db.executescript("""
        PRAGMA foreign_keys = OFF;

        DROP TABLE IF EXISTS recipes_ingredients;
        DROP TABLE IF EXISTS recipes;
        DROP TABLE IF EXISTS ingredients;

        PRAGMA foreign_keys = ON;
    """)
    db.commit()


def init_db():
    """Executes schema.sql to initialize database tables and constraints."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.executescript(f.read())
        db.commit()


# Automatically initialize the database on first run if database file is missing
if not os.path.exists(DATABASE):
    init_db()


# ==========================================
# ROUTES & APPLICATION LOGIC
# ==========================================

@app.route('/')
def index():
    """Renders the main dashboard page."""
    return render_template('index.html')


@app.route('/add', methods=['GET', 'POST'])
def add():
    """
    Handles recipe creation:
    - GET: Displays the recipe creation form.
    - POST: Validates input fields, uploads optional media, populates database tables
            (recipes, ingredients, and join table recipes_ingredients), and commits changes.
    """
    if request.method == 'POST':
        # 1. Validate required core recipe metadata
        recipe_name = request.form.get("recipe_name")
        if not recipe_name:
            print("Validation Error: Recipe name missing")
            return render_template("add.html")

        # 2. Process optional recipe image upload
        filename = "default_picture"
        file = request.files.get("recipe_photo")
        if file and file.filename != '':
            filename = file.filename
            file.save(os.path.join(UPLOAD_FOLDER, filename))

        # 3. Extract parallel lists of ingredient attributes from form fields
        ingredients_names = request.form.getlist("ingredient_name")
        ingredients_amounts = request.form.getlist("ingredient_amount")
        ingredients_UOM = request.form.getlist("unit")

        # 4. Validate completeness of all dynamically added ingredient rows
        for name in ingredients_names:
            if not name:
                print("Validation Error: Ingredient name missing")
                return render_template("add.html")

        for amount in ingredients_amounts:
            if not amount:
                print("Validation Error: Ingredient amount missing")
                return render_template("add.html")

        for uom in ingredients_UOM:
            if not uom:
                print("Validation Error: Unit of measure not selected")
                return render_template("add.html")

        instructions = request.form.get("instructions")
        db = get_db()
        
        # 5. Insert primary recipe entry
        db.execute(
            "INSERT OR IGNORE INTO recipes (name, photo, instructions) VALUES (?, ?, ?)",
            (recipe_name, filename, instructions)
        )
        
        # 6. Insert new unique ingredients (skips existing entries via UNIQUE index)
        for name in ingredients_names:
            db.execute("INSERT OR IGNORE INTO ingredients (name) VALUES (?)", (name,))

        # 7. Fetch foreign key ID for the created recipe
        cursor = db.execute("SELECT id FROM recipes WHERE name = ?", (recipe_name,))
        row = cursor.fetchone()
        if row:
            recipe_id = row["id"]
        else:
            print("Database Error: Could not recover inserted recipe ID")
            return render_template("add.html")
        
        # 8. Map recipe and ingredients together in join table with amounts and units
        for ing_name, ing_amount, ing_uom in zip(ingredients_names, ingredients_amounts, ingredients_UOM):
            cursor = db.execute("SELECT id FROM ingredients WHERE name = ?", (ing_name,))
            row = cursor.fetchone()
            if row:
                ingredient_id = row["id"]
                db.execute(
                    "INSERT OR IGNORE INTO recipes_ingredients (recipe_id, ingredient_id, ingredient_amount, unit) VALUES (?, ?, ?, ?)",
                    (recipe_id, ingredient_id, ing_amount, ing_uom)
                )
            else:
                print(f"Database Error: Could not resolve ID for ingredient '{ing_name}'")
                return render_template("add.html")
            
        # 9. Atomic commit for all database writes
        db.commit()
        return render_template("index.html")
        
    return render_template('add.html')


@app.route('/index')
def load():
    """Placeholder route for secondary data loading."""
    pass


if __name__ == '__main__':
    app.run(debug=True)