import collections
import csv
import datetime
import requests
import settings
import menu

def apply_qualifier(qualifier, value, mode):
  '''Returns val after accounting for qualifier, including multiple cases for <'''
  if qualifier == "A":  #if ok, just use val
    return value
  if qualifier == "e" or "X":  #val was estimated, don't use
    return ''
  if qualifier == "<":  #when val is below min
    if mode == "v":     #if in v mode, use val
      return value
    elif mode == "m":   #if in mean mode, take mean
      return value / 2
    elif mode == "0":   #if in 0 mode, use 0
      return 0
  else:
    return value        #base case
  

def get_url(site, year):
  '''Returns url for data of site during specified year'''
  url = "http://waterservices.usgs.gov/nwis/iv/?format=json&indent=on&sites="
  url += str(site)
  #Make sure they start on January 1st (01-01) and end in December
  url += "&startDT=" + str(year) + "-01-01"
  #No parameters specified so that all variables will be returned
  url += "&endDT=" + str(year + 1) + "-12-31&siteStatus=all"
  return url
  
def extract_data(site, q_mode, start_year=settings.earliest_year):
  '''Writes to file in site_data that contains site data since beginning of start year to present'''
  current_year = datetime.datetime.today().year
  file_location = "site_data/" + str(site) + ".csv"
  open(file_location, 'w').close()  #clear the current file
  site_dict = {}
  dict_variables = []

  #Go through each year of site's history write, data to file
  with open(file_location, 'w', newline='') as myfile:
    for year in range(start_year, current_year + 1, 1):
      print("Gathering site data for", year)
      url = get_url(site, year)
      response = requests.get(url)
      if response.status_code == 200: #if USGS doesn't return error
        data = response.json()["value"]["timeSeries"]
        #For each variable in the timeSeries, save the data
        for variable in data:
          var_name = variable["variable"]["variableName"]
          #Record names of new variables for table organization
          if var_name not in dict_variables:
            dict_variables.append(var_name)
          #header_index will align variable values in correct column
          header_index = dict_variables.index(var_name)
          for value in variable["values"][0]["value"]:
            dt = value["dateTime"]
            #If no row represents this datetime, make one
            if dt not in site_dict.keys():
              #Give row correct width
              site_dict[dt] = [None] * len(data)
            q_val = apply_qualifier(value["qualifiers"][0], value["value"], q_mode)
            site_dict[dt][header_index] = q_val
    writer = csv.writer(myfile, delimiter=',')
    #Order the rows by their datetimes
    ordered = collections.OrderedDict(sorted(site_dict.items()))
    first_row = ["DateTimes"] + dict_variables
    writer.writerow(first_row)
    for sample in ordered:
      writer.writerow([sample] + site_dict[sample])
    print("Completed gathering site data")