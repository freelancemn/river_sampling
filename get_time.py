import menu
from datetime import datetime
from tzlocal import get_localzone
import settings

def get_weekdays():
  '''returns list of bools for selected weekdays, 0 is Monday'''
  weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
  return menu.multiselect(weekdays, "day of week")

def time_range():
  '''Input a range of hours defined by a start and end hour'''
  start = menu.select_integer("starting hour (inclusive)", 0, 23)
  end = 0
  
  while end <= start:
    end = menu.select_integer("ending hour (exclusive)", start + 1, 24)
  return (start, end)

def in_range(dt, weekdays, time_range):
  '''Returns true if datetime falls in temporal range'''
  dt_object = datetime.fromisoformat(dt)
  if weekdays[dt_object.weekday()] == True:
    if dt_object.hour >= time_range[0] and dt_object.hour < time_range[1]:
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

def choose_month(year):
  '''(Returns date, whether special), user chooses month or special date, must not be in future'''
  months = ["January", "February", "March", "April", "May", "June", "July"]
  months += ["August", "September", "October", "November", "December"]

  month_dict = {months[m-1]:datetime(year, m, 1) for m in range(1, len(months)+1)}
  month_dict["Start of year"] = datetime(year, 1, 1)
  month_dict["End of water year"] = datetime(year, 9, 30)
  month_dict["Start of water year"] = datetime(year, 10, 1)
  month_dict["End of year"] = datetime(year, 12, 31)
  
  cur_dt = datetime.today()   #only present option if it's not in future
  options = [m for (m,d) in month_dict.items() if cur_dt > d]
  choice = menu.select_element("month", options)
  return (month_dict[choice], (True if choice not in months else False))

def select_datetime(prompt, just_year = False):
  '''Ask user to select date between settings.earliest year and now'''
  print(prompt)
  now = datetime.now()
  tz = get_localzone()

  #If current year is chosen, make maximum month the current month
  year = menu.select_integer("Year", settings.earliest_year, now.year)
  if just_year:
    return tz.localize(datetime(year, 1, 1, 0, 0))
  
  (month_year, is_special) = choose_month(year)
  if is_special:  #skip choosing day/time if special date is chosen
    return tz.localize(month_year)
  
  #Specify maximum day of month depending on month and leap year
  max_day = 31
  month = month_year.month
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