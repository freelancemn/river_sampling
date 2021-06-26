from os import listdir

def assert_integer(i):
  '''returns true if string represents an integer'''
  try:
    val = int(i)
    return True
  except ValueError:
    print("Invalid input, enter an integer!")
    return False

def in_bounds(n, lower, upper):
  '''returns true if integer n is between lower and upper, both inclusive'''
  if lower == 0 and upper == 0:
    return True
  if n < lower or n > upper:
    print("Must be greater than " + str(lower) + " and less than " + str(upper))
    return False
  return True

def select_element(name, l, return_int=False):
  choice = ""
  while True:
    print("Select", name)
    counter = 0
    #Enumerate and display elements
    for element in range(len(l)):
      counter += 1
      print(str(counter) + ":\t" + str(l[element]))
    choice = input("Enter an index (integer):\t")

    if assert_integer(choice) and in_bounds(int(choice), 1, len(l)):
      break

  print()
  choice = int(choice)

  #If returning integer instead of element, use 0 index
  if return_int:
    return choice
  return l[choice - 1]

def select_integer(name, lower=0, upper=0, as_int = True):
  choice = ""
  
  while True:
    message = ":\t"
    #If bounds weren't specified, don't enforce them
    if not (lower == 0 and upper == 0):
      message = " between " + str(lower) + " and " + str(upper) + ":\t"
    choice = input("Select " + name + message)

    if assert_integer(choice) and in_bounds(int(choice), lower, upper):
      break
  
  choice = int(choice)

  if as_int:
    return int(choice)
  return choice

def select_site():
  '''User chooses from sites held in site_data folder'''
  return select_element("site", listdir("site_data") + ["Exit"])