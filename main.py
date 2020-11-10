import get_auto_sites
import get_site_data
import sample_analysis
import site_management
import numpy
import settings
import get_time
import menu
import table_math

#print(numpy.percentile([1,12,3,5,31], settings.percentile_grain))

#print(get_time.select_datetime("make pasta"))

#get_site_data.extract_data("03346500", 2019)
#sample_analysis.collect_samples(False)
'''
week = get_time.range_week()
t = get_time.range_time()

print(get_time.time_codify(week, t))
'''

main_menu_options = ["Analyze site", "Site management", "Quit"]
main_menu = menu.select_element("Main menu", main_menu_options)

while main_menu != "Quit":
    if main_menu == "Analyze site":
        sample_analysis.collect_samples()
    elif main_menu == "Site management":
        site_management.interface()
    main_menu = menu.select_element("Main menu", main_menu_options)