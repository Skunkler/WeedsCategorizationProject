import arcpy
from arcpy import env



class ReadFile():
    
    
    def __init__(self, filePath):
        self.filePath = filePath
        self.__InvasiveWeeds = []
        self.__NoxiousWeeds = []
        self.__NWP = []
        self.__native = []
        self.__other = []
        self.__bareground = []

    def setWeeds(self):
        readFile = open(self.filePath, "r")
        lines = readFile.readlines()
        
        for line in lines:
            if line.split(',')[1] == "invasive\n":
                self.__InvasiveWeeds.append(line.split(',')[0].lower())
            elif line.split(',')[1] == "noxious\n":
                self.__NoxiousWeeds.append(line.split(',')[0].lower())
            elif line.split(',')[1] == "No Weeds Present\n":
                self.__NWP.append(line.split(",")[0].lower())
            elif line.split(",")[1] == "bare ground\n":
                self.__bareground.append(line.split(",")[0].lower())
            elif line.split(",")[1] == "native\n":
                self.__native.append(line.split(",")[0].lower())
            elif line.split(",")[1] == "other\n":
                self.__other.append(line.split(",")[0].lower())



    def getNoxWeeds(self):
        return self.__NoxiousWeeds

    def getInvWeeds(self):
        return self.__InvasiveWeeds

    def getNatweeds(self):
        return self.__native


    def getOthweeds(self):
        return self.__other


    def getNWP(self):
        return self.__NWP

    def getBareGround(self):
        return self.__bareground






class Find_Weeds():
    
    
    def __init__(self, ws):
        self.ws = ws
        

    def __SearchCursor(self, fc, fieldName):
        CommonNameList = []
        with arcpy.da.SearchCursor(fc, fieldName) as cursor:
            string = ""
            for row in cursor:
                string = str(row[0])
                CommonNameList.append(string.lower())
        return CommonNameList


    def __findCommonField(self, fc):
        fields = arcpy.ListFields(fc)
        FieldList = ["Commonname", "COMMON_NAME", "COMMON_NAM", "Common_Name", "Noxious", "Target_Wee"]
        newSet = 0
        
        for field in fields:
            if field.name in FieldList:
                newSet = set(self.__SearchCursor(fc, field.name))
        return newSet        

    def __findMissingPlants(self, firstList, secondList):
        r = ReadFile(r"D:\NorthernResources\Weeds.csv")
        r.setWeeds()

        for i in firstList:
            for elem in i[1].copy():
                if elem in r.getNoxWeeds():
                    i[1].remove(elem)

        for x in secondList:
            for elem in x[1].copy():
                if elem in r.getInvWeeds():
                    x[1].remove(elem)

        print "Outputting Noxious Files"
        outFile = open(r"D:\NorthernResources\\Noxious" + '.txt' ,"w")
        for i in firstList:
            if len(i[1]) != 0:
                outFile.write("missing types of Noxious plants from " + str(i[0]) + '\n')
                for elem in i[1]:
                    outFile.write(elem + '\n')
        outFile.close()

            
        outFile2 = open(r"D:\NorthernResources\\Invasive" + '.txt' ,"w")
        for i in secondList:
            if len(i[1]) != 0:
                outFile2.write("missing types of Invasive plants from " + str(i[0]) + '\n')
                for elem in i[1]:
                    outFile2.write(elem + '\n')
        outFile2.close()
            
    def findDS(self):
        env.workspace = self.ws   
        fds = arcpy.ListDatasets()
        firstListSet = []
        secondListSet = []

        
        for ds in fds:
            if ds == "Noxious_Survey":
                env.workspace = self.ws + '\\' + ds
                fcs = arcpy.ListFeatureClasses()
                fcSetVal = 0
                for fc in fcs:
                    if fc != "TCWC_Invasive_Weed_Survey_Ranches_2008":
                        fcSetVal = self.__findCommonField(fc)
                        firstListSet.append((fc, fcSetVal))
            elif ds == "Invasive_Survey":
                env.workspace = self.ws + '\\' + ds
                fcs = arcpy.ListFeatureClasses()
                fcSetVal = 0
                for fc in fcs:
                    if fc != "TCWC_Invasive_Weed_Survey_Ranches_2008":
                        fcSetVal = self.__findCommonField(fc)
                        secondListSet.append((fc, fcSetVal))
                

        

        self.__findMissingPlants(firstListSet, secondListSet)






