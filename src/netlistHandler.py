import sys
import numpy as np
from sympy import Matrix

class Transistor:
    def __init__(self, name, fluss_in, fluss_out, widerstand):
        self.name = name
        self.fluss_in = fluss_in
        self.fluss_out = fluss_out
        self.widerstand = widerstand

class Widerstand:
    def __init__(self, name, fluss_in, fluss_out, widerstand):
        self.name = name
        self.fluss_in = fluss_in
        self.fluss_out = fluss_out
        self.widerstand = widerstand

    def __str__(self):
        return "Widerstandname: " + self.name + " | Rein: " + str(self.fluss_in) + " | Raus: " + str(self.fluss_out) + "\n"

    def __repr__(self):
        return "Widerstandname: " + self.name + " | Rein: " + str(self.fluss_in) + " | Raus: " + str(self.fluss_out) + "\n"

class Spule:
    def __init__(self, name, fluss_in, fluss_out, widerstand):
        self.name = name
        self.fluss_in = fluss_in
        self.fluss_out = fluss_out
        self.widerstand = widerstand

class V:
    def __init__(self, name, fluss_in, fluss_out, f_t):
        self.name = name
        self.fluss_in = fluss_in
        self.fluss_out = fluss_out
        self.f_t = f_t

class Erzeuger:
    def __init__(self, name, fluss_in, fluss_out, f_t):
        self.name = name
        self.fluss_in = fluss_in
        self.fluss_out = fluss_out
        self.f_t = f_t

class NetListHandler:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fileLines = []

    def readFile(self, filename):
        f = open(filename, "r")
        with open(filename) as f:
            content = f.readlines()
            content = [x.strip() for x in content] 

        result = []

        for line in content:
            if line[0] == "#":
                result.append(line[1:])

        return(result)

    def writeFile(self, filename, potenzialNummer):
        print("Hi")
        for i in range(0, len(self.fileLines)-1):
            k = self.fileLines[i].split("-")
            print(k)
            if k[0] == -10:
                k[0] = potenzialNummer
                print("K1")
            if k[1] == -10:
                k[1] = potenzialNummer
                print("K2")

        with open(filename, 'w') as f:
            for item in self.fileLines:
                f.write("%s\n" % item) 
    
    def addLineToNetlist(self, name, eFromIndex, eToIndex, value):
        self.fileLines.append("#" + str(name) + "-" + str(eFromIndex) + "-" + str(eToIndex) + "-" + str(value))

    def addPotencialLineToNetList(self, name, value):
        self.fileLines.append("#" + str(name) + "-" + str(value))
    
class Schaltung:
    def __init__(self, input_data):
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
            print(element)
            
            #Widerstand
            if element[0] == "G":
                name, fluss_in, fluss_out, value = element.split("-")
                temp_widerstand = Widerstand(name, int(fluss_in), int(fluss_out), value)
                self.widerstaende.append(temp_widerstand)

            elif element[0] == "C":
                name, fluss_in, fluss_out, value = element.split("-")
                temp_transitor = Transistor(name, int(fluss_in), int(fluss_out), value)
                self.transitoren.append(temp_transitor)

            elif element[0] == "L":
                name, fluss_in, fluss_out, value = element.split("-")
                temp_Spule = Spule(name, int(fluss_in), int(fluss_out), value)
                self.spulen.append(temp_Spule)
            elif element[0] == "V":
                name, fluss_in, fluss_out, value = element.split("-")
                temp_vs = V(name, int(fluss_in), int(fluss_out), value)
                self.vs.append(temp_vs)
            elif element[0] == "I":
                name, fluss_in, fluss_out, value = element.split("-")
                temp_erzeuger = Erzeuger(name, int(fluss_in), int(fluss_out), value)
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
        
        maxPotenzialNr = self.potenzialNumber
        masseknoten = 0
        #Transitoren
        self.inzidenz_c = [[0 for x in range(maxPotenzialNr)] for y in range(len(self.transitoren))]

        for i in range(len(self.transitoren)):
            transistor = self.transitoren[i]
            
            self.inzidenz_c[i][transistor.fluss_in] = 1
            self.inzidenz_c[i][transistor.fluss_out] = -1

        
        #Widerstaende
        self.inzidenz_g = [[0 for x in range(maxPotenzialNr)] for y in range(len(self.widerstaende))]

        print(self.widerstaende)
        for i in range(len(self.widerstaende)):
            widerstand = self.widerstaende[i]
            
            self.inzidenz_g[i][widerstand.fluss_in] = 1
            self.inzidenz_g[i][widerstand.fluss_out] = -1



        #Spulen
        self.inzidenz_l = [[0 for x in range(maxPotenzialNr)] for y in range(len(self.spulen))]
        for i in range(len(self.spulen)):
            spule = self.spulen[i]
            
            self.inzidenz_l[i][spule.fluss_in] = 1
            self.inzidenz_l[i][spule.fluss_out] = -1



        #Vs
        self.inzidenz_v = [[0 for x in range(maxPotenzialNr)] for y in range(len(self.vs))]

        for i in range(len(self.vs)):
            v = self.vs[i]
            
            self.inzidenz_v[i][v.fluss_in] = 1
            self.inzidenz_v[i][v.fluss_out] = -1


        self.inzidenz_i = [[0 for x in range(maxPotenzialNr)] for y in range(len(self.erzeuger))]

        for i in range(len(self.erzeuger)):
            erzeug = self.erzeuger[i]
            
            self.inzidenz_i[i][erzeug.fluss_in] = 1
            self.inzidenz_i[i][erzeug.fluss_out] = -1

        self.inzidenz_c = np.array(self.inzidenz_c)
        if(len(self.inzidenz_c) != 0):
            print(self.inzidenz_c)
            self.inzidenz_c = np.delete(self.inzidenz_c, masseknoten, 1).transpose()

        self.inzidenz_g = np.array(self.inzidenz_g)
        if(len(self.inzidenz_g) != 0):
            self.inzidenz_g = np.delete(self.inzidenz_g, masseknoten, 1).transpose()

        self.inzidenz_i = np.array(self.inzidenz_i)
        if(len(self.inzidenz_i) != 0):
            self.inzidenz_i = np.delete(self.inzidenz_i, masseknoten, 1).transpose()

        self.inzidenz_l = np.array(self.inzidenz_l)
        if(len(self.inzidenz_l) != 0):
            self.inzidenz_l = np.delete(self.inzidenz_l, masseknoten, 1).transpose()

        self.inzidenz_v = np.array(self.inzidenz_v)
        if(len(self.inzidenz_v) != 0):
            self.inzidenz_v = np.delete(self.inzidenz_v, masseknoten, 1).transpose()

        
        print("Transistoren")
        print(self.inzidenz_c)

        print("Widerstände")
        print(self.inzidenz_g)

        print("Spulen")
        print(self.inzidenz_l)

        print("V`s")
        print(self.inzidenz_v)

        print("Stromquellen")
        print(self.inzidenz_i)

    def getGr(self):
        return lambda x,t: [50, 50]

    def getV_t(self):
        return lambda t: [50, 50]





