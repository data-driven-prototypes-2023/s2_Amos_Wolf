import numpy as np
import pandas as pd
import cohere
import ast
import os

def new_column_lang(df, column_str, order_of_importance):
    column_names = df.columns
    column_names = [column for column in column_names if column_str in column]
    column_names = [column for column in column_names if column.split('_')[-1] in order_of_importance]
    column_names.sort(key=lambda x: order_of_importance.index(x.split('_')[-1]))
    df[column_str+'_modif'] = np.where(df[column_names[0]].notna(), df[column_names[0]], None)
    for column in column_names[1:]:
        df[column_str+'_modif'] = np.where(df[column].notna(), df[column], df[column_str+'_modif'])
    return df[column_str+'_modif']

def get_columns_lang(df, order_of_importance):
    column_names = df.columns
    column_names = np.unique([('_').join(column.split('_')[:-1]) for column in column_names if column.split('_')[-1] in order_of_importance])
    return column_names.tolist()

def interesting_columns():
    columns = ['code', 'product_name', 'quantity', 'serving_size', 'brands', 'categories', 'labels', 'countries', 'stores', 'manufacturing_places', 'ingredients_text',
               'allergens', 'traces', 'nutrition_data_per', 'nutrition_data_prepared_per', 'conservation_conditions', 'off:nutriscore_grade', 'off:ecoscore_grade', 'off:nova_group_tags',
               'preparation', 'warning', 'recipe_idea', 'link',
    ]
    return columns

def get_value_unit_columns(df):
    columns = df.columns
    columns = [column for column in columns if '_value' in column]
    columns = [column.split('_value')[0] for column in columns]
    columns = np.unique(columns)
    return columns

def get_nutrition_columns():
    # Macronutrients
    macronutrients = ['carbohydrates', 'carbohydrates_prepared', 'fat', 'fat_prepared', 'fiber', 'fiber_prepared', 'proteins', 'proteins_prepared', 'sugars', 'sugars_prepared']

    # Vitamins and Minerals
    vitamins_minerals = ['calcium', 'folates', 'iron', 'magnesium', 'molybdenum', 'phosphorus', 'potassium', 'sodium', 'sodium_prepared', 'zinc']

    # Vitamins
    vitamins = ['vitamin-a', 'vitamin-b1', 'vitamin-b2', 'vitamin-b6', 'vitamin-b9', 'vitamin-b12', 'vitamin-c', 'vitamin-d', 'vitamin-e', 'vitamin-pp']

    # Sugars
    sugars = ['added-sugars', 'fructose', 'glucose', 'lactose', 'maltose', 'sucrose']

    # Energy
    energy = ['energy', 'energy-from-fat', 'energy-kcal', 'energy-kcal_prepared', 'energy-kj', 'energy-kj_prepared', 'energy_prepared']

    # Fats
    fats = ['monounsaturated-fat', 'polyunsaturated-fat', 'saturated-fat', 'saturated-fat_prepared', 'trans-fat', 'omega-3-fat', 'omega-9-fat']

    # Alcohols and Polyols
    alcohols_polyols = ['alcohol', 'alcohol_prepared', 'polyols']

    # Fatty Acids
    fatty_acids = ['alpha-linolenic-acid', 'docosahexaenoic-acid', 'eicosapentaenoic-acid', 'oleic-acid']

    # Others
    others = ['beta-glucan', 'cholesterol', 'cocoa', 'fruits-vegetables-nuts', 'fruits-vegetables-nuts-estimate', 'insoluble-fiber', 'maltodextrins', 'melissic-acid', 'montanic-acid', 'pantothenic-acid', 'soluble-fiber', 'starch']

    return macronutrients, vitamins_minerals, vitamins, sugars, energy, fats, alcohols_polyols, fatty_acids, others

def get_packaging_columns(df):
    columns = df.columns
    columns = [column for column in columns if 'packaging_' in column]
    columns = np.unique(columns)
    return columns

try:
    path="COHERE_KEY.txt"
    os.environ["COHERE_KEY"] = open(path, 'r').read()
