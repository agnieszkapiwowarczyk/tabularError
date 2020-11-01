# -*- coding: utf-8 -*-
#####
#TabularError.pyt/Indexes
#obliczanie wskaźników oceny kartogramu: TAI, OAI, BAI, MAI, BAIS, D, AG, C, HN
#parametry: warstwa wejściowa, wskaźniki oceny, katalog roboczy, plik wynikowy
#wskaźniki oceny kartogramu
#Agnieszka Piwowarczyk,21.06.2018r.,
#ver.1.0
####
 
import arcpy
import decimal
from dbfpy import dbf
import os
import math
import codecs


class Toolbox(object):
	def __init__(self):
		"""Define the toolbox (the name of the toolbox is the name of the
		.pyt file)."""
		self.label = "Tabular Error"
		self.alias = ""

		# List of tool classes associated with this toolbox
		self.tools = [TabularError]


class TabularError(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Tabular Error"
		self.description = "Calculation the most important indexes of choropleth map: TAI, OAI, BAI, MAI, BAIS, D, AG, C, HN" 
		self.canRunInBackground = False

	def getParameterInfo(self):
		"""Define parameter definitions"""
			# First parameter
		param0 = arcpy.Parameter(
		displayName="Warstwa Wejściowa",
		name="Layer",
		datatype="GPString",
		parameterType="Required",
		direction="Input")
		
			#  Second parameter		  
		param1 = arcpy.Parameter(
		displayName="Wskaźniki oceny kartogramu",
		name="Calculation_Index",
		datatype="GPString",
		parameterType="Required",
		direction="Input",
		multiValue=True)
		param1.filter.type = "Value List"
		param1.filter.list = ["TAI", "BAI","OAI", "MAI", "D", "BAIS", "AG", "C", "HN"]
			
			# Third parameter
		param2 = arcpy.Parameter(
		displayName="Katalog roboczy",
		name="out_folder",
		datatype="DEFolder",
		parameterType="Required",
		direction="Input")
		
			# Fourth parameter
		param3 = arcpy.Parameter(
		displayName="Plik wynikowy",
		name="out_file",
		datatype="DEFile",
		parameterType="Required",
		direction="Output")
		param3.filter.list = ['txt', 'csv']
		params = [param0, param1, param2, param3]
		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True

	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""

		Layer = []	   
		stringFilter = parameters[0].filter
		stringFilter.list = []
		fc= arcpy.mapping.MapDocument("CURRENT")
		for lyr in arcpy.mapping.ListLayers(fc):
			if lyr.symbologyType == "GRADUATED_COLORS":
				Layer.append(lyr.name)
		stringFilter.list = Layer
		return

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	def execute(self, parameters, messages):
		"""The source code of the tool."""
		layer = parameters[0].valueAsText
		table = "NS_elec_neigh"
		disolve="Agregacja"
		index= parameters[1].valueAsText
		folder = parameters[2].valueAsText
		output = parameters[3].valueAsText
		
		#Class with parameters
		New = Indexes(folder, layer, table, disolve, output)
		New.dataPath();
		
		#Splitting indicators into groups - they use the same methods from class Indexes
		Table=[]
		for j in index.split( ";" ):
			Table.append(j);
		
		TAIOAID = ["TAI","OAI","D"]
		HN = ["HN"]
		BAIBAISMAI = ["BAI", "BAIS, MAI"]
		AGC = ["AG","C"]
		c=[i for i in Table if i in TAIOAID]
		d=[i for i in Table if i in HN]
		e=[i for i in Table if i in BAIBAISMAI]
		f=[i for i in Table if i in AGC]

		if len(c)!= 0:
			New.readData()
			New.initialValues()
			if len(d)!= 0:
				New.newField()
				New.polygonCalculation()
				if len(f)!= 0:
					New.readDbf()
					if len(e)!= 0:
						New.border()
				elif len(e)!= 0:
					New.readDbf()
					New.border()
			elif len(f)!= 0:
				New.newField()
				New.polygonCalculation()
				New.readDbf()
				if len(e)!= 0:
					New.border()
			elif len(e)!= 0:
				New.newField()
				New.polygonCalculation()
				New.readDbf()
				New.border()
		elif len(d)!= 0:
			New.readData()
			New.initialValues()
			New.newField()
			New.polygonCalculation()
			if len(f)!= 0:
				New.readDbf()
				if len(e)!= 0:
					New.border()
			elif len(e)!= 0:
				New.readDbf()
				New.border()
		elif len(f)!= 0:
			New.readData()
			New.initialValues()
			New.newField()
			New.polygonCalculation()
			New.readDbf()
			if len(e)!= 0:
				New.border()
		elif len(e)!= 0:
			New.readData()
			New.initialValues()
			New.newField()
			New.polygonCalculation()
			New.readDbf()
			New.border()
		
		
		
		#Writing of final results
		print (arcpy.arcpy.AddMessage("_________________________________________ \n \n WYNIKI \n"))
		text= []
		text.append("Obliczane wskaźniki: " +"\n")
		for i in xrange(len(Table)):
			if Table[i]=='TAI':
				New.TAI()
				text.append("Tabular Accuracy Index (TAI) wynosi  "+str(New.TAI) +"\n")
				print (arcpy.arcpy.AddMessage("Tabular Accuracy Index (TAI) wynosi {0}".format(New.TAI)))
			elif Table[i]=='OAI':
				New.OAI()
				text.append("Overview Accuracy Index (OAI) wynosi  "+str(New.OAI) +"\n")
				print (arcpy.arcpy.AddMessage("Overview Accuracy Index (OAI) wynosi {0}".format(New.OAI)))
			elif Table[i]=='BAI':
				New.BAI()
				text.append("Boundary Accuracy Index (BAI) wynosi  "+str(New.BAI) +"\n")
				print (arcpy.arcpy.AddMessage("Boundary Accuracy Index (BAI) wynosi {0}".format(New.BAI)))
			elif Table[i]=='BAIS':
				New.BAIS()
				text.append("BAIS wynosi  "+str(New.BAIS) +"\n")
				print (arcpy.arcpy.AddMessage("BAIS wynosi {0}".format(New.BAIS)))
			elif Table[i]=='MAI':
				if Table.count('TAI') == 0:
					New.TAI()
				if Table.count('OAI') == 0:
					New.OAI()
				if Table.count('BAI') == 0:
					New.BAI()
				New.MAI()
				text.append("Map Accuracy Index (MAI) wynosi  "+str(New.MAI) +"\n")
				print (arcpy.arcpy.AddMessage("Map Accuracy Index (MAI) wynosi {0}".format(New.MAI)))
			elif Table[i]=='AG':
				New.AG()
				text.append("Aggregation Index (AG) wynosi  "+str(New.AG) +"\n")
				print (arcpy.arcpy.AddMessage("Aggregation Index (AG) wynosi {0}".format(New.AG)))
			elif Table[i]=='C':
				New.Contrast()
				text.append("Contrast Index (C) wynosi  "+str(New.C) +"\n")
				print (arcpy.arcpy.AddMessage("Contrast Index (C) wynosi {0}".format(New.C)))
			elif Table[i]=='D':
				New.D()
				text.append("Average Difference Index (D) wynosi  "+str(New.D) +"\n")
				print (arcpy.arcpy.AddMessage("Average Difference Index (D) wynosi {0}".format(New.D)))
			elif Table[i]=='HN':
				New.HN()
				text.append("Relative Entropy Index (Hn) wynosi  "+str(New.HN) +"\n")
				print (arcpy.arcpy.AddMessage("Relative Entropy Index (Hn) wynosi {0}".format(New.HN)))

		New.saveFile(text)
		print (arcpy.arcpy.AddMessage("_________________________________________ \n \n "))
		return

class Indexes(object):
	#method of class initialisation (used in execute in 111 line)
	def __init__(self,c,l,f,p,o):
		self.catalog = c
		self.layer = l
		self.Filename = f
		self.Filedisolve = p
		self.outputfile = o
		self.LowLimit = []
		self.UpLimit = []
		self.data = []
		self.FieldsArea = []
		self.range = []
		self.AverageOfRange = []
		self.TablePolygonNeighbors = []
	#creating paths to work files ("NS_elec_neigh.shp", "Agregacja.dbf")
	def dataPath(self):
		self.filename = os.path.join(self.catalog, self.Filename + ".dbf")
		self.filedisolve = os.path.join(self.catalog, self.Filedisolve  + ".shp")
		print(arcpy.arcpy.AddMessage("pliki robocze: \n {0} \n {1}... ".format(self.filename,self.filedisolve)))
		return
		

	def __del__(self):
		#Delate file with information about classification and disolve ("NS_elec_neigh.shp", "Agregacja.dbf")
		for suffix in (".shp",".shx", ".prj", ".dbf", ".cpg", ".sbx", ".sbn",".shp.xml"):
			filename = os.path.join(self.catalog, self.Filedisolve + suffix)
			if os.path.isfile(filename) :
				os.unlink(filename)
				if suffix == ".shp":
					print(arcpy.arcpy.AddMessage("Usuwanie pliku {0}... ".format(filename)))
			else :
				if suffix == ".shp":
					print(arcpy.arcpy.AddMessage("Wybacz, plik {0} nie istnieje...".format(filename)))
		for suffix in (".dbf",".cpg", ".dbf.xml"):
			filename = os.path.join(self.catalog, self.Filename + suffix)
			if os.path.isfile(filename) :
				os.unlink(filename)
				if suffix == ".dbf":
					print(arcpy.arcpy.AddMessage("Usuwanie pliku {0}... ".format(filename)))
			else :
				if suffix == ".dbf":
					print(arcpy.arcpy.AddMessage("Wybacz, plik {0} nie istnieje...".format(filename)))
		 
	def readData(self):
		#Getting the value of the layer: data source (dataSource), defined class ranges (BreakValues),
		#number of defined classes (NumClasses), the name of the field, that was used for the classification (fieldName)
		mxd = arcpy.mapping.MapDocument("CURRENT")
		for lyr in arcpy.mapping.ListLayers(mxd):
			if lyr.name == self.layer:	
				lyrSymbolClass = lyr.symbology
				self.dataSource = lyr.dataSource
				self.BreakValues = lyrSymbolClass.classBreakValues
				self.NumClasses = lyrSymbolClass.numClasses
				self.fieldName = lyrSymbolClass.valueField
				#messages:
				print (arcpy.arcpy.AddMessage("Wybrana warstwa: {0}".format(self.layer)))
				print (arcpy.arcpy.AddMessage("Warstwa {0} posiada symbolizację dla pola {1} podzieloną na {2} klas".format(lyr.name,self.fieldName,self.NumClasses )))
		del mxd

		#Getting the value of the field- SearchCursor
		self.Field={}
		with arcpy.da.SearchCursor(self.dataSource, [self.fieldName, "Shape_Area"]) as rows:
			for row in rows:
				self.data.append(row[0])
				self.Field[row[0]]=row[1]
		#Writting all data:
		#print (arcpy.arcpy.AddMessage("Dane: \n {0} \n ".format(self.data)))
		del row				

	def newField(self):
		#Adding new field where is information about class- AddField, UpdateCursor for numClasses
		arcpy.AddField_management(self.dataSource, "ClassNum", "LONG")
		rows = arcpy.UpdateCursor(self.dataSource)
		for row in rows:
			for x in xrange(self.NumClasses):
				if row.getValue(self.fieldName) == self.X1:
					row.setValue("ClassNum", 0)
					rows.updateRow(row)
				elif (self.LowLimit[x] < row.getValue(self.fieldName) <= self.UpLimit[x]):
					row.setValue("ClassNum", x)
					rows.updateRow(row)
		del row, rows

	def polygonCalculation(self):
		#Creating new file with information about classification, delete field with class 
		arcpy.PolygonNeighbors_analysis(self.dataSource, self.filename, [self.fieldName, "ClassNum","Shape_Area"],"NO_AREA_OVERLAP", "NO_BOTH_SIDES")
		arcpy.Dissolve_management(self.dataSource,self.filedisolve,"ClassNum","ClassNum COUNT","SINGLE_PART","UNSPLIT_LINES")
		arcpy.AddGeometryAttributes_management(self.filedisolve,"AREA","","SQUARE_METERS","")
		arcpy.DeleteField_management(self.dataSource, "ClassNum")
		
		#Getting the value of the field in Disolve - SearchCursor
		self.AreaHomogeneousClass=[]
		with arcpy.da.SearchCursor(self.filedisolve, [ "POLY_AREA"]) as rows:
			for row in rows:
				self.AreaHomogeneousClass.append(row[0])
		return self.AreaHomogeneousClass 
		del row
		
	def readDbf (self):
		#Using dbfpy module and reading file with information about classification "Agregacja.dbf"
		dbfFile = dbf.Dbf(self.filename, True)
		for i in xrange(len(dbfFile.fieldNames)-1):
			Table = []
			for rec in dbfFile:
				Table.append(rec[dbfFile.fieldNames[i]])
			self.TablePolygonNeighbors.append(Table)
		print (arcpy.arcpy.AddMessage("Czytanie pliku DBF ..."))
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
		#self.dot = abs(d.as_tuple().exponent)
		self.dot= 3
		self.average = round(sum(self.data)/len(self.data),self.dot)
		self.Xi_Xsr = [abs(round((i-self.average),self.dot)) for i in self.data]
		for data in self.data:
			self.FieldsArea.append(self.Field[data])
			
		#Verification that the maximum value equals the upper limit 
		if self.Xn != self.UpLimit[self.NumClasses-1]:
			print (arcpy.arcpy.AddMessage("__________________________________________________________\n \n "))
			print (arcpy.arcpy.AddMessage("Uwaga! Proszę sprawdzić górną granicę najwyższej klasy, to nie jest wartość maksymalna dla zbioru. Wartość maksymalna wynosi {0} \n".format(self.Xn)))
			print (arcpy.arcpy.AddMessage("__________________________________________________________"))
			self.UpLimit[self.NumClasses-1] = self.Xn
		
		#Writing messages:
		print (arcpy.arcpy.AddMessage("X min: {0}, X max {1}, Średnia: {2}, Miejsca po przecinku: {3}".format(self.X1, self.Xn,self.average,  self.dot)))
		print (arcpy.arcpy.AddMessage(" Dolne granice klas: {0} \n Górne granice klas: {1}".format(self.LowLimit, self.UpLimit)))

		#Sorting of data into classes and calculation of average
		for x in xrange(self.NumClasses):
			xclass = []
			for i in xrange(len(self.data)):
				if self.data[i] != self.LowLimit[x]:
					if (self.LowLimit[x] <= self.data[i] < self.UpLimit[x]):
						Xi=self.data[i]
						xclass.append(Xi)
					elif (self.LowLimit[x] <= self.data[i] <= self.UpLimit[x]):
						Xi=self.data[i]
						xclass.append(Xi)
				else:
					if self.data[i] == self.X1:
						Xi=self.data[i]
						xclass.append(Xi)
					elif (self.LowLimit[x] < self.data[i] <= self.UpLimit[x]):
						Xi=self.data[i]
						xclass.append(Xi)
			self.range.append(xclass)
		
			if len(xclass) !=0:
				average = round(sum(xclass) / len(xclass),self.dot)
			else:
				average = 0
			self.AverageOfRange.append(average)
		#print (arcpy.arcpy.AddMessage("Ilość danych ... {0}, ilość danych w klasie: {1}".format(len(self.data),len(xclass))))
		#print (arcpy.arcpy.AddMessage("Klasy ... {0}".format(self.range)))
		print (arcpy.arcpy.AddMessage("Średnie w klasach: {0}".format(self.AverageOfRange)))
		del xclass
		return self.LowLimit, self.UpLimit, self.Xn, self.X1, self.average, self.AverageOfRange
	
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
		for x in xrange(numBordersDifferentClasses):
			self.maxBordersValue.append(self.bordersValue[x])
		self.bordersValue.reverse()
		for x in xrange(numBordersSameClasses):
			self.minBordersValue.append(self.bordersValue[x])
		print (arcpy.arcpy.AddMessage(" Obliczanie wartości granicznych..."))
		#print (arcpy.arcpy.AddMessage("{0}".format(self.TablePolygonNeighbors)))
		#print (arcpy.arcpy.AddMessage("Borders: BordersDifferentClasses {0}, numBordersSameClasses {1}".format(numBordersDifferentClasses, numBordersSameClasses)))
		#print (arcpy.arcpy.AddMessage("Borders: liczba max {0}, liczba min {1}".format(len(self.maxBordersValue), len(self.minBordersValue))))
		return
	
	def TAI(self):
		#Calculation TAI
		sumLine = []
		for x in xrange(self.NumClasses):
			ac = [abs(c-self.AverageOfRange[x]) for c in self.range[x]]
			sumLine.append(sum(ac))
		sumAll=sum(sumLine)
		self.TAI=round(1 - sumAll/sum(self.Xi_Xsr),self.dot)
		del ac, sumLine
		#print (arcpy.arcpy.AddMessage(" TAI = 1 - {0} / {1} = {2}".format(sumAll, sum(self.Xi_Xsr), self.TAI)))
		return self.TAI
	
	def OAI (self):
		Line = []
		First = []
		Second = []
		for x in xrange(self.NumClasses):
			AC = [abs(c-self.AverageOfRange[x]) for c in self.range[x]]
			Line.extend(AC)
			x=x+1
		#print (arcpy.arcpy.AddMessage("Line: {0}, Fields: {1}".format(len(Line),len(self.FieldsArea))))
		for x in xrange(len(self.data)):
			First.append(Line[x]*self.FieldsArea[x])
			Second.append(self.Xi_Xsr[x]*self.FieldsArea[x])
		self.OAI=1- round(sum(First)/sum(Second), self.dot)
		#print (arcpy.arcpy.AddMessage(" OAI = 1 - {0} / {1} = {2}".format(sum(First), sum(Second), self.OAI)))
		return self.OAI
	
	def D (self):
		Xo=[]
		rangeClasses=[]
		Di=[]
		for i in xrange(self.NumClasses):
			Xo.append((self.UpLimit[i]+self.LowLimit[i])/2)
			rangeClasses.append(self.UpLimit[i]-self.LowLimit[i])
			i=i+1
		for i in xrange(self.NumClasses):
			if self.AverageOfRange[i] !=0:
				Di.append(abs(rangeClasses[i]/Xo[i]-rangeClasses[i]/self.AverageOfRange[i]))
				self.D=round(sum(Di), self.dot)
			i=i+1
		#print (arcpy.arcpy.AddMessage("Range: {0}, Average of range: {1}, AverageClasses: {2}".format(rangeClasses,Xo,self.AverageOfRange)))
		#print (arcpy.arcpy.AddMessage(" D  = {0}".format(self.D)))
		return self.D
	
	def BAI (self):
		#BAI= B/b (suma wartości granic oznaczonych na danym kartogramie między 
		#polami należacymi do różnych klas podzielona przez sume wartości 
		#najwyższych granic, których liczba odpowiada liczbie granic międzyklasowych).
		B=float(sum(self.bordersValueDifferentClasses))
		b=float(sum(self.maxBordersValue))
		if b != 0:
			self.BAI=round(B/b,self.dot)
			#print (arcpy.arcpy.AddMessage(" BAI = {0} / {1} = {2}".format(B, b, self.BAI)))
		else:
			self.BAI=0
			print (arcpy.arcpy.AddMessage(" BAI = 0 - kartogram zawiera tylko jedną klasę"))
		return self.BAI		


	def BAIS (self):
		A=float(sum(self.bordersValue))
		B=float(sum(self.bordersValueDifferentClasses))
		C=float(sum(self.bordersValueSameClasses))
		b=float(sum(self.maxBordersValue))
		c=float(sum(self.minBordersValue))
		if B != 0 and C !=0:
			self.BAIS=round(math.sqrt(B/b*c/C*B/A),self.dot)
		elif B==0:
			self.BAIS = 0
			print (arcpy.arcpy.AddMessage(" BAIS = 0 - kartogram zawiera tylko jedną klasę"))
		elif C==0:
			self.BAIS = 0
			print (arcpy.arcpy.AddMessage(" BAIS = 0 - na kartogramie brak granic wewnątrzklasowych"))
		#print (arcpy.arcpy.AddMessage("A: {0} \n B: {1} \n C:{2} \n b: {3} c: {4}".format(self.bordersValue,self.bordersValueDifferentClasses, self.bordersValueSameClasses, self.maxBordersValue,self.minBordersValue)))
		#print (arcpy.arcpy.AddMessage(" BAIS = ({0} / {1})*({2} / {3})*({4} / {5}) = {6}".format(B,b,c,C,B,A, self.BAIS)))
		return self.BAIS	
			
	def MAI (self):
		CAI=round(math.sqrt(self.TAI**2+self.OAI**2+self.BAI**2),self.dot)
		self.MAI=round(CAI/math.sqrt(3),self.dot)
		#print (arcpy.arcpy.AddMessage(" CAI= sqrt(TAI ^2 + OAI ^2 + BAI ^2)= sqrt({0} ^2 + {1} ^2 + {2} ^2 = {3} \n MAI= CAI/sqrt(3)= {4} /sqrt(3)= {5}".format(self.TAI, self.OAI,self.BAI, CAI, CAI,self.MAI)))
		return self.MAI

	def AG (self):
		#Agregation Index (AG)- liczba granic pól należacych do tej samej klasy podzielona przez całkowitą liczbę graniczeń
		self.ab = 0
		for x in xrange(len(self.TablePolygonNeighbors[0])-1):
			if self.TablePolygonNeighbors[2][x] == self.TablePolygonNeighbors[3][x]:
				self.ab=self.ab+1
		self.AG = round(float(self.ab)/len(self.TablePolygonNeighbors[0]),self.dot)
		#print (arcpy.arcpy.AddMessage(" AG = {0} / {1} = {2}".format(self.ab, len(self.TablePolygonNeighbors[0]), self.AG)))		
		return self.AG

	def Contrast(self):
		BrightnessI = []
		BrightnessJ = []
		Cij = []
		AllBorderLength=sum(self.TablePolygonNeighbors[6])
		for x in xrange(len(self.TablePolygonNeighbors[0])):
			BrightnessI.append((self.TablePolygonNeighbors[2][x]+1)*100/(self.NumClasses))
			BrightnessJ.append((self.TablePolygonNeighbors[3][x]+1)*100/(self.NumClasses))
			Cij.append((self.TablePolygonNeighbors[6][x]/AllBorderLength)*abs(BrightnessI[x]-BrightnessJ[x]))
		#print (arcpy.arcpy.AddMessage(" BrightnessI: {0} \n BrightnessJ: {1}".format(BrightnessI,BrightnessJ)))
		self.C = round(sum(Cij),self.dot)
		#print (arcpy.arcpy.AddMessage(" C = {0}".format(self.C)))
		return self.C
	
	def HN(self):
		if len(self.AreaHomogeneousClass) != 1:
			AreaLogArea = []
			AllArea = sum(self.AreaHomogeneousClass)
			for x in xrange(len(self.AreaHomogeneousClass)):
				AreaLogArea.append((self.AreaHomogeneousClass[x]/AllArea)*math.log((self.AreaHomogeneousClass[x]/AllArea),2))
			self.HN = round(-sum(AreaLogArea)/math.log(len(self.AreaHomogeneousClass),2),self.dot)
			#print (arcpy.arcpy.AddMessage(" HN = {0}/ {1} = {2}".format(sum(AreaLogArea),math.log(len(self.AreaHomogeneousClass),2), self.HN)))
		else:
			self.HN = 0
			print (arcpy.arcpy.AddMessage(" HN = 0 - kartogram zawiera tylko jedną klasę"))
		return self.HN
		
	def saveFile(self, line):
		plik = open(self.outputfile, 'w')
		print(arcpy.arcpy.AddMessage("plik końcowy: \n {0} ... ".format(self.outputfile)))
		plik.writelines("Analizowana warstwa " + self.layer + " posiada symbolizacje dla pola " + self.fieldName + "\n" + "Warstwa podzielona jest na " + str(self.NumClasses) + " klas" + "\n" + "\n")
		plik.write("__________________________________________________________" + "\n")
		plik.writelines(line)
				
		plik.close()

