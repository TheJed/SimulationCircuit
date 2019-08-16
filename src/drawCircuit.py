"""
    This module handels the drawing of the circuit
    :copyright: (c) 2019 by Tobias Klein.
"""

import matplotlib
matplotlib.use('Agg')
import os


import SchemDraw as schem
import SchemDraw.elements as e

import netlistHandler as netHandler

class CircuitDrawing():
    """Class for drawing the circuit"""

    def __init__(self,choosen):
        """Intialize the needed values for the drawing

        :param choosen: Choosed starting component (e.g. v-source or i-source)"""
        
        current_path = os.path.realpath(__file__)
        current_path = current_path.split("\\")
        pathToProgramm= current_path[:-2 or None]
        self.pathToRessources = ""
        for s in pathToProgramm:
            self.pathToRessources += s +"\\" 
        self.pathToRessources += "resources\\"

        self.fileLine = []

        self.potenzialList = []

        self.circuitDrawing = schem.Drawing()

        self.circuitDrawing.push()

        self.potenzialNummer = 1

        self.fromPotenzial = 0

        self.wasFullyConnectedBeforeUndo = []
        
        if choosen == 0:
            k = self.circuitDrawing.add(e.SOURCE_I, label="I1", d="left", reverse = True)
        else:
            k = self.circuitDrawing.add(e.SOURCE_V, label="V1", d="left", reverse = True)
        self.potenzialList.append(self.circuitDrawing.add(e.DOT, label = "E-Last", xy = k.end ))
        self.potenzialList.append(self.circuitDrawing.add(e.DOT, label = "E-Masse", xy = k.start))

    

    def addComponent(self, component, direction, name, eFromIndex, eToIndex):
        """This function adds a new component to the drawing

        :param component: Component type e.g. coil
        :param direction: Parameter which tells the drawing module in which direction the new component should face
        :param name: Name of new component
        :param eFromIndex: Potencial, where the power comes in the new component
        :param eToIndex: Potencial, where the power goes to
        :return: returns the label for the potencials
        :rtype: String"""

        eFrom = self.potenzialList[eFromIndex-1]
        eTo = self.potenzialList[eToIndex-1]

        sign = "?"

        if component == "Coil":
            componentType = e.INDUCTOR2
            sign = "L"
        if component == "Resistor":
            componentType = e.RBOX
            sign = "G"
        if component == "Capacitator":
            componentType = e.CAP
            sign = "C"
        if component == "V-Source":
            componentType = e.SOURCE_V
            sign = "V"
        if component == "I-Source":
            sign = "I"
            componentType = e.SOURCE_I

        elabel = ""
        nameForFile = ""
        if name == "":
            name = self.potenzialNummer - 1
        nameForFile = sign + str(name)
       
        if eFromIndex-1 >= 0 and eToIndex-1 >= 0:
            k = self.circuitDrawing.add(componentType, xy=eFrom.start, to=eTo.end)
            self.circuitDrawing.labelI(k, name)
            self.wasFullyConnectedBeforeUndo.append(True)
            self.fromPotenzial = eFromIndex-1
        elif eFromIndex-1 > 0 and eToIndex-1 < 0:
            k = self.circuitDrawing.add(componentType, d=direction, xy=eFrom.start)
            self.circuitDrawing.labelI(k, name)
            elabel = "E" + str(self.potenzialNummer)
            self.potenzialList.append(self.circuitDrawing.add(e.DOT, d=direction, label= elabel))
            
            self.potenzialNummer+=1

            self.fromPotenzial = eFromIndex - 1
            self.wasFullyConnectedBeforeUndo.append(False)

        else:
            k = self.circuitDrawing.add(componentType, d=direction, xy=self.circuitDrawing._elm_list[-1].end)
            self.circuitDrawing.labelI(k, name)
            elabel = "E" + str(self.potenzialNummer)
            self.potenzialList.append(self.circuitDrawing.add(e.DOT, d=direction, label= elabel))
            
            self.potenzialNummer+=1
            self.fromPotenzial = (self.potenzialNummer - 1)
            self.wasFullyConnectedBeforeUndo.append(False)

        self.circuitDrawing.draw()
        self.circuitDrawing.save(self.pathToRessources + "ergebnis.png")
        
        return elabel

    def undo(self):
        """Deletes the last added Component (and connected labels and potencials) from the drawing"""

        isPotenzialListeAndWasNozFullyConnectedBeforeUndo = False
    
        if(len(self.potenzialList) > 2):
            self.circuitDrawing._elm_list.pop()
            self.circuitDrawing._elm_list.pop()
    
            if not self.wasFullyConnectedBeforeUndo.pop():
                self.wasFullyConnectedBeforeUndo
                self.circuitDrawing._elm_list.pop()
                self.potenzialList.pop()
                self.potenzialNummer-=1
                isPotenzialListeAndWasNozFullyConnectedBeforeUndo = True
                
            
        self.draw() 
        return isPotenzialListeAndWasNozFullyConnectedBeforeUndo
          

    def draw(self):
        """Draws the new circuit and saves it to a file, so that the gui can load it"""
        self.circuitDrawing.draw()
        self.circuitDrawing.save(self.pathToRessources + "ergebnis.png")

