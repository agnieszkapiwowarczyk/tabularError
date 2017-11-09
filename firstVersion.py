# -*- coding: utf-8 -*-
####
#Piwowarczyk.py
#Calculation the most important indexes of choropleth map
#ver.1.1
####

import arcpy
import decimal
from dbfpy import dbf
import os
import math

class TabularError(object):

    def __init__(self,d, f):
        self.DataPath = d
        self.filename = f
        self.LowLimit = []
        self.UpLimit = []
        self.data = []
        self.FieldsArea = []
        self.range = []
        self.AverageOfRange = []
        self.TablePolygonNeighbors = []

    def __del__(self,filename):
        #Delate file with information about classification
        if os.path.isfile(filename) :
            os.unlink(filename)
        else :
            print("Wybacz, plik nie istnieje :(")
            
    def readData(self):
        #Getting the value of the layer: data source (dataSource), defined class ranges (BreakValues),
        #number of defined classes (NumClasses), the name of the field, that was used for the classification (fieldName)
        mxd = arcpy.mapping.MapDocument(self.DataPath)
        for lyr in arcpy.mapping.ListLayers(mxd):
            if lyr.symbologyType == "GRADUATED_COLORS":              
                lyrSymbolClass = lyr.symbology
                self.dataSource = lyr.dataSource
                self.BreakValues = lyrSymbolClass.classBreakValues
                self.NumClasses = lyrSymbolClass.numClasses
                self.fieldName = lyrSymbolClass.valueField
            else: print "Doesn't exist"

        #Getting the value of the field
        self.Field={}
        with arcpy.da.SearchCursor(self.dataSource, [self.fieldName, "Shape_Area"]) as rows:
            for row in rows:
                self.data.append(row[0])
                self.Field[row[0]]=row[1]
        del row                
#zmienic!! ale jeszcze nie wiem jak powinno byc poprawnie
    def newField(self):
        #Adding new field where is information about class
        arcpy.AddField_management(self.dataSource, "ClassNumber", "LONG")
        rows = arcpy.UpdateCursor(self.dataSource)
        for row in rows:
            for x in xrange(self.NumClasses):
                if (self.LowLimit[x] <= row.getValue(self.fieldName) < self.UpLimit[x]):
                    row.setValue("ClassNumber", x)
                    rows.updateRow(row)
                elif (self.LowLimit[x] <= row.getValue(self.fieldName) <= self.UpLimit[x]):
                    row.setValue("ClassNumber", self.NumClasses)
                    rows.updateRow(row)
        del row, rows
#zmienione 03.06
    def polygonCalculation(self):
        #Creating new file with information about classification, delete field with class 
        arcpy.PolygonNeighbors_analysis(self.dataSource, self.filename, [self.fieldName, "ClassNumber","Shape_Area"],"NO_AREA_OVERLAP", "NO_BOTH_SIDES")
        Disolve="ROBOCZY\\agregacja2.shp"
        arcpy.Dissolve_management(self.dataSource,Disolve,"ClassNumber","ClassNumber COUNT","SINGLE_PART","UNSPLIT_LINES")
        arcpy.AddGeometryAttributes_management(Disolve,"AREA","","SQUARE_METERS","")
        arcpy.DeleteField_management(self.dataSource, "ClassNumber")
        #Getting the value of the field in Disolve
        self.AreaHomogeneousClass=[]
        with arcpy.da.SearchCursor(Disolve, [ "POLY_AREA"]) as rows:
            for row in rows:
                self.AreaHomogeneousClass.append(row[0])
        return self.AreaHomogeneousClass 
        del row   

    def readDbf (self):
        #Using dbfpy module and reading file with information about classification
        dbfFile = dbf.Dbf(self.filename, True)
        for i in xrange(len(dbfFile.fieldNames)-1):
            Table = []
            for rec in dbfFile:
                Table.append(rec[dbfFile.fieldNames[i]])
            self.TablePolygonNeighbors.append(Table)
        #print self.TablePolygonNeighbors
        dbfFile.close()
        del Table
        
    def initialValues (self):
        #Creating a table with lower and upper class limits
        for i in range(self.NumClasses):
            self.LowLimit.append(self.BreakValues[i])
            i=i+1
            self.UpLimit.append(self.BreakValues[i])

        #Calculation of average, maximum, minimum for data
        self.data.sort()
        self.Xn=max(self.data)
        self.X1=min(self.data)
        d = decimal.Decimal(str(self.data[1]))
        self.dot = abs(d.as_tuple().exponent)
        self.average = round(sum(self.data)/len(self.data),self.dot)
        self.Xi_Xsr = [abs(round((i-self.average),self.dot)) for i in self.data]
        for data in self.data:
            self.FieldsArea.append(self.Field[data])
