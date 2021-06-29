import get_auto_sites
import get_site_data
import load_calculator
import sample_analysis
import site_management
import sparse_dataset_creator
import settings
import get_time
import menu

#print(numpy.percentile([1,12,3,5,31], settings.percentile_grain))

#print(get_time.select_datetime("make pasta"))

#get_site_data.extract_data("03346500", 2019)
#sample_analysis.collect_samples(False)
'''
week = get_time.range_week()
t = get_time.range_time()

print(get_time.time_codify(week, t))

'''
pizzas = ["cheese", "meaty", "veggie", "fishy"]
print(menu.multiselect(pizzas))

main_menu_options = ["Analyze site", "Site management", "Discharge record maker"]
main_menu_options += ["Sparse dataset maker", "Quit"]
main_menu = menu.select_element("Main menu", main_menu_options)

while main_menu != "Quit":
    if main_menu == "Analyze site":
        sample_analysis.analyze()
    elif main_menu == "Site management":
        site_management.interface()
    elif main_menu == "Discharge record maker":
        load_calculator.discharge_record()
    elif main_menu == "Sparse dataset maker":
        sparse_dataset_creator.make_sparse_dataset()
    main_menu = menu.select_element("Main menu", main_menu_options)