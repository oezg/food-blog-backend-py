import argparse
import sqlite3
import sys

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

parser = argparse.ArgumentParser()
parser.add_argument('db_name')
parser.add_argument('--ingredients', dest='ingredients')
parser.add_argument('--meals', dest='meals')
args = parser.parse_args()
db_name = args.db_name
conn = sqlite3.connect(db_name)
cur = conn.cursor()
cur.execute("PRAGMA foreign_keys = ON;")

if args.ingredients or args.meals:
    t = args.meals.replace(",", "', '")
    cur.execute(f"select recipe_id from serve join meals on serve.meal_id = meals.meal_id where meal_name in ('{t}');")
    result = [{row[0] for row in cur.fetchall()}]
    for ingred in args.ingredients.split(","):
        cur.execute(f"""
        select recipe_id from quantity join ingredients on quantity.ingredient_id = ingredients.ingredient_id
        where ingredient_name = '{ingred}';
        """)
        result.append({row[0] for row in cur.fetchall()})
    out = set.intersection(*result)
    if not out:
        print('There are no such recipes in the database.')
    else:
        z = []
        for u in out:
            cur.execute(f"select recipe_name from recipes where recipe_id = {u};")
            z.append(cur.fetchone()[0])
        print(f"Recipes selected for you: {', '.join(z)}")
else:
    cur.execute(CREATE_MEALS)
    cur.execute(CREATE_INGREDIENTS)
    cur.execute(CREATE_MEASURES)
    cur.execute(CREATE_RECIPES)
    cur.execute(CREATE_SERVE)
    cur.execute(CREATE_QUANTITY)

    for table, variables in data.items():
        for variable in variables:
            cur.execute(f"INSERT INTO {table} ({table[:-1]}_name) VALUES ('{variable}');")
    conn.commit()

    print('Pass the empty recipe name to exit.')
    while recipe_name := input('Recipe name: '):
        recipe_description = input('Recipe description: ')
        cur.execute(f"""INSERT INTO recipes (recipe_name, recipe_description) 
                        VALUES ('{recipe_name}', '{recipe_description}');
                        """)
        recipe_id = cur.lastrowid

        meals = cur.execute("SELECT * FROM meals;").fetchall()
        meals_string = " ".join(") ".join(map(str, meal)) for meal in meals)
        print(meals_string)
        meals_choice = map(int, input("When can the dish be served: ").split())
        for choice in meals_choice:
            cur.execute(f"INSERT INTO serve (recipe_id, meal_id) VALUES ({recipe_id}, {choice});")

        while quantity_ingredient := input('Input quantity of ingredient <press enter to stop>: '):
            qmi_input = quantity_ingredient.split()
            quantity = int(qmi_input[0])
            measure = qmi_input[1] if len(qmi_input) == 3 else ''
            ingredient = qmi_input[-1]
            cur.execute(f"SELECT measure_id FROM measures WHERE measure_name LIKE '{measure + '%' if measure else ''}';")
            if len((matching_measures := cur.fetchall())) == 1:
                measure_id = matching_measures[0][0]
            else:
                print('The measure is not conclusive!')
                continue
            cur.execute(f"SELECT ingredient_id FROM ingredients WHERE ingredient_name LIKE '%{ingredient}%';")
            if len((matching_ingredients := cur.fetchall())) == 1:
                ingredient_id = matching_ingredients[0][0]
            else:
                print('The ingredient is not conclusive!')
                continue
            cur.execute(f"INSERT INTO quantity (quantity, measure_id, ingredient_id, recipe_id) "
                        f"VALUES ({quantity}, {measure_id},{ingredient_id},{recipe_id});")

conn.commit()
conn.close()
