import arcpy
from arcpy import env

file = r'D:\NorthernResources\Weeds.gdb\TCW_Weeds\TCWC_Weed_Survey_Polys_2019'

readfile = open(r"D:\NorthernResources\Weeds.csv", 'r')

lines = readfile.readlines()
FieldList = ["Commonname", "COMMON_NAME", "COMMON_NAM", "Common_Name", "Noxious", "Target_Wee"]

plantLst = []



def getField(layer):
    names = [field.name for field in arcpy.ListFields(layer)]
    for i in FieldList:
        if i in names:
            return i


for line in lines:
    elem = (line.split(",")[0].lower(), line.split(",")[1][:-1])
    plantLst.append(elem)



arcpy.MakeFeatureLayer_management(file, 'lyr', "TYPE IS NULL")
fieldName = getField("lyr")

for i in plantLst:
    arcpy.SelectLayerByAttribute_management("lyr", "NEW_SELECTION", "LOWER("+fieldName+") = '{}'".format(i[0]))
    if i[1] == "invasive":
        arcpy.CalculateField_management("lyr", "TYPE", 1, "PYTHON_9.3")
    elif i[1] == "noxious":
        arcpy.CalculateField_management("lyr", "TYPE", 2, "PYTHON_9.3")
    elif i[1] == "No Weeds Present":
        arcpy.CalculateField_management("lyr", "Type", 3, "Python_9.3")
    elif i[1] == "bare ground":
        arcpy.CalculateField_management("lyr", "Type", 4, "Python_9.3")
    elif i[1] == "other":
        arcpy.CalculateField_management("lyr", "Type", 5, "PYTHON_9.3")
    elif i[1] == "native":
        arcpy.CalculateField_management("lyr", "Type", 6, "PYTHON_9.3")

