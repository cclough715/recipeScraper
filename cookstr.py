# Author:   Chad Clough
#           github/cclough715
#
# Created:  3/23/2015

import urllib3
import bs4
from bs4 import BeautifulSoup
import time
from datetime import datetime
import recipeScraper
import pickle


def get_recipe(url):
    '''
        Gets a recipe from cookstr

        Args:
            url: The url to the recipe that were scraping

        Returns:	
            A recipe object with the recipe scraped from the url
    '''
    
    soup = recipeScraper.get_soup_data(url)

    #scrape recipe information
    try:
        name = soup.findAll('span', {"itemprop" : "name"})[0].text
    except IndexError:
        print ("\tError: Recipe name not found")
        name = 'N/A'
    try:   
        author =  soup.findAll('span', {"itemprop" : "author"})[0].text
    except IndexError:
        print ("\tError: Author not found")
        author = 'N/A'
        
    dish = recipeScraper.Recipe(name, author)
    
    attributes = soup.findAll('span', {'class' : "attr value"})
    for attribute in attributes:
        dish.add_attribute(attribute.text)

    ingredients = soup.findAll('span', {"class" : "ingredient"})
    for ingredient in ingredients:
        dish.add_ingredient(ingredient.text)

    return dish
    
def get_random_recipes(n):
    ''' Gets n recipes at random from cookstr

        Args:
            n: The number of recipes to scrape
        returns:
            A list of recipes
	'''
    url = 'http://www.cookstr.com/searches/surprise'
    recipe_list = list()
    
    #retrieve the recipes
    for i in range(1, n):
        try:
            dish = get_recipe(url)
            #check for duplicate recipes
            if dish in recipe_list:
                n = n + 1
                continue
            else:
                recipe_list.append(dish)
                time.sleep(0.2) #prevent ddos
        except Exception, e:
            print("Error = " + str(e))
            n = n + 1

    return recipe_list
    
def get_recipes(query):
    ''' Gets a list of all recipes found with query
        
        Args:
            query: A search term for a type of recipe (ex. 'italian', 'asian', etc.)
            
        Returns:
            A list of all recipes found using the query 
    '''
    recipes = list()
    page = 1
    url = 'http://www.cookstr.com/searches?page=' + str(page) + '&query=' + query
    soup = recipeScraper.get_soup_data(url)
    
    last_page = soup.findAll('span', {"class" : "next_page disabled"})  
    while len(last_page) == 0:
        print ("Scraping page: %d..." % (page))
        #grab each recipe on this search page
        recipe_links = soup.findAll('p', {"class" : "recipe_title"})
        for link in recipe_links:
            recipe_url = 'http://www.cookstr.com' + link.find('a').get('href')
            recipes.append(get_recipe(recipe_url))
        
        #get next page
        page = page + 1
        url = 'http://www.cookstr.com/searches?page=' + str(page) + '&query=' + query
        soup = recipeScraper.get_soup_data(url)
        last_page = soup.findAll('span', {"class" : "next_page disabled"})  
    
    return recipes

if __name__ == '__main__':
    query = 'desert'
    print ("Scraping cookstr for query: '%s'\nThis may take a while...\n" % (query))
    
    start   = datetime.now()
    recipes = get_recipes(query)
    end     = datetime.now()
    elapsed = end - start #calculate total scrape time
    
    #save our recipes to a file
    recipeScraper.save_object(recipes, query + '.p')
    
    #read back the recipes we just scraped
    savedRecipes = recipeScraper.get_object(query + '.p')
    for r in savedRecipes:
        print r
        print '\n'

    print ("Number of recipes found: %d" % (len(savedRecipes)))

    #display total scrape time
    days    = divmod(elapsed.total_seconds(), 86400)
    hours   = divmod(days[1], 3600)
    minutes = divmod(hours[1], 60)
    seconds = minutes[1]
    print ("Total scrape time: %d days, %d hours, %d minutes, %d seconds" % 
        (days[0], hours[0], minutes[0], seconds))