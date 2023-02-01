from bs4 import BeautifulSoup as soup
from datetime import date
import requests
import unicodedata
import json

# Our cached values will be stored here
cache_breakfast = []
cache_lunch = []
cache_dinner = []

def lambda_handler(event, context):

    global cache_breakfast
    global cache_lunch 
    global cache_dinner

    # Warmup our function!
    if event.get("source") == "serverless-plugin-warmup":
        print("WarmUp - Lambda is warm!")

        if not cache_breakfast:
            print("Breakfast not cached")

        if not cache_lunch:
            print("Lunch not cached")

        if not cache_dinner:
            print("Dinner not cached")

        return {}

    parse = event['path'].split("/")
    meal = parse[2]

    if meal == "breakfast":
        cache_breakfast = fetch_cache(meal)

        return {
        'statusCode': 200,
        "headers": {
            "Content-Type": "application/json"
        },
        'body': json.dumps(cache_breakfast)
    }

    elif meal == "lunch":
        cache_lunch = fetch_cache(meal)

        return {
        'statusCode': 200,
        "headers": {
            "Content-Type": "application/json"
        },
        'body': json.dumps(cache_lunch)
    }

    elif meal == "dinner":
        cache_dinner = fetch_cache(meal)

        return {
        'statusCode': 200,
        "headers": {
            "Content-Type": "application/json"
        },
        'body': json.dumps(cache_dinner)
    }

    return "Failed at lambda_handler"   
    
def fetch_cache(meal):
    global cache_breakfast
    global cache_lunch
    global cache_dinner

    if meal == "breakfast":
        if not cache_breakfast:
            cache_breakfast = getMeals(meal)
            return cache_breakfast

        return cache_breakfast

    elif meal == "lunch":
        if not cache_lunch:
            cache_lunch = getMeals(meal)
            return cache_lunch

        return cache_lunch

    elif meal == "dinner":
        if not cache_dinner:
            cache_dinner = getMeals(meal)
            return cache_dinner

        return cache_dinner 

    return "Failed at fetch_cache() function"     

def getMeals(meal):
    # Buckley
    url_buckley = "http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=03&locationName=Buckley+Dining+Hall&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate="   # 10%2f25%2f2022&mealName=Breakfast"

    # Refactor link | Get todays link
    today = date.today()
    dd = today.strftime("%d")
    mm = today.strftime("%m")
    yyyy = today.strftime("%Y")

    edited_url = url_buckley + mm + '%2f' + dd + '%2f' + yyyy + '&mealName=' + meal.capitalize()
    buckley = requests.get(edited_url)

    # HTML Parsing
    html = buckley.content
    page_soup = soup(html, "html.parser")

    # Grabs each menu_item
    containers = page_soup.findAll("div", {"class": "longmenucoldispname"})

    L = []
    myDict = dict()
    for menu_item in containers:
        href = menu_item.a['href']
        new_url = "http://nutritionanalysis.dds.uconn.edu/" + href
        label = requests.get(new_url)

        # HTML Parsing
        html2 = label.content
        page_soup = soup(html2, "html.parser")
        nut_facts = page_soup.findAll("span", {"class": "nutfactstopnutrient"})

        calories_val = page_soup.find("td", {"class": "nutfactscaloriesval"})
        serving_size = page_soup.findAll("div", {"class": "nutfactsservsize"})

        myDict = dict()
        myDict["Food Item"] = menu_item.text
        myDict["Calories"] = calories_val.text
        myDict["Serving Size"] = serving_size[1].text

        for facts in nut_facts:

            clean_text = unicodedata.normalize("NFKD", facts.text).strip() # remove unicode and leading spaces
            if clean_text.split() == []: 
                pass
            else:
                parse = clean_text.split()[-1] # get grams of nutritional fact

            # parse out weird strings
            if "%" in clean_text or "g" not in clean_text:
                continue

            if "Total Fat" in clean_text:
                myDict["Total Fat"] = parse
                continue
            
            if "Total Carbohydrates" in clean_text:
                myDict["Total Carbohydrates"] = parse
                continue

            if "Saturated Fat" in clean_text:
                myDict["Saturated Fat"] = parse
                continue

            if "Dietary Fiber" in clean_text:
                myDict["Dietary Fiber"] = parse
                continue

            if "Trans Fat" in clean_text:
                myDict["Trans Fat"] = parse
                continue

            if "Total Sugars" in clean_text:
                myDict["Total Sugars"] = parse
                continue

            if "Cholesterol" in clean_text:
                myDict["Cholesterol"] = parse
                continue

            if "Added Sugars" in clean_text:
                parse = clean_text.split()[1] # get grams of nutritional fact
                myDict["Added Sugars"] = parse
                continue

            if "Sodium" in clean_text:
                myDict["Sodium"] = parse
                continue

            if "Protein" in clean_text:
                myDict["Protein"] = parse
                continue

            if "Calcium" in clean_text:
                myDict["Calcium"] = parse
                continue

            if "Iron" in clean_text:
                myDict["Iron"] = parse
                continue

            if "Vitamin D" in clean_text:
                myDict["Vitamin D"] = parse
                continue

            if "Potassium" in clean_text:
                myDict["Potassium"] = parse
                continue

            L.append(myDict)

    return L







