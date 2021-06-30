import get_time
import menu
import model

class Base_Model(model.Model):
  def cull(self):
    '''base model has no culling strategy'''
    pass

class Time_Model(model.Model):
  def cull(self):
    '''remove samples based on day of week and time of day'''
    weekdays = get_time.get_weekdays()
    time_range = get_time.time_range()
    new_samples = []

    for sample in self.samples:
      if get_time.in_range(sample[0], weekdays, time_range):
        new_samples.append(sample)

    self.samples = new_samples

def choose_model():
  '''user may select a model'''
  options_dict = {
    "None": Base_Model, 
    "Time": Time_Model
  }
  options = list(options_dict.keys())
  choice = menu.select_element("Sampling strategy type", options)
  return options_dict[choice]