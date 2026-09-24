-- RECIPE TABLE
CREATE TABLE IF NOT EXISTS recipes 
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    photo TEXT DEFAULT 'default_picture',
    instructions TEXT
);

-- INGREDIENTS TABLE
CREATE TABLE IF NOT EXISTS ingredients 
(
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    name TEXT UNIQUE NOT NULL
);

-- RECIPE INGREDIENTS JUNCTION TABLE
CREATE TABLE IF NOT EXISTS recipes_ingredients
(
    recipe_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    ingredient_amount REAL NOT NULL,
    unit TEXT NOT NULL,
    PRIMARY KEY (recipe_id, ingredient_id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
);