except:
    print("Please set the GITHUB_KEY environment variable.")

COHERE_API_KEY = os.getenv('COHERE_KEY')
cohere_client = cohere.Client(COHERE_API_KEY)
# let's create a command agent that cleans a list to only have uniques in english
def agent_clean_list(list_to_clean):
    prompt = f"""
    You will receive a list of elements. You're objective is to return a the list cleaned.
     - All the lements returned have to be in English.
     - No duplicated elements.
     - Return only the list in this format: ['Italy', 'Germany', ...]
    Here is the list to clean:
    {list_to_clean}
    """
    #print('start cleaning')
    response = cohere_client.chat(
        message=prompt,
        model='command-r'
    )
    #print(response.text)
    # get index of the first '['
    index = response.text.find('[')
    # get index of the last ']'
    index_end = response.text.rfind(']')
    # get the list
    list_cleaned = response.text[index:index_end+1]
    list_cleaned = ast.literal_eval(list_cleaned)
    #print(list_cleaned)
    #print(list_cleaned)
    return list_cleaned

def transl_allergens(allergen):
    translations = {
        'Eggs': 'Eggs',
        'Gluten': 'Gluten',
        'Milk': 'Milk',
        'Soybeans': 'Soybeans',
        'Lait': 'Milk',
        'Soja': 'Soybeans',
        'Œufs': 'Eggs',
        'Leche': 'Milk',
        'Glúten': 'Gluten',
        'Lapte': 'Milk',
        'Soia': 'Soybeans',
        'pt:Metabissulfito': 'Metabisulfite',
        'Глутен': 'Gluten',
        'Суроватка': 'Whey',
        'Sulphur dioxide and sulphites': 'Sulphur dioxide and sulphites',
        'es:Metabisulfito': 'Metabisulfite',
        'Dióxido de azufre y sulfitos': 'Sulphur dioxide and sulphites',
        'Avena': 'Oats',
        'es:Avena': 'Oats',
        'Nuts': 'Nuts',
        'Frutos de cáscara': 'Nuts',
        'غلوتين': 'Gluten',
        'حليبب': 'Milk',
        'بندقة': 'Nut',
        'فول الصويا': 'Soybeans',
        'Mantequilla': 'Butter',
        'Huevos': 'Eggs',
        'Anhydride sulfureux et sulfites': 'Sulphur dioxide and sulphites',
        'Latte': 'Milk',
        'Laktoza': 'Lactose',
        'Tartrazina': 'Tartrazine',
        'Glutine': 'Gluten',
        'en:Gluten': 'Gluten',
        'en:Milk': 'Milk',
        'Fruits à coque': 'Nuts',
        'Cacahuetes': 'Peanuts',
        'Granos de sésamo': 'Sesame seeds',
        'Eieren': 'Eggs',
        'Melk': 'Milk',
        'Munat': 'Eggs',
        'Gluteeni': 'Gluten',
        'Maito': 'Milk',
        'Schalenfrüchte': 'Nuts',
        'en:SULFITOS': 'Sulphites',
        'en:TRIGO': 'Wheat',
        'en:Œufs': 'Eggs',
        'Gluteen': 'Gluten',
        'Laktoos': 'Lactose',
        'Jaja': 'Eggs',
        'Orašaste plodove': 'Nuts',
        'Milch': 'Milk',
        'Sojafaser': 'Soy fiber',
        'Avoine': 'Oats',
        'Ovos': 'Eggs',
        'Leite': 'Milk',
        'Dióxido de enxofre e sulfitos': 'Sulphur dioxide and sulphites',
        'Lupin': 'Lupin',
        "pt:Flocos d'aveia": 'Oat flakes',
        'Crema': 'Cream',
        'Emulsionante': 'Emulsifier',
        'Sciroppo di glucosio': 'Glucose syrup',
        'pl:laktoza': 'Lactose',
        'Láctea': 'Dairy',
        'Rge': 'Rye',
        'en:aveia': 'Oats',
        'en:leite': 'Milk',
        'en:láctea': 'Dairy',
        'en:trigo': 'Wheat',
        'Soija': 'Soybeans',
        'Peanuts': 'Peanuts',
        'Sesame seeds': 'Sesame seeds',
        'Apple': 'Apple',
        'Pescado': 'Fish',
        'Frutta a guscio': 'Nuts',
        'Altramuces': 'Lupins',
        'Graines de sésame': 'Sesame seeds',
        'Eier': 'Eggs',
        'en:Soybeans': 'Soybeans',
        'Lehce Soja': 'Soybeans',
        'en:dried fruits': 'Dried fruits',
        'Erdnüsse': 'Peanuts',
        'Uova': 'Eggs',
        'Burro': 'Butter',
        'Metabisulfito': 'Metabisulfite',
        'Mostaza': 'Mustard',
        'es:mantequilla': 'Butter',
        'Caseinato': 'Caseinate',
        'Suero': 'Whey',
        'pt:Avena': 'Oats',
        'ca:civada': 'Oats',
        'ca:espelta': 'Spelt',
        'Soja y derivados de los mismos.': 'Soybeans and derivatives',
        'Sarrasin': 'Buckwheat',
        'xx:Butterreinfett': 'Butterfat',
        'xx:Hühnereieiweißpulver': 'Egg white powder',
        'xx:Hühnervollei': 'Whole egg',
        'xx:Magermilchpulver': 'Skimmed milk powder',
        'xx:Vollmilchpulver': 'Whole milk powder',
        'xx:Weizenmehl': 'Wheat flour',
        'xx:Weizenstärke': 'Wheat starch',
        'ca:CEBADA': 'Barley',
        'ca:ESPELTA': 'Spelt',
        'ca:TRIGO': 'Wheat',
        'Trigo': 'Wheat',
        'fr:Avoine': 'Oats',
        'Metabisulfito sódico': 'Sodium metabisulfite',
        '卵': 'Eggs',
        '小麦/そば': 'Wheat/Soba',
        '乳': 'Milk',
        '大豆': 'Soybeans',
        'Ufs': 'Eggs',
        'Lepek': 'Gluten',
        'Lácteas': 'Dairy',
        'Sal': 'Salt',
        'Sementes de sésamo': 'Sesame seeds',
        'Gelatin': 'Gelatin',
        'en:None': 'None',
        'es:Láctea': 'Dairy',
        'es:Mantequilla': 'Butter',
        'Metabissulfito': 'Metabisulfite',
        'Sulfítico': 'Sulphitic',
        'pt:Sulfítico': 'Sulphitic',
        'Arachidi': 'Peanuts',
        'Frutos de casca rija': 'Nuts',
        'Celery': 'Celery',
        'Sellerie': 'Celery',
        'Sesam': 'Sesame',
        'Pasta de cacahuete': 'Peanut butter',
        'Blat': 'Wheat',
        'Llet': 'Milk',
        'Mantega': 'Butter',
        'Ou': 'Egg',
        'es:leite': 'Milk',
        "Blé d'épeautre": 'Spelt wheat',
        'Glutén': 'Gluten',
        'Tej': 'Milk',
        'Coco': 'Coconut',
        'Arachides': 'Peanuts',
        'th:กลูเตน': 'Gluten',
        'th:ถั่วเปลือกแข็ง': 'Tree nuts',
        'th:ธัญพืช': 'Cereals',
        'Aveia': 'Oats',
        'Centeio': 'Rye',
        'Cevada': 'Barley',
        'Ovo': 'Egg',
        'Matalahúga': 'Anise',
        'ca:blat': 'Wheat',
        'ca:ou': 'Egg',
        'Metabisulfito potásico': 'Potassium metabisulfite',
        'Weizenvollkornmehl': 'Whole wheat flour',
        'Levhe': 'Lupin',
        'Amendoins': 'Peanuts',
        'Harina integral de espelta': 'Whole spelt flour',
    }
    if allergen in translations.keys():
        return translations[allergen]
    else:
        return 'Unknown'
