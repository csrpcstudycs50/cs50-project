import os
import sqlite3
from flask import Flask, request, render_template, g, redirect

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
@app.route('/index')
def load():
    """Load and display all saved recipes with their associated ingredients."""
    db = get_db()

    # 1. Fetch all recipes ordered by newest first
    recipes_rows = db.execute("SELECT * FROM recipes ORDER BY id DESC").fetchall()

    recipes = []
    
    # 2. For each recipe, fetch its linked ingredients, amounts, and units
    for recipe in recipes_rows:
        recipe_id = recipe["id"]
        
        ingredients_rows = db.execute("""
            SELECT 
                i.name, 
                ri.ingredient_amount AS amount, 
                ri.unit 
            FROM recipes_ingredients ri
            JOIN ingredients i ON ri.ingredient_id = i.id
            WHERE ri.recipe_id = ?
        """, (recipe_id,)).fetchall()

        # Build a structured dictionary for each recipe
        recipes.append({
            "id": recipe["id"],
            "name": recipe["name"],
            "photo": recipe["photo"],
            "instructions": recipe["instructions"],
            "ingredients": ingredients_rows
        })

    # 3. Pass the structured list to index.html
    return render_template('index.html', recipes=recipes)


@app.route('/add', methods=['GET', 'POST'])
def add():
    """
    Handles recipe creation:
    - GET: Displays the recipe creation form.
    - POST: Validates input fields, uploads optional media, populates database tables, and commits changes.
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
        
        # 5. Insert primary recipe entry and capture its auto-incremented primary key
        cursor = db.execute(
            "INSERT INTO recipes (name, photo, instructions) VALUES (?, ?, ?)",
            (recipe_name, filename, instructions)
        )
        recipe_id = cursor.lastrowid
        
        # 6. Insert new unique ingredients into master catalog
        for name in ingredients_names:
            db.execute("INSERT OR IGNORE INTO ingredients (name) VALUES (?)", (name,))

        # 7. Map recipe and ingredients together in join table with amounts and units
        for ing_name, ing_amount, ing_uom in zip(ingredients_names, ingredients_amounts, ingredients_UOM):
            row = db.execute("SELECT id FROM ingredients WHERE name = ?", (ing_name,)).fetchone()
            if row:
                ingredient_id = row["id"]
                db.execute(
                    "INSERT OR IGNORE INTO recipes_ingredients (recipe_id, ingredient_id, ingredient_amount, unit) VALUES (?, ?, ?, ?)",
                    (recipe_id, ingredient_id, ing_amount, ing_uom)
                )
            else:
                print(f"Database Error: Could not resolve ID for ingredient '{ing_name}'")
                return render_template("add.html")
            
        # 8. Atomic commit for all database writes
        db.commit()
        return redirect('/')
        
    return render_template('add.html')


@app.route('/edit/<int:recipe_id>', methods=['POST'])
def edit(recipe_id):
    """Updates an existing recipe and its ingredients in the database."""
    db = get_db()

    # 1. Fetch form inputs
    recipe_name = request.form.get("recipe_name")
    instructions = request.form.get("instructions")
    
    if not recipe_name:
        return redirect('/')

    # 2. Check if a new photo was uploaded; otherwise keep existing photo
    file = request.files.get("recipe_photo")
    if file and file.filename != '':
        filename = file.filename
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        db.execute("UPDATE recipes SET photo = ? WHERE id = ?", (filename, recipe_id))

    # 3. Update main recipe fields
    db.execute(
        "UPDATE recipes SET name = ?, instructions = ? WHERE id = ?",
        (recipe_name, instructions, recipe_id)
    )

    # 4. Refresh ingredients: Clear old join-table relationships for this recipe
    db.execute("DELETE FROM recipes_ingredients WHERE recipe_id = ?", (recipe_id,))

    # 5. Extract updated ingredient lists
    ingredients_names = request.form.getlist("ingredient_name")
    ingredients_amounts = request.form.getlist("ingredient_amount")
    ingredients_UOM = request.form.getlist("unit")

    # 6. Insert missing ingredients and re-link in recipes_ingredients
    for name, amount, uom in zip(ingredients_names, ingredients_amounts, ingredients_UOM):
        if name and amount and uom:
            # Ensure ingredient exists in catalog
            db.execute("INSERT OR IGNORE INTO ingredients (name) VALUES (?)", (name,))
            
            # Fetch ingredient ID
            row = db.execute("SELECT id FROM ingredients WHERE name = ?", (name,)).fetchone()
            if row:
                ingredient_id = row["id"]
                db.execute(
                    "INSERT INTO recipes_ingredients (recipe_id, ingredient_id, ingredient_amount, unit) VALUES (?, ?, ?, ?)",
                    (recipe_id, ingredient_id, amount, uom)
                )

    db.commit()
    return redirect('/')


@app.route('/delete/<int:recipe_id>', methods=['POST'])
def delete(recipe_id):
    """Deletes a recipe and its image file, returning to the main dashboard."""
    db = get_db()
    
    # 1. Clean up local image file if custom photo was uploaded
    recipe = db.execute("SELECT photo FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
    if recipe and recipe["photo"] and recipe["photo"] != "default_picture":
        photo_path = os.path.join(UPLOAD_FOLDER, recipe["photo"])
        if os.path.exists(photo_path):
            os.remove(photo_path)

    # 2. Remove recipe from database (CASCADE deletes linked recipes_ingredients)
    db.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    db.commit()

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)