from bs4 import BeautifulSoup as soup
from datetime import date
import requests
import unicodedata
import json

def getMeals(event, context):

    url_buckley = "http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=03&locationName=Buckley+Dining+Hall&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate="                    # 10%2f25%2f2022&mealName=Breakfast"
    url_gelfenbien = "http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=42&locationName=Gelfenbien+Commons%2c+Halal+%26+Kosher&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate="  # 10%2f27%2f2022&mealName=Breakfast"
    url_mcmahon = "http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=05&locationName=McMahon+Dining+Hall&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate="                    # 10%2f27%2f2022&mealName=Breakfast"
    url_north = "http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=07&locationName=North+Campus+Dining+Hall&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate="                 # 10%2f27%2f2022&mealName=Breakfast"
    url_northwest = "http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=15&locationName=Northwest+Marketplace&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate="                # 10%2f27%2f2022&mealName=Breakfast
    url_putnum = "http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=06&locationName=Putnam+Dining+Hall&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate="                      # 10%2f27%2f2022&mealName=Breakfast"
    url_south = "http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=16&locationName=South+Campus+Marketplace&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate="                 # 10%2f27%2f2022&mealName=Breakfast"
    url_whitney = "http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=01&locationName=Whitney+Dining+Hall&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate="                    # 10%2f27%2f2022&mealName=Breakfast"

    link_list = [url_buckley, url_mcmahon, url_north, url_gelfenbien, url_northwest, url_putnum, url_south, url_whitney]

    parse = event['path'].split("/")
    dining_hall = parse[1].capitalize()
    meal = parse[2].capitalize()

    # What dining hall is it?
    for link in link_list:
        if dining_hall in link:
            url = link

    # Refactor link | Get todays link
    today = date.today()
    dd = today.strftime("%d")
    mm = today.strftime("%m")
    yyyy = today.strftime("%Y")

    edited_url = url + mm + '%2f' + dd + '%2f' + yyyy + '&mealName=' + meal
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

    return {
        'statusCode': 200,
        "headers": {
            "Content-Type": "application/json"
        },
        'body': json.dumps(L)
    }




