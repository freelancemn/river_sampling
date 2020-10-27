def select_element(name, l, return_int=False):
  print("Select", name)
  counter = 0
  #Enumerate and display elements
  for element in range(len(l)):
    counter += 1
    print(str(counter) + ":\t" + str(l[element]))
  choice = int(input("Enter an index (integer):\t"))

  while choice < 1 or choice > len(l):
    choice = int(input("Not within bounds. Enter an index:\t"))
  print()

  #If returning integer instead of element, use 0 index
  if return_int:
    return choice
  return l[choice - 1]

def select_integer(name, lower=0, upper=0, as_int = True):
  message = ":\t"
  #If bounds weren't specified, don't enforce them
  if not (lower == 0 and upper == 0):
    message = " between " + str(lower) + " and " + str(upper) + ":\t"
  choice = input("Select " + name + message)

  if lower != 0 and upper != 0:
    while int(choice) < lower or int(choice) > upper:
      choice = input("Not within bounds. Enter an integer:\t")
  print()

  if as_int:
    return int(choice)
  return choice