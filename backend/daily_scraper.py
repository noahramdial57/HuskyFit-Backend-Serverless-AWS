from bs4 import BeautifulSoup as soup
from datetime import date
import requests
import unicodedata
import json
import csv

def getMeals(event):

    link_list= ["http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=03&locationName=Buckley+Dining+Hall&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate=",                    # 10%2f25%2f2022&mealName=Breakfast"
                "http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=42&locationName=Gelfenbien+Commons%2c+Halal+%26+Kosher&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate=",  # 10%2f27%2f2022&mealName=Breakfast"
                "http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=05&locationName=McMahon+Dining+Hall&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate=",                    # 10%2f27%2f2022&mealName=Breakfast"
                "http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=07&locationName=North+Campus+Dining+Hall&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate=",                 # 10%2f27%2f2022&mealName=Breakfast"
                "http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=15&locationName=Northwest+Marketplace&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate=",                # 10%2f27%2f2022&mealName=Breakfast
                "http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=06&locationName=Putnam+Dining+Hall&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate=",                      # 10%2f27%2f2022&mealName=Breakfast"
                "http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=16&locationName=South+Campus+Marketplace&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate=",                 # 10%2f27%2f2022&mealName=Breakfast"
                "http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=01&locationName=Whitney+Dining+Hall&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate=",
                "http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=42&locationName=Gelfenbien+Commons%2c+Halal+%26+Kosher&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate="]                    # 10%2f27%2f2022&mealName=Breakfast"

    # parse = event['path'].split("/")
    parse = event.split("/")  
    # print(parse)
    dining_hall = parse[0].capitalize()
    meal = parse[1].capitalize()

    if dining_hall == "Mcmahon":
        dining_hall = "McMahon"

    # What dining hall is it?
    url = ""
    for link in link_list:
        if dining_hall in link:
            url = link
            break

    # print(url)
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
        allergen_val = page_soup.find("span", {"class": "labelallergensvalue"})
        # TODO add tags for allergens
        # allergen_codes = page_soup.find("span", {"class": "labelwebcodesvalue"})


        myDict = dict()
        myDict["Food Item"] = menu_item.text
        myDict["Calories"] = calories_val.text
        myDict["Serving Size"] = serving_size[1].text
        myDict["Allegerns"] = allergen_val.text


        # TODO add tags for allergens
        # for tag in allergen_codes:
        #     instrument = tag.find('img')
        #     if instrument:  
        #         # ...create a new string with the content of 'alt' in the middle if 'tag.text'
        #         tmp = tag.text[:2] + instrument['alt'] + tag.text[2:]
        #         myDict["Allegerns Codes"] = allergen_codes.text.append(tmp)
        #     else:   # if we haven't found an <img> tag we just print 'tag.text'
        #         print(tag.text)


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

# def cachetodaysmeals():
#     meals = ["breakfast", "lunch", "dinner"]
#     dhs = ["mcmahon", "south", "north", "buckley", "northwest", "putnam", "whitney", "gelfenbien"]
#     # today_meals = []
#     for h in dhs:
#         for m in meals:
#             print(h + "/" + m)
#             # data = getMeals(h + "/" + m)
#             # today_meals.append(data)
#             # __import__('pprint').pprint(json.dumps(data))
#
#     # TODO convert to a csv file
#     # return today_meals


def main():

    today = date.today()
    dd = today.strftime("%d")
    mm = today.strftime("%m")
    yyyy = today.strftime("%Y")

    data = []
    # d0 = getMeals("mcmahon/breakfast")
    d1 = getMeals("mcmahon/lunch")
    # print(type(d1))
    for i in d1:
        print(i)
    # d2 = getMeals("mcmahon/dinner")
    # d3 = getMeals("south/breakfast")
    # d4 = getMeals("south/lunch")
    # d5 = getMeals("south/dinner")
    # d6 = getMeals("north/breakfast")
    # d7 = getMeals("north/lunch")
    # d8 = getMeals("north/dinner")
    # d9 = getMeals("buckley/breakfast")
    # d10 = getMeals("buckley/lunch")
    # d11 = getMeals("buckley/dinner")
    # d12 = getMeals("northwest/breakfast")
    # d13 = getMeals("northwest/lunch")
    # d14 = getMeals("northwest/dinner")
    # d15 = getMeals("putnam/breakfast")
    # d16 = getMeals("putnam/lunch")
    # d17 = getMeals("putnam/dinner")
    # d18 = getMeals("whitney/breakfast")
    # d19 = getMeals("whitney/lunch")
    # d20 = getMeals("whitney/dinner")
    # d21 = getMeals("gelfenbien/breakfast")
    # d22 = getMeals("gelfenbien/lunch")
    # d23 = getMeals("gelfenbien/dinner")

    # data.extend((d1))
    # data.extend((d0, d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12, d13, d14, d15, d16, d17, d18, d19, d20, d21, d22, d23))
    # jdata = json.dumps(data, indent=4)
    
    
    # # data = cachetodaysmeals()
    # __import__('pprint').pprint(data)
    # __import__('pprint').pprint(jdata)
    # __import__('pprint').pprint(type(data))

    # csv_file = dd+mm+yyyy+'data.json'
    # with open(csv_file, 'w') as f:
    #     f.write(jdata)
    
    # csv_writer = csv.writer(data_file)
    # count = 0
    # for d in data:
    #     if count == 0:
    #         header = d.keys()
    #         csv_writer.writerow(header)
    #         count += 1
    #     csv_writer.writerow(d.values())
    # data_file.close()

if __name__ == "__main__":
    main()
    # cachetodaysmeals()
