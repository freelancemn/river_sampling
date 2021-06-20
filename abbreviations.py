abbreviations = {
    "Specific conductance, water, unfiltered, microsiemens per centimeter at 25&#176;C": ["SC", "Specific Conductance", "microsiemens per centimeter"],
    "Temperature, water, &#176;C": ["TEMP", "Temperature", "Celsius"],
    "Streamflow, ft&#179;/s": ["Q", "Streamflow", "ft3 per s"],
    "Gage height, ft": ["GH", "Gage Height", "ft"],
    "Dissolved oxygen, water, unfiltered, mg/L": ["DO", "Disolved Oxygen", "mg per L"],
    "pH, water, unfiltered, field, standard units": ["PH", "pH", "standard units"],
    "Orthophosphate, water, in situ, milligrams per liter as phosphorus": ["OP", "Orthophosphate", "miligrams per liter"],
    "Turbidity, water, unfiltered, monochrome near infra-red LED light, 780-900 nm, detection angle 90 &#177;2.5&#176;, formazin nephelometric units (FNU)": ["TURB", "Turbidity", "FNU"],
    "Nitrate plus nitrite, water, in situ, mg/L as N": ["NO3", "Nitrate", "mg per L"],
    "Dissolved organic matter fluorescence (fDOM), water, in situ, concentration estimated from reference material, micrograms per liter as quinine sulfate equivalents (QSE)": ["FDOM", "fDOM", "QSE"],
    "Chlorophyll, total, water, fluorometric, 650-700 nanometers, in situ sensor, micrograms per liter": ["CHLA", "Chlorophyll", "micrograms per liter"],
    "Phycocyanins (cyanobacteria), water, in situ, in vivo fluorescence, in vivo fluorescence units": ["CYAN", "Phycocyanins (cyanobacteria)", "vivo fluorescence units"]
}

def abbreviate(p_name):
    '''returns an abbreviation of a parameter name that is <= 4 characters, or the original name if none exists'''
    if p_name not in abbreviations.keys():
        return p_name
    return abbreviations[p_name][0]

def shorten(p_name):
    '''returns a shortened version of a parameter name with its units, or the original name if none exists'''
    if p_name not in abbreviations.keys():
        return p_name
    return abbreviations[p_name][1] + ", " + abbreviations[p_name][2]