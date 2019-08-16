"""
    This module handels the netlist and holds the circuit-object
    :copyright: (c) 2019 by Tobias Klein.
"""

import sys
import numpy as np
from sympy import Matrix
import functionLib

class Transistor:
    """Simple class to store capacitators"""
    def __init__(self, name, fluss_in, fluss_out, value, function):
        self.name = name
        self.fluss_in = fluss_in
        self.fluss_out = fluss_out
        self.value = value
        self.function = function

class Widerstand:
    """Simple class to store resistors"""
    def __init__(self, name, fluss_in, fluss_out, value, function):
        self.name = name
        self.fluss_in = fluss_in
        self.fluss_out = fluss_out
        self.value = value
        self.function = function

class Spule:
    """Simple class to store coils"""
    def __init__(self, name, fluss_in, fluss_out, value, function):
        self.name = name
        self.fluss_in = fluss_in
        self.fluss_out = fluss_out
        self.value = value
        self.function = function

class V:
    """Simple class to store v-sources"""
    def __init__(self, name, fluss_in, fluss_out, value, function):
        self.name = name
        self.fluss_in = fluss_in
        self.fluss_out = fluss_out
        self.value = value
        self.function = function

class Erzeuger:
    """Simple class to store i-sources"""
    def __init__(self, name, fluss_in, fluss_out, value, function):
        self.name = name
        self.fluss_in = fluss_in
        self.fluss_out = fluss_out
        self.value = value
        self.function = function

class NetListHandler:
    """This class handles and holds the netlist"""

    def __init__(self, *args, **kwargs):
        """Inits the needed values"""
        super().__init__(*args, **kwargs)
        self.fileLines = []

    def readFile(self, filename):
        """Reads a netlist

        :param filename: Name of file for reading
        :return: Netlist as list of strings
        :rtype: list."""

        f = open(filename, "r")
        with open(filename) as f:
            content = f.readlines()
            content = [x.strip() for x in content] 

        result = []

        for line in content:
            if line[0] == "#":
                result.append(line[1:])

        return(result)

    def writeFile(self, filename):
        """ Writes the netlist to file

        :param filename: Name of file to write to"""

        with open(filename, 'w') as f:
            for item in self.fileLines:
                
                f.write("%s\n" % item) 
    
    def addLineToNetlist(self, name, eFromIndex, eToIndex, value, function):
        """ Add a new component to the netlist

        :param name: Name of new component
        :param eFromIndex: Potencial, where the power comes in the new component
        :param eToIndex: Potencial, where the power goes to
        :param value: Starting value of component (currently only for coils)
        :param function: Behavior of component"""

        self.fileLines.append("#" + str(name) + "-" + str(eFromIndex) + "-" + str(eToIndex) + "-" + str(value) + "-" + str(function))

    def addPotencialLineToNetList(self, name, value):
        """Adds a new potencial to the netlist
        
        :param name: name of potencial
        :param value: value of potencial"""
        self.fileLines.append("#" + str(name) + "-" + str(value))
    
