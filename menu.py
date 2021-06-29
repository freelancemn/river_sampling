from os import listdir

def assert_integer(n):
  '''returns true if string represents an integer'''
  for i in n:
    try:
      val = int(i)
    except ValueError:
      print("Invalid input, enter an integer!")
      return False
  return True

def in_bounds(n, lower, upper):
  '''returns true if integer n is between lower and upper, both inclusive'''
  if lower == 0 and upper == 0:
    return True
  for i in n:
    j = int(i)
    if j < lower or j > upper:
      print("Must be greater than " + str(lower) + " and less than " + str(upper))
      return False
  return True

def select_element(name, l, return_index=False, single=True):
  '''select element from list, or elements separated by spaces'''
  choice = ""
  single_msg = "" if single else "(May enter multiple ints separated by spaces)\n"

  while True:
    print("Select", name)
    counter = 0
    #Enumerate and display elements
    for element in range(len(l)):
      counter += 1
      print(str(counter) + ":\t" + str(l[element]))
    choice = input(single_msg + "Enter an index (integer):\t").split(" ")

    if assert_integer(choice) and in_bounds(choice, 1, len(l)):
      break
  choice = list(map(int, choice))

  print()
  #If returning integer instead of element, use 0 index
  if return_index:
    return choice[0] if single else choice
  return l[choice[0] - 1] if single else [l[x - 1] for x in choice]

def select_integer(name, lower=0, upper=0, as_int=True):
  '''input number within bounds'''
  choice = ""
  
  while True:
    message = ":\t"
    #If bounds weren't specified, don't enforce them
    if not (lower == 0 and upper == 0):
      message = " between " + str(lower) + " and " + str(upper) + ":\t"
    choice = input("Select " + name + message).split(" ")

    if assert_integer(choice) and in_bounds(int(choice), lower, upper):
      break

  if as_int:
    return int(choice[0])
  return choice[0]

def select_site(message = "site", single=True):
  '''User chooses from sites held in site_data folder'''
  if single:
    return select_element(message, listdir("site_data") + ["Exit"])
  else:
    return multiselect(listdir("site_data"), message)

def multiselect(ls, name = "option"):
  '''binary select multiple options from list of strings'''
  #start off with all unselected
  choices = [False for x in range(len(ls) + 3)]
  #3 extra spaces: select all, unselect all, continue respectively

  while (not choices[-1]):  #while continue isn't selected
    options = ["[" + ("Y" if choices[x] else "N") + "] " + ls[x] for x in range(len(ls))]
    options += ["Select all", "Unselect all", "Continue"]
    
    choice = select_element(name, options, return_index=True, single=False)
    choice = [x - 1 for x in choice]  #make 0 indexed

    for c in choice:  #allow for multiple choices separated by spaces
      if c == len(options) - 3:  #select all case
        choices = [True for x in range(len(options))]
        choices[-1] = False   #keep the continue choice the same
      elif c == len(options) - 2:  #unselect all case
        choices = [False for x in range(len(options))]
      else:
        #flip bool value at chosen index in options
        choices[c] = not choices[c]
  
  return choices[:-3]   #return choices (aside from select/continue)