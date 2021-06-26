import menu
from datetime import datetime
import pytz
from tzlocal import get_localzone
import time
import settings

def update_week(week, week_choices):
  '''Update array of selected weeks'''
  #Options for menu
  week_map = week[:] + ["Remove all", "Add all", "Next"]

  #Negate selected status of selected day
  for day in range(len(week)):
    if week_choices[day]:
      week_map[day] = "Remove " + week[day]
    else:
      week_map[day] = "Add " + week[day]
      
  return week_map

def range_week():
  '''Input combination of days of the week'''
  week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
  #Initialize all days of week to be selected
  week_choices = [1] * len(week)
  week_map = update_week(week, week_choices)

  #Select weekday to add or remove
  choice = menu.select_element("day", week_map, True)

  while choice != len(week_map): #if "Next" not chosen, keep asking
    if choice < len(week_map) - 2:  #if a day of week was chosen
      week_choices[choice - 1] = not week_choices[choice - 1]
    elif choice == len(week_map) - 2: #if remove all
      week_choices = [0] * len(week)
    else: #if add all
      week_choices = [1] * len(week)
    week_map = update_week(week, week_choices)
    choice = menu.select_element("day", week_map, True)

  return week_choices

def range_time():
  '''Input a range of hours defined by a start and end hour'''
  start = menu.select_integer("starting hour (inclusive)", 0, 23)
  end = 0
  
  while end <= start:
    end = menu.select_integer("ending hour (exclusive)", start + 1, 24)
  return (start, end)

def in_range(dt, weekdays, time_range):
  '''Returns true if datetime falls in temporal range'''
  if weekdays[dt.weekday()] == True:
    if dt.hour >= time_range[0] and dt.hour < time_range[1]:
      return True

def codify(weekdays, time_range):
  '''Converts sampling strategy into unique 7-digit code'''
  week = 0
  #convert the list of week bits into an int
  for day in weekdays:
    week = (week << 1) | day
  week += 100 #codes can't start with a 0

  #make sure the times line up by adding a 0 if necessary
  time_start = str(time_range[0])
  if len(time_start) < 2:
    time_start = "0" + time_start
  time_end = str(time_range[1])
  if len(time_end) < 2:
    time_end = "0" + time_end

  return str(week) + str(time_start) + str(time_end)

def select_datetime(prompt, just_year = False):
  '''Ask user to select date between settings.earliest year and now'''
  print(prompt)
  now = datetime.now()
  tz = get_localzone()
  months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "Start of year"]

  #If current year is chosen, make maximum month the current month
  year = menu.select_integer("Year", settings.earliest_year, now.year)
  
  if just_year:
    return tz.localize(datetime(year, 1, 1, 0, 0))
  
  max_month = 12
  if year == now.year:
    max_month = now.month
  month = menu.select_element("Month", months, True)
  
  if (month > max_month):
    return tz.localize(datetime(year, 1, 1, 0, 0))
  
  #Specify maximum day of month depending on month and leap year
  max_day = 31
  if month in [4,6,9,11]:
    max_day = 30
  if month == 2:
    max_day = 29
    if year % 4 == 0:
      max_day = 28
  
  #If current year and month chosen, specify max day, hour, minute
  max_hour = 23
  max_minute = 4
  if year == now.year and month == now.month:
    max_day = now.day
    max_hour = now.hour #fix thi slaterffff
    max_minute = now.minute // 15 + 1
  day = menu.select_integer("Day", 1, max_day)
  hour = menu.select_integer("Hour", 0, max_hour)

  #Specify available 15 minute intervals within chosen hour
  minute_options = [str(hour)+":"+str(m*15) for m in range(max_minute)]
  minute_options[0] += "0"
  minute = (menu.select_element("Minute", minute_options, True)-1) * 15

  return tz.localize(datetime(year, month, day, hour, minute))

def select_timerange():
  start_datetime = select_datetime("Selecting start date/time")
  end_datetime = select_datetime("Selecting end date/time")
  
  while end_datetime < start_datetime:
    print("Select an end date/time that's greater than " + str(start_datetime))
    end_datetime = select_datetime("Selecting end date/time")
  return [start_datetime, end_datetime]