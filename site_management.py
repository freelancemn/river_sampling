import get_auto_sites
import get_site_data
from os import listdir
import menu
import os
import settings

def interface():
  options = ["Add site", "Remove site", "Refresh auto site list", "Exit"]
  choice = menu.select_element("Site management", options)
  while choice != "Exit":
    if choice == "Add site":
      add_site()
    elif choice == "Remove site":
      remove_site()
    elif choice == "Refresh auto site list":
      get_auto_sites.get_auto_sites(settings.us_w, settings.us_e, settings.us_n, settings.us_s)
    choice = menu.select_element("Site management", options)

def add_site():
  '''Add a site to site_data if it's in auto_sites.txt'''
  site = menu.select_integer("site number", 0, 0, False)

  q_prompt = "How should values known to be less than the reported value be handled?"
  q_options = ["v: use minimum reporting value", "m: use mean (half of minimum reporting value)", "0: use 0"]
  q_mode = menu.select_element(q_prompt, q_options)[0]

  with open("auto_sites.txt", "r") as file:
    for line in file:
      #If the site id is found in auto_sites.txt, get its data
      if site == line.rstrip():
        get_site_data.extract_data(site, q_mode, settings.earliest_year)
        return
  #site was not in the list of auto sites, will attempt to add site and mark filename as 'not auto'
  print("Site number wasn't found in list of automatic sites, will mark site file as 'not auto'")
  get_site_data.extract_data(site, q_mode, settings.earliest_year, " not auto")

def remove_site():
  '''Remove a site from site_data'''
  site = menu.select_element("site", listdir("site_data") + ["Exit"])
  if site == "Exit":
    return
  
  file_location = "site_data/" + site
  os.remove(file_location)