PRAGMA_FOREIGN_KEYS = "PRAGMA foreign_keys = ON;"

CREATE_MEALS = """
CREATE TABLE IF NOT EXISTS meals (
    meal_id INTEGER PRIMARY KEY,
    meal_name TEXT UNIQUE NOT NULL 
);
"""

CREATE_INGREDIENTS = """
CREATE TABLE IF NOT EXISTS ingredients (
    ingredient_id INTEGER PRIMARY KEY,
    ingredient_name TEXT UNIQUE NOT NULL 
);
"""

CREATE_MEASURES = """
CREATE TABLE IF NOT EXISTS measures (
    measure_id INTEGER PRIMARY KEY,
    measure_name TEXT UNIQUE 
);
"""

CREATE_RECIPES = """
CREATE TABLE IF NOT EXISTS recipes (
    recipe_id INTEGER PRIMARY KEY,
    recipe_name TEXT NOT NULL,
    recipe_description TEXT 
);
"""

CREATE_SERVE = """
CREATE TABLE IF NOT EXISTS serve (
    serve_id INTEGER PRIMARY KEY,
    recipe_id INTEGER NOT NULL,
    meal_id INTEGER NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipes (recipe_id),
    FOREIGN KEY (meal_id) REFERENCES meals (meal_id)
);
"""

CREATE_QUANTITY = """
CREATE TABLE IF NOT EXISTS quantity (
    quantity_id INTEGER PRIMARY KEY,
    quantity INTEGER NOT NULL,
    measure_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    recipe_id INTEGER NOT NULL,
    FOREIGN KEY (measure_id) REFERENCES measures (measure_id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients (ingredient_id),
    FOREIGN KEY (recipe_id) REFERENCES recipes (recipe_id)
);
"""

data = {
    "meals": ("breakfast", "brunch", "lunch", "supper"),
    "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
    "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")
}

INSERT_DATA = "INSERT INTO {0} ({1}_name) VALUES ('{2}');"

INSERT_RECIPE = "INSERT INTO recipes (recipe_name, recipe_description) VALUES ('{0}', '{1}');"

INSERT_SERVE = "INSERT INTO serve (recipe_id, meal_id) VALUES ({0}, {1});"

INSERT_QUANTITY = "INSERT INTO quantity (quantity, measure_id, ingredient_id, recipe_id) VALUES ({0}, {1},{2},{3});"

SELECT_MEASURE = "SELECT measure_id FROM measures WHERE measure_name LIKE '{}';"

SELECT_INGREDIENT = "SELECT ingredient_id FROM ingredients WHERE ingredient_name LIKE '%{}%';"

SELECT_RECIPE_MEAL = "SELECT recipe_id FROM serve JOIN meals ON serve.meal_id = meals.meal_id WHERE meal_name IN ('{}');"

SELECT_RECIPE_INGREDIENT = """SELECT recipe_id FROM quantity 
JOIN ingredients ON quantity.ingredient_id = ingredients.ingredient_id 
WHERE ingredient_name = '{}';"""

SELECT_RECIPE_NAME = "select recipe_name from recipes where recipe_id = {};"
