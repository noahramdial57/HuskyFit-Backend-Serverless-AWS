import boto3
from botocore.exceptions import ClientError
import json
from bs4 import BeautifulSoup as soup
from datetime import date
import requests
import unicodedata
import os
from datetime import datetime, timedelta


def lambda_handler(event, context):
    
    dining_halls = ["Buckley", "Gelfenbien", "Kosher", "Mcmahon", "North", "Northwest", "Putnam", "South", "Whitney"]
    meals = ["Breakfast", "Lunch", "Dinner"]
    
    # Initialize bucket client
    s3_client = boto3.client('s3')
    bucket = "dininghall-data-cache"
    
    # Get tomorrows date
    presentday = datetime.now() # or presentday = datetime.today()
    tomorrow = presentday + timedelta(1)
    date = tomorrow.strftime('%m/%d/%Y') # 07/03/2023
    
    date_parse = date.split('/') # ['03', '04', '2023']
    mm = date_parse[0]
    dd = date_parse[1]
    yyyy = date_parse[2]
    
    for diningHall in dining_halls:
        for meal in meals:
            
            # Writing to file
            file_name = "{}-{}-{}-{}-{}.json".format(diningHall, meal, mm, dd, yyyy)
            path = "/tmp/{}-{}-{}-{}-{}.json".format(diningHall, meal, mm, dd, yyyy)
            data = json.dumps(getMeals(diningHall, meal, date))
            
            # Move to next iteration if there are no meals for this dining hall
            if len(data) == 0:
                continue
            else:
                
                # create file
                f = open(path, 'w+') 
            
                # If file is empty, run the algo and cache the data
                if os.path.getsize(path) == 0:

                    # Cache the data in its corresponding file
                    with open(path, "w") as outfile:
                        outfile.write(data)
                            
                    try:
                        response = s3_client.upload_file(path, bucket, file_name)
                        print(f"{file_name} was successfully added to S3 bucket")
                    except ClientError as e:
                        print(f"There was an error in storing {path} in the S3 bucket.")
                        return False

    content = json.dumps("Data has been successfully added to the S3 bucket.")

    return {
        'statusCode': 200,
        "headers": {
            "Content-Type": "application/json"
        },
        'body': content
    }


def getMeals(dining_hall, meal, date):

    link_list= ["http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=03&locationName=Buckley+Dining+Hall&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate=",                    # 10%2f25%2f2022&mealName=Breakfast"
                "http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=42&locationName=Gelfenbien+Commons%2c+Halal+%26+Kosher&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate=",  # 10%2f27%2f2022&mealName=Breakfast"
                "http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=05&locationName=McMahon+Dining+Hall&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate=",                    # 10%2f27%2f2022&mealName=Breakfast"
                "http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=07&locationName=North+Campus+Dining+Hall&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate=",                 # 10%2f27%2f2022&mealName=Breakfast"
                "http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=15&locationName=Northwest+Marketplace&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate=",                # 10%2f27%2f2022&mealName=Breakfast
                "http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=06&locationName=Putnam+Dining+Hall&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate=",                      # 10%2f27%2f2022&mealName=Breakfast"
                "http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=16&locationName=South+Campus+Marketplace&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate=",                 # 10%2f27%2f2022&mealName=Breakfast"
                "http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=01&locationName=Whitney+Dining+Hall&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate=",
                "http://nutritionanalysis.dds.uconn.edu/longmenu.aspx?sName=UCONN+Dining+Services&locationNum=42&locationName=Gelfenbien+Commons%2c+Halal+%26+Kosher&naFlag=1&WeeksMenus=This+Week%27s+Menus&dtdate="]                    # 10%2f27%2f2022&mealName=Breakfast"

    # string issues with mcmahon
    if dining_hall == "Mcmahon":
        dining_hall = "McMahon"

    # What dining hall is it?
    url = ""
    for link in link_list:
        if dining_hall in link:
            url = link
            break
    
    parse = date.split("/") # ['02', '28', '2023']
    mm = parse[0]
    dd = parse[1]
    yyyy = parse[2]

    edited_url = url + mm + '%2f' + dd + '%2f' + yyyy + '&mealName=' + meal
    buckley = requests.get(edited_url)

    # HTML Parsing
    html = buckley.content
    page_soup = soup(html, "html.parser")

    # Grabs each menu_item
    containers = page_soup.findAll("div", {"class": "longmenucoldispname"})

    L = []
    for menu_item in containers:
        href = menu_item.a['href']
        new_url = "http://nutritionanalysis.dds.uconn.edu/" + href
        label = requests.get(new_url)

        # HTML Parsing
        html2 = label.content
        page_soup = soup(html2, "html.parser")
        nut_facts = set(page_soup.findAll("span", {"class": "nutfactstopnutrient"}))

        calories_val = page_soup.find("td", {"class": "nutfactscaloriesval"})
        serving_size = page_soup.findAll("div", {"class": "nutfactsservsize"})
        allergens = page_soup.find("span", {"class": "labelallergensvalue"})

        myDict = dict()
        myDict["Food Item"] = menu_item.text
        myDict["Dining Hall"] = dining_hall
        myDict["Meal"] = meal
        
        # For menu items with no corresponding Nutrition Labels | Don't include them
        try: 
            myDict["Allergens"] = allergens.text
        except:
            break

        # Get all dietary restrictions
        restrictions = []
        for foo in page_soup.find_all('img', alt=True):
            text = foo['alt']
            if "Gluten Friendly" in text:
                restrictions.append("Gluten Friendly")
                continue
            if "Less Sodium" in text:
                restrictions.append("Less Sodium")
                continue
            if "Smart Check" in text:
                restrictions.append("Smart Check")
                continue

            restrictions.append(text)

        myDict['Dietary Restrictions'] = restrictions
        myDict["Date"] = date
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
            
            if "Total Carbohydrate." in clean_text:
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