class Clean_Weeds():
    #r = ReadFile(r"")
    #r.setWeeds()
    def __init__(self, ws):
        self.ws = ws
        
    def __checkAgainst_Inv_weeds(self, fc, keyWord):
        env.workspace = self.ws

        fds = arcpy.ListDatasets()

        for ds in fds:
            if ds == "Invasive_Survey":
                env.workspace = self.ws + '\\' + ds
                fcs = arcpy.ListFeatureClasses()
                for fc2 in fcs:
                    if keyWord in fc2 and fc2.split('_')[-1] == fc.split('_')[-1]:
                        if "Areas" in fc2 and "Areas" in fc:
                            return fc2
                        elif "Poly" in fc2 and "Poly" in fc:
                            return fc2
                        elif "Points" in fc2 and "Points" in fc:
                            return fc2

    def __defineMultFiles(self, fc, fc2, keyWord):
        print(fc, fc2)

        firstPath = self.ws + '\\Noxious_Survey\\' + fc
        secondPath = self.ws + '\\Invasive_Survey\\' + fc2
        dsc = arcpy.Describe(fc)

        targetPath = self.ws + '\\TCW_Weeds\\'
        targetName = 'TCWC_Weed_Survey_' + keyWord + fc.split("_")[-1]
        arcpy.CreateFeatureclass_management(targetPath, targetName, dsc.shapeType, fc, "", "", dsc.spatialReference)
        arcpy.MakeFeatureLayer_management(targetPath + targetName, "targetLyr")
        arcpy.MakeFeatureLayer_management(firstPath, "NoxLyr")
        arcpy.MakeFeatureLayer_management(secondPath, "InvLyr")
        print("appending " + fc + " to target layer")

        arcpy.Append_management("NoxLyr", "targetLyr", "NO_TEST")
        print("Success")
        print("now appending " + fc2 + " to target layer")
        arcpy.Append_management("InvLyr", "targetLyr", "NO_TEST")
        print("Success")



    def __defineSingleFiles(self, fc, keyWord,ds, addKey=None):
        env.workspace = self.ws
        env.overwriteOutput = True
        dsc = arcpy.Describe(fc)

        print("append old single feature classes to new" + fc)
        inputLayer = self.ws + '\\' + ds + '\\' + fc
        targetLayerOut = self.ws + '\\' + 'TCW_Weeds\\'
        if addKey == None:
            TargetLayer = "TCWC_Weed_Survey_" + keyWord + "_" + fc.split("_")[-1]
        else:
            TargetLayer = "TCWC_Weed_Survey_" + keyWord + "_" + addKey + "_" + fc.split("_")[-1]

        arcpy.MakeFeatureLayer_management(inputLayer, 'singleFCLy')
        arcpy.CreateFeatureclass_management(targetLayerOut,TargetLayer, dsc.shapeType, fc, "", "", dsc.spatialReference)
        arcpy.MakeFeatureLayer_management(targetLayerOut + TargetLayer, "targetLyr")


        arcpy.Append_management(
            inputs="singleFCLy",
            target="targetLyr",
            schema_type="NO_TEST",
            subtype="")


        print(fc, TargetLayer)
        print("process complete")




    def Organize_weeds(self):
        
        env.workspace = self.ws
        env.overwriteOutput = True
        fds = arcpy.ListDatasets()
        compareDict = dict()

        for ds in fds:
            if ds == "Noxious_Survey":

                env.workspace = self.ws + '\\' + ds

                fcs = arcpy.ListFeatureClasses()
                for fc in fcs:
                    if "Ranch" in fc:
                        compareDict[fc] = self.__checkAgainst_Inv_weeds(fc, "Ranch")
                    elif "Warm" in fc:
                        compareDict[fc] = self.__checkAgainst_Inv_weeds(fc, "Warm_Springs")
                    elif "Test" in fc:
                        compareDict[fc] = self.__checkAgainst_Inv_weeds(fc, "Test_Well_Site")




        env.workspace = self.ws
        env.overwriteOutput = True

        for ds in fds:
            if ds == "Invasive_Survey":
                env.workspace = self.ws + '\\' + ds
                fcs = arcpy.ListFeatureClasses()
                for fc in fcs:
                    if "Ranch_Treatment" in fc and "Areas" in fc and fc not in compareDict.values():
                        self.__defineSingleFiles(fc, "Ranch_Treatment",ds)

                    elif "Ranch_Treatment" in fc and fc not in compareDict.values():
                        self.__defineSingleFiles(fc, "Ranch_Treatment", ds, "Points")

                    elif "Warm_Springs" in fc and "Poly" in fc and fc not in compareDict.values():
                        self.__defineSingleFiles(fc,"Warm_Springs",ds, "Poly")
                    elif "Test_Well_Site_Treatment" in fc and "Areas" in fc and fc not in compareDict.values():
                        self.__defineSingleFiles(fc, "Test_Well_Site_Treatment",ds, "Areas")
                    elif "Test_Well_Site_Treatment" in fc and fc not in compareDict.values():
                        self.__defineSingleFiles(fc, "Test_Well_Site_Treatment", ds, "Points")



        for key in compareDict:
            # if compareDict[key] == None and "Ranch" in key and "Areas" in key:
            #     self.__defineSingleFiles(key, "Ranch_Treatment", "Noxious_Survey", "Areas")

            if compareDict[key] != None and "Ranch" in key:
                self.__defineMultFiles(key, compareDict[key], "Ranch_Treatment")

            elif compareDict[key] != None and "Warm_Springs" in key:
                self.__defineMultFiles(key, compareDict[key], "Warm_Springs")

            elif compareDict[key] != None and "Test_Well_Site" in key:
                self.__defineMultFiles(key, compareDict[key], "Test_Well_Site_Treatment")

            elif compareDict[key] == None and "Ranch" in key:
               self.__defineSingleFiles(key, "Ranch_Treatment", "Noxious_Survey", "Points")

            elif compareDict[key] == None and "Warm_Springs" in key and "Poly" in key:
                self.__defineSingleFiles(key, "Warm_Springs","Noxious_Survey", "Poly")

            elif compareDict[key] == None and "Warm_Springs" in key:
                self.__defineSingleFiles(key, "Warm_Springs", "Noxious_Survey", "Points")

            elif compareDict[key] == None and "Test_Well_Site_Treatment" in key and "Areas" in key:
                self.__defineSingleFiles(key, "Test_Well_Site_Treatment", "Noxious_Survey", "Areas")
            elif compareDict[key] == None and "Test_Well_Site_Treatment" in key:
                self.__defineSingleFiles(key, "Test_Well_Site_Treatment", "Points")


