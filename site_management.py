import get_site_data
from os import listdir
import menu
import os
import settings

def interface():
  choice = menu.select_element("Site management", ["Add site", "Remove site", "Exit"])
  while choice != "Exit":
    if choice == "Add site":
      add_site()
    elif choice == "Remove site":
      remove_site()
    choice = menu.select_element("Site management", ["Add site", "Remove site", "Exit"])

def add_site():
  '''Add a site to site_data if it's in auto_sites.txt'''
  site = menu.select_integer("site number", 0, 0, False)
  with open("auto_sites.txt", "r") as file:
    for line in file:
      #If the site id is found in auto_sites.txt, get its data
      if site == line.rstrip():
        get_site_data.extract_data(site, settings.earliest_year)
        return
  print("Site number wasn't found in list of automatic sites")

def remove_site():
  '''Remove a site from site_data'''
  site = menu.select_element("site", listdir("site_data") + ["Exit"])
  if site == "Exit":
    return
  
  file_location = "site_data/" + site

  os.remove(file_location)