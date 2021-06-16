def calculate_load(data, p):
    p_name = data[0][p]
    discharge_index = data[0].index("Streamflow, ft&#179;/s") #don't know if all sites use this name, need abrev. table
    scalar = 900
    is_discharge = False
    annual_load = 0

    cur_discharge = 0
    cur_p_val = 0

    concentrations = ["Nitrate plus nitrite, water, in situ, mg/L as N", "Dissolved oxygen, water, unfiltered, mg/L"]
    if p_name in concentrations:
        scalar = 900 * 28.317 * (1/1000000)
    elif p_name == "Specific conductance, water, unfiltered, microsiemens per centimeter at 25&#176;C":
        scalar = 900 * 28.317 * (1/1000000) * (1/0.6)
    elif p_name == "Streamflow, ft&#179;/s":
        is_discharge = True
    else:
        return "N/A"

    if is_discharge:
        for row in data[1:]:
            if row[p] != '':
                cur_p_val = float(row[p])
            annual_load += cur_p_val * scalar
    else:
        cur_discharge_val = 0
        for row in data[1:]:
            if row[p] != '':
                cur_p_val = float(row[p])
            if row[discharge_index] != '':
                cur_discharge_val = float(row[discharge_index])
            annual_load += cur_p_val * cur_discharge_val * scalar
    return annual_load