#zmiana 04.06
        #Sorting data and calculation of average in classes
        for x in xrange(self.NumClasses):
            aa = []
            for i in xrange(len(self.data)):
                if self.data[i] != self.LowLimit[x]:
                    if (self.LowLimit[x] <= self.data[i] < self.UpLimit[x]):
                        Xi=self.data[i]
                        aa.append(Xi)
                    elif (self.LowLimit[x] <= self.data[i] <= self.UpLimit[x]):
                        Xi=self.data[i]
                        aa.append(Xi)

                else:
                    if self.data[i] == self.data[0]:
                        Xi=self.data[i]
                        aa.append(Xi)
                    
                    elif (self.LowLimit[x] < self.data[i] <= self.UpLimit[x]):
                        Xi=self.data[i]
                        aa.append(Xi)
            self.range.append(aa)
            #print "Klasy: ",self.range
            average = round(sum(aa) / len(aa),self.dot);
            self.AverageOfRange.append(average)
        del aa
        return self.LowLimit, self.UpLimit, self.Xn, self.X1, self.average, self.AverageOfRange
#zmienione 4.06
    def border(self):             
        #Calculation: Number of Borders between different classes (numBordersDifferentClasses), 
        #value between all fields (borderValue), value between fields in different classes (bordersValueDifferentClasses),
        #max value between all fields(maxBordersValue)- number value must be the same of number value in table bordersValueDifferentClasses  
        numBordersDifferentClasses = 0
        numBordersSameClasses = 0
        self.bordersValue = []
        self.bordersValueDifferentClasses = []
        self.bordersValueSameClasses = []
        self.maxBordersValue = []
        self.minBordersValue = []
        for i in xrange(len(self.TablePolygonNeighbors[0])):
            self.bordersValue.append(abs(self.TablePolygonNeighbors[0][i]-self.TablePolygonNeighbors[1][i]))
            self.bordersValue.sort()
            self.bordersValue.reverse()
            if self.TablePolygonNeighbors[2][i] != self.TablePolygonNeighbors[3][i]:
                self.bordersValueDifferentClasses.append(abs(self.TablePolygonNeighbors[0][i]-self.TablePolygonNeighbors[1][i]))
                numBordersDifferentClasses = numBordersDifferentClasses + 1
            if self.TablePolygonNeighbors[2][i] == self.TablePolygonNeighbors[3][i]:
                self.bordersValueSameClasses.append(abs(self.TablePolygonNeighbors[0][i]-self.TablePolygonNeighbors[1][i]))
                numBordersSameClasses = numBordersSameClasses + 1
        for x in range(numBordersDifferentClasses):
            self.maxBordersValue.append(self.bordersValue[x])
        self.bordersValue.reverse()
        for x in range(numBordersSameClasses):
            self.minBordersValue.append(self.bordersValue[x])
            
    def TAI(self):
        #Calculation TAI
        sumLine = []
        for x in xrange(self.NumClasses):
            ac = [abs(c-self.AverageOfRange[x]) for c in self.range[x]]
            sumLine.append(sum(ac))
            print sumLine
        sumAll=sum(sumLine)
        self.TAI=round(1 - sumAll/sum(self.Xi_Xsr),self.dot)
        del ac, sumLine
        
        return  'TAI = 1 - %s / %s = %s' % (sumAll, sum(self.Xi_Xsr), self.TAI)

    def OAI (self):
        Line = []
        First = []
        Second = []
        for x in xrange(self.NumClasses):
            AC = [abs(c-self.AverageOfRange[x]) for c in self.range[x]]
            Line.extend(AC)
            x=x+1
        for x in xrange(len(self.data)):
            First.append(Line[x]*self.FieldsArea[x])
            Second.append(self.Xi_Xsr[x]*self.FieldsArea[x])
        self.OAI=1- round(sum(First)/sum(Second), self.dot)
        return 'OAI = 1 - %s / %s = %s' % (sum(First), sum(Second), self.OAI)
    
    def D (self):
        Xo=[]
        rangeClasses=[]
        Di=[]
        for i in xrange(self.NumClasses):
            Xo.append((self.UpLimit[i]+self.LowLimit[i])/2)
            rangeClasses.append(self.UpLimit[i]-self.LowLimit[i])
            i=i+1
        for i in xrange(self.NumClasses):
            Di.append(abs(rangeClasses[i]/Xo[i]-rangeClasses[i]/self.AverageOfRange[i]))
            self.D=round(sum(Di), self.dot)
            i=i+1
        return 'D = %s' % self.D


    def BAI (self):
        #BAI= B/b (suma wartości granic oznaczonych na danym kartogramie między polami należacymi do różnych klas podzielona
        # przez sume wartości najwyższych granic, których liczba odpowiada liczbie granic międzyklasowych).
        B=sum(self.bordersValueDifferentClasses)
        b=sum(self.maxBordersValue)
        self.BAI=round(B/b,self.dot)
        return  'BAI = %s / %s = %s ' %(B, b, self.BAI)

    def BAIS (self):
        A=sum(self.bordersValue)
        B=sum(self.bordersValueDifferentClasses)
        C=sum(self.bordersValueSameClasses)
        b=sum(self.maxBordersValue)
        c=sum(self.minBordersValue)
        self.BAIS=round(math.sqrt(B/b*c/C*B/A),self.dot)
        return 'BAIS= sqrt( (%s / %s )* (%s / %s) * (%s / %s) = %s' %(B,b,c,C,B,A, self.BAIS)        
            
    def MAI (self):
        CAII=math.sqrt(self.TAI**2+self.OAI**2+self.BAI**2)
        CAI=round(CAII,self.dot)
        self.MAI=round(CAI/math.sqrt(3),self.dot)
        return 'CAI= sqrt(TAI ^2 + OAI ^2 + BAI ^2)= sqrt(%s ^2 + %s ^2 + %s ^2)= %s \n MAI= CAI/sqrt(3)= %s /sqrt(3)= %s' %(self.TAI, self.OAI,self.BAI, CAI, CAI,self.MAI)
    def AG (self):
        #Agregation Index (AG)- liczba granic pól należacych do tej samej klasy podzielona przez całkowitą liczbę graniczeń
        self.ab=0
        for x in xrange(len(self.TablePolygonNeighbors[0])-1):
            if self.TablePolygonNeighbors[2][x] == self.TablePolygonNeighbors[3][x]:
                self.ab=self.ab+1
        self.AG=round(float(self.ab)/len(self.TablePolygonNeighbors[0]),self.dot)
        return 'Współczynnik Agregacji (AG) \n AG= %s / %s = %s' %(self.ab, len(self.TablePolygonNeighbors[0]), self.AG)

    def Contrast(self):
        BrightnessI = []
        BrightnessJ = []
        Cij = []
        AllBorderLength=sum(self.TablePolygonNeighbors[6])
        for x in xrange(len(self.TablePolygonNeighbors[0])):
            BrightnessI.append((self.TablePolygonNeighbors[2][x])*100/(self.NumClasses))
            BrightnessJ.append((self.TablePolygonNeighbors[3][x])*100/(self.NumClasses))
            Cij.append((self.TablePolygonNeighbors[6][x]/AllBorderLength)*abs(BrightnessI[x]-BrightnessJ[x]))
        self.C=round(sum(Cij),self.dot)
        return ' Wskazik sredniej roznicy (C): %s' %self.C


    def HN(self):
        AreaLogArea=[]
        AllArea=sum(self.AreaHomogeneousClass)
        for x in xrange(len(self.AreaHomogeneousClass)):
            AreaLogArea.append((self.AreaHomogeneousClass[x]/AllArea)*math.log((self.AreaHomogeneousClass[x]/AllArea),2))
        self.HN=round(sum(AreaLogArea)/math.log(len(self.AreaHomogeneousClass),2),self.dot)
        return self.HN
    
    def _str__(self):
        return '[Tabular Accuracy Index: %s \n Overview Accuracy Index: %s \n D: %s \n Boundary Accuracy Index: %s \n BAIS: %s \n Map Accuracy Index: %s \n Aggregation Index: %s \n Wskaznik Sredniej Roznicy: %s]' % (self.TAI, self.OAI, self.D, self.BAI, self.BAIS, self.MAI, self.AG, self.C)
    def _repr__(self):
        print ' Zrodlo danych: %s \n Pole dla którego wykonano kartogram: %s \n Dane: \n %s \n' % (str(self.dataSource),str(self.fieldName), self.data)
        print ' Wyniki badania najbliższego sąsiada (Dane w polu i / Dane w polu j /  Numer klasy pola i / Numer klasy pola j / /Powierzchnia poligonu i / Powierzchnia poligonu j / Długość granicy \n %s \n' %(self.TablePolygonNeighbors)
        print ' Dane: Min: %s, Max: %s, Srednia: %s, \n Dolne granice : %s \n Górne granice: %s \n Srednie przedziałów: %s  ' %(self.Xn, self.X1, self.average, self.LowLimit, self.UpLimit , self.AverageOfRange)
        print New.TAI
        print New.OAI
        print New.D
        print New.BAI
        print New.BAIS
        print New.MAI
        print New.AG
        #print New.Contrast
        return 'KONIEC'

    def saveFile(self):
        plik=open("D:\\studia\\GiK\\3 mgr\\praca_mgr\\tt.txt", 'w')
        #print(arcpy.arcpy.AddMessage("plik końcowy: \n {0} ... ".format(self.outputfile)))
        plik.writelines("Analizowana warstwa posiada symbolizację dla pola "+self.fieldName +" podzieloną na " + str(self.NumClasses) +" klas" +"\n")
        #plik.writelines("Analizowana warstwa " + self.layer + " podzielona jest na " +str(self.NumClasses) + " klas" +"\n")
        #plik.write("__________________________________________________________"+"\n")
	#plik.writelines(line)
	#self.fieldName.decode(encoding='UTF-8',errors='strict')
	#plik.writelines("symbolizację dla pola "+self.fieldName)
        plik.close()

    
fileName = arcpy.GetParameterAsText(1)
if fileName == '#' or not fileName:
    #fileName = "D:\\studia\\GiK\\3 mgr\\praca_mgr\\DBF\\NS_elec_neigh.dbf"
    fileName = "ROBOCZY\\NS_elec_neigh.dbf"
    
Path = arcpy.GetParameterAsText(0)
if Path == '#' or not Path:
    #Path = r"D:\studia\GiK\3 mgr\praca_mgr\mapa.mxd"
    Path = r"mapa2.mxd"
    
New = TabularError(Path, fileName)
#New.__del__("ROBOCZY\\agregacja2.shp")
#New.__del__(fileName)
New.readData()
New.initialValues()
New.newField()
print New.polygonCalculation()
New.readDbf()
New.border()
New.TAI()
New.OAI()
New.BAI()
New.BAIS()
New.MAI()
New.AG()
New.Contrast()
New.D()
New.HN()
New.saveFile()
print (New)

