import argparse
import sqlite3
import statements


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('db_name')
    parser.add_argument('--ingredients', dest='ingredients')
    parser.add_argument('--meals', dest='meals')
    args = parser.parse_args()
    db_name = args.db_name
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    if args.ingredients or args.meals:
        meals_text = args.meals.replace(",", "', '")
        ingredients_list = args.ingredients.split(",")
        search(meals_text, ingredients_list, cur)
    else:
        initialize_database(cur)
        conn.commit()

        fill_recipes(cur)

    conn.commit()
    conn.close()


def fill_recipes(cur):
    print('Pass the empty recipe name to exit.')
    while recipe_name := input('Recipe name: '):
        recipe_description = input('Recipe description: ')
        cur.execute(statements.INSERT_RECIPE.format(recipe_name, recipe_description))
        recipe_id = cur.lastrowid

        meals = cur.execute("SELECT * FROM meals;").fetchall()
        meals_string = " ".join(") ".join(map(str, meal)) for meal in meals)
        print(meals_string)
        meals_choice = map(int, input("When can the dish be served: ").split())
        for choice in meals_choice:
            cur.execute(statements.INSERT_SERVE.format(recipe_id, choice))

        while quantity_ingredient := input('Input quantity of ingredient <press enter to stop>: '):
            qmi_input = quantity_ingredient.split()
            quantity = int(qmi_input[0])
            measure = qmi_input[1] if len(qmi_input) == 3 else ''
            ingredient = qmi_input[-1]
            cur.execute(statements.SELECT_MEASURE.format(measure + '%' if measure else ''))
            if len((matching_measures := cur.fetchall())) != 1:
                print('The measure is not conclusive!')
                continue
            measure_id = matching_measures[0][0]
            cur.execute(statements.SELECT_INGREDIENT.format(ingredient))
            if len((matching_ingredients := cur.fetchall())) != 1:
                print('The ingredient is not conclusive!')
                continue
            ingredient_id = matching_ingredients[0][0]
            cur.execute(statements.INSERT_QUANTITY.format(quantity, measure_id, ingredient_id, recipe_id))


def initialize_database(cur):
    cur.execute(statements.PRAGMA_FOREIGN_KEYS)
    cur.execute(statements.CREATE_MEALS)
    cur.execute(statements.CREATE_INGREDIENTS)
    cur.execute(statements.CREATE_MEASURES)
    cur.execute(statements.CREATE_RECIPES)
    cur.execute(statements.CREATE_SERVE)
    cur.execute(statements.CREATE_QUANTITY)

    for table, variables in statements.data.items():
        for variable in variables:
            cur.execute(statements.INSERT_DATA.format(table, table[:-1], variable))


def search(meals_text: str, ingredients: list[str], cur: sqlite3.Cursor) -> None:
    cur.execute(statements.SELECT_RECIPE_MEAL.format(meals_text))
    recipe_sets = [{row[0] for row in cur.fetchall()}]
    for ingredient in ingredients:
        cur.execute(statements.SELECT_RECIPE_INGREDIENT.format(ingredient))
        recipe_sets.append({row[0] for row in cur.fetchall()})
    recipes_with_every_ingredient = set.intersection(*recipe_sets)
    if not recipes_with_every_ingredient:
        print('There are no such recipes in the database.')
    else:
        selected_recipe_names = []
        for recipe in recipes_with_every_ingredient:
            cur.execute(statements.SELECT_RECIPE_NAME.format(recipe))
            selected_recipe_names.append(cur.fetchone()[0])
        print(f"Recipes selected for you: {', '.join(selected_recipe_names)}")


if __name__ == '__main__':
    main()