class Schaltung:
    """This class holds the circuit"""
    def __init__(self, input_data):

        """Init the circuit values based on the values of the netlist"""
        self.input_data = input_data
        self.transitoren = []
        self.widerstaende = []
        self.spulen = []
        self.vs = []
        self.erzeuger = []
        self.potencialList = []

        self.inzidenz_c = [[]]
        self.inzidenz_g = [[]]
        self.inzidenz_l = [[]]
        self.inzidenz_v = [[]]
        self.inzidenz_i = [[]]
        

        maxPotenzialNr = 0
        for element in input_data:
           
            if element[0] == "G":
                name, fluss_in, fluss_out, value, function = element.split("-")
                temp_widerstand = Widerstand(name, int(fluss_in), int(fluss_out), value, function)
                self.widerstaende.append(temp_widerstand)

            elif element[0] == "C":
                name, fluss_in, fluss_out, value, function = element.split("-")
                temp_transitor = Transistor(name, int(fluss_in), int(fluss_out), value, function)
                self.transitoren.append(temp_transitor)

            elif element[0] == "L":
                name, fluss_in, fluss_out, value, function = element.split("-")
                temp_Spule = Spule(name, int(fluss_in), int(fluss_out), value, function)
                self.spulen.append(temp_Spule)
            elif element[0] == "V":
                name, fluss_in, fluss_out, value, function = element.split("-")
                temp_vs = V(name, int(fluss_in), int(fluss_out), value, function)
                self.vs.append(temp_vs)
            elif element[0] == "I":
                name, fluss_in, fluss_out, value, function = element.split("-")
                temp_erzeuger = Erzeuger(name, int(fluss_in), int(fluss_out), value, function)
                self.erzeuger.append(temp_erzeuger)
            else:
                name, value = element.split("-")
                self.potencialList.append(value)

            if int(fluss_in) > maxPotenzialNr:
                maxPotenzialNr = int(fluss_in)
            elif int(fluss_out) > maxPotenzialNr:
                maxPotenzialNr = int(fluss_out)
        
        maxPotenzialNr += 1
        
        
        self.potenzialNumber = maxPotenzialNr
    
    def initInzidenzMatritzen(self):
        """Inits the inzidenz-matrices of the circuit"""
        
        maxPotenzialNr = self.potenzialNumber
        masseknoten = 0


        self.inzidenz_c = np.zeros((len(self.transitoren), maxPotenzialNr))

        for i in range(len(self.transitoren)):
            transistor = self.transitoren[i]
            
            self.inzidenz_c[i][transistor.fluss_in] = 1
            self.inzidenz_c[i][transistor.fluss_out] = -1

        self.inzidenz_g = np.zeros((len(self.widerstaende), maxPotenzialNr))

        for i in range(len(self.widerstaende)):
            widerstand = self.widerstaende[i]
            
            self.inzidenz_g[i][widerstand.fluss_in] = 1
            self.inzidenz_g[i][widerstand.fluss_out] = -1


        self.inzidenz_l = np.zeros((len(self.spulen), maxPotenzialNr))
        for i in range(len(self.spulen)):
            spule = self.spulen[i]
            
            self.inzidenz_l[i][spule.fluss_in] = 1
            self.inzidenz_l[i][spule.fluss_out] = -1


        self.inzidenz_v = np.zeros((len(self.vs), maxPotenzialNr))

        for i in range(len(self.vs)):
            v = self.vs[i]
            
            self.inzidenz_v[i][v.fluss_in] = 1
            self.inzidenz_v[i][v.fluss_out] = -1


        self.inzidenz_i = np.zeros((len(self.erzeuger), maxPotenzialNr))

        for i in range(len(self.erzeuger)):
            erzeug = self.erzeuger[i]
            
            self.inzidenz_i[i][erzeug.fluss_in] = 1
            self.inzidenz_i[i][erzeug.fluss_out] = -1

        self.inzidenz_c = np.delete(self.inzidenz_c, masseknoten, 1).transpose()

        self.inzidenz_g = np.delete(self.inzidenz_g, masseknoten, 1).transpose()

        self.inzidenz_i = np.delete(self.inzidenz_i, masseknoten, 1).transpose()

        self.inzidenz_l = np.delete(self.inzidenz_l, masseknoten, 1).transpose()

        self.inzidenz_v = np.delete(self.inzidenz_v, masseknoten, 1).transpose()

    def getGr(self):
        """Provides all the functions from the resistors of the circuit

        :return: List of all the resistor functions
        :rtype: vector"""

        listOfFunctions = []
        for widerstand in self.widerstaende:
            functionVector = getattr(functionLib, widerstand.function)()
            listOfFunctions.append(functionVector[0])
        return listOfFunctions

    def getV_t(self):
        """Provides all the functions from the v-sources of the circuit

        :return: List of all the v-sources functions
        :rtype: vector"""

        listOfFunctions = []
        for v in self.vs:
            functionVector = getattr(functionLib, v.function)()
            listOfFunctions.append(functionVector[0])
        return listOfFunctions

    def getI_t(self):
        """Provides all the functions from the i-sources of the circuit

        :return: List of all the i-sources functions
        :rtype: vector"""

        listOfFunctions = []
        for i in self.erzeuger:
            functionVector = getattr(functionLib, i.function)()
            listOfFunctions.append(functionVector[0])
        return listOfFunctions

    def getC_dx(self):
        """Provides all the derivative (regarding x) functions from the capacitors of the circuit

        :return: List of all the capacitator functions
        :rtype: vector"""
        listOfFunctions = []
        
        
        for c in self.transitoren:
            functionVector = getattr(functionLib, c.function)()
            listOfFunctions.append(functionVector[1])
        return listOfFunctions

    def getC_dt(self):
        """Provides all the derivative (regarding time) functions from the capacitors of the circuit

        :return: List of all the capacitator functions
        :rtype: vector"""

        listOfFunctions = []
        for c in self.transitoren:
            
            functionVector = getattr(functionLib, c.function)()
            listOfFunctions.append(functionVector[2])
        return listOfFunctions

    def getL_dx(self):
        """Provides all the derivative (regarding x) functions from the coils of the circuit

        :return: List of all the coils functions
        :rtype: vector"""

        listOfFunctions = []
        for l in self.spulen:
            functionVector = getattr(functionLib, l.function)()
            listOfFunctions.append(functionVector[1])
        return listOfFunctions

    def getL_dt(self):
        """Provides all the derivative (regarding t) functions from the coils of the circuit

        :return: List of all the coils functions
        :rtype: vector"""

        listOfFunctions = []
        for l in self.spulen:
            functionVector = getattr(functionLib, l.function)()
            listOfFunctions.append(functionVector[2])
        return listOfFunctions

    def getjl(self):
        """Provides the starting values of jl
        :return: Staring jl - values
        :rtype: vector"""

        if not self.spulen:
            return np.zeros((0,1))

        else:
            jl = []
            for x in self.spulen:
                jl.append(float(x.value))
            return np.array(jl)







