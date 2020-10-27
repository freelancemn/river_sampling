import math
import requests

def get_url(lon_w, lon_e, lat_upper, lat_lower):
  '''Returns a USGS url for sites contained in the coordinate rectangle'''
  #start building url for waterservices
  url = "http://waterservices.usgs.gov/nwis/site/?format=rdb&bBox="
  #use the coords for the current sliver 
  url += str(lon_w)[:7] + "," + str(lat_lower)[:7] + ","
  url += str(lon_e)[:7] + "," + str(lat_upper)[:7]
  #only grab sites that are active and have auto sampling
  url += "&siteType=ST&siteStatus=active&hasDataTypeCd=dv"
  return url

def extract_ids(url):
  '''Returns the site ids from the url that use automatic sampling'''
  response = requests.get(url)  #get sites in sliver from USGS
  if response.status_code == 200: #if no errors occurred
    with open("auto_sites.txt", "a") as myfile:
      for line in response.text.splitlines():
        if line[:4] == "USGS":  #write the site ids to auto_sites.txt
          myfile.write(line.split()[1] + "\n")

def get_auto_sites(lon_w, lon_e, lat_n, lat_s):
  '''Writes to auto_sites.txt the site ids within the coordinate rectangle that use automatic sampling'''
  open('auto_sites.txt', 'w').close()   #clear autosite's current ids 
  
  #area of lat*lon can't exceed 25
  #lat * abs(lon_w - lon_e) < 25, lat < 25/abs(lon_w - lon_e)
  #use 24 instead of 25 because rounding
  lat_range = abs(24/(lon_w - lon_e))

  #the number of slivers will be difference between latitudes
  #divided by the lat_range
  num_slivers = math.ceil(abs(lat_n - lat_s)/lat_range)
  #round up for the for loop

  #Go through each horizontal sliver of the bounding box:
  for sliver in range(num_slivers):
    #get the lower and upper latitudes of the sliver
    lat_lower = lat_s + sliver*lat_range
    lat_upper = lat_lower + lat_range

    #on the final sliver make sure it doesn't exceed lat_n
    if lat_upper > lat_n:
      lat_upper = lat_n

    url = get_url(lon_w, lon_e, lat_upper, lat_lower)
    #print(url)
    extract_ids(url)
  print("\nall done")