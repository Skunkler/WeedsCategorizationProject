import arcpy
from arcpy import env

"""env.workspace = r'D:\NorthernResources\Weeds.gdb\TCW_Weeds'
env.overwriteOutput = True

output = r'D:\NorthernResources\Weeds.gdb\TCWC_Weeds'


fcs = arcpy.ListFeatureClasses()
dsc2 = arcpy.Describe(output+ '\\TCWC_Weed_Survey_Points_2005_2')
for fc in fcs:
    if fc != 'TCWC_Weed_Survey_Points_2005':
        dsc = arcpy.Describe(fc)
        arcpy.CreateFeatureclass_management(output, fc + '_2', dsc.shapeType, fc, "", "", dsc2.spatialReference)
        arcpy.MakeFeatureLayer_management(fc, "lyr")
        arcpy.Append_management("lyr", output + '\\' + fc + '_2', "NO_TEST")"""

env.workspace = r'D:\NorthernResources\Weeds.gdb\TCWC_Weeds'


fcs = arcpy.ListFeatureClasses()

for fc in fcs:
    print "rename " + fc + " to " + fc[:-2]
    arcpy.Rename_management(fc, fc[:-2])