class define_weed_types():

    r = ReadFile(r"D:\NorthernResources\Weeds.csv")
    r.setWeeds()

    def __init__(self, ws):
        self.ws = ws

    def __def(self, InvWeed, TypeVal):
        env.workspace = self.ws

        env.overwriteOutput = True
        FieldList = ["Commonname", "COMMON_NAME", "COMMON_NAM", "Common_Name", "Noxious", "Target_Wee"]


        fcs = arcpy.ListFeatureClasses()
        for fc in fcs:
            fields = arcpy.ListFields(fc)
            names = [fieldex.name for fieldex in fields]
            codeblock = """def getVal(input):
              return input"""
            for i in FieldList:
                if i in names and names.count("Type") > 0:
                    print("type field already exists for" + fc)
                    arcpy.MakeFeatureLayer_management(fc, "lyr")

                    arcpy.SelectLayerByAttribute_management("lyr", "NEW_SELECTION", "LOWER(" + i + ") = '{}'".format(InvWeed))
                    arcpy.CalculateField_management("lyr", "Type", "getVal("+str(TypeVal)+")", "PYTHON_9.3", codeblock)
                    arcpy.SelectLayerByAttribute_management("lyr", "CLEAR_SELECTION")
                    print("success")
                elif i in names and names.count("Type") == 0:
                    print("Creating type field and calculation for " + fc)

                    arcpy.MakeFeatureLayer_management(fc, "lyr")
                    arcpy.AddField_management("lyr", "Type", "SHORT")
                    arcpy.SelectLayerByAttribute_management("lyr", "NEW_SELECTION", i + " = '{}'".format(InvWeed))
                    arcpy.CalculateField_management("lyr", "Type", "getVal("+str(TypeVal)+")", "PYTHON_9.3", codeblock)
                    arcpy.SelectLayerByAttribute_management("lyr", "CLEAR_SELECTION")
                    print("success")


    def defineType(self):



        for i in define_weed_types.r.getInvWeeds():

            self.__def(i, 1)
        for i in define_weed_types.r.getNoxWeeds():

            self.__def(i,2)
        for i in define_weed_types.r.getNWP():

            self.__def(i,3)
        for i in define_weed_types.r.getBareGround():

            self.__def(i,4)
        for i in define_weed_types.r.getOthweeds():

            self.__def(i,5)
        for i in define_weed_types.r.getNatweeds():

            self.__def(i,6)







    
print "Hello"
ws = r"D:\NorthernResources\Weeds.gdb\TCW_Weeds"

a = define_weed_types(ws)
a.defineType()
