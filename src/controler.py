"""
    This module handels the communication between the GUI and the backend
    :copyright: (c) 2019 by Tobias Klein.
"""

import netlistHandler as nt
import drawCircuit as draw
import solver as solv
import os

class Controler:
    """The controler handels the communication between the backend and the frontend"""

    def __init__(self, *args, **kwargs):
        """Initialize the starting values"""
        super().__init__(*args, **kwargs)


        self.netHandler = nt.NetListHandler()
        self.solutionData = []

        """current_path = os.path.realpath(__file__)
        current_path = current_path.split("\\")
        pathToProgramm= current_path[:-2 or None]
        self.pathToRessources = ""
        for s in pathToProgramm:
            self.pathToRessources += s +"\\" 
        self.pathToRessources += "resources\\"""
        self.pathToRessources = "../resources"


    def createCircuit(self, choosen, function):
        """This function calls the Drawing module to draw a new circuit"""

        self.choosen = choosen
        self.startFunction = function
        self.circuitDrawing = draw.CircuitDrawing(choosen)
        self.circuitDrawing.draw()

    def setTValues(self, t, t_steps):
        """This function sets parameters for the simulation"""
        self.t = t
        self.t_steps = t_steps

    def addComponent(self, component, direction, name, eFromIndex, eToIndex, value, function):
        """This function calls the Drawing module to add a new component and saves the new component in the netlist

        :param component: Component type e.g. coil
        :param direction: Parameter which tells the drawing module in which direction the new component should face
        :param name: Name of new component
        :param eFromIndex: Potencial, where the power comes in the new component
        :param eToIndex: Potencial, where the power goes to
        :param value: Starting value of component (currently only for coils)
        :param function: Behavior of component
        """

        elabel = self.circuitDrawing.addComponent(component, direction, name, eFromIndex, eToIndex)

        sign = "?"

        if component == "Coil":
            sign = "L"
        elif component == "Resistor":
            sign = "G"
        elif component == "Capacitator":
            sign = "C"
        elif component == "V-Source":
            sign = "V"
        elif component == "I-Source":
            sign = "I"

        if name == "":
            name = self.circuitDrawing.potenzialNummer -1
        nameForFile = sign + str(name)

        
        eFromIndex = self.circuitDrawing.fromPotenzial - 1
        
        if(eToIndex != 1):
            eToIndex = self.circuitDrawing.potenzialNummer -1
        else:
            eToIndex = self.circuitDrawing.potenzialNummer


        self.netHandler.addLineToNetlist(nameForFile, eFromIndex, eToIndex, value, function)
        return elabel

    def addPotencialValue(self, name, value):
        """Adds a new Potencil dot to the Drawing"""
        if not any(name in s for s in self.netHandler.fileLines):
            self.netHandler.addPotencialLineToNetList(name, value)

    def undoAddComponent(self):
        """Deletes the last added Component from the drawing and from the netlist"""
        self.netHandler.fileLines.pop()
        return self.circuitDrawing.undo()

    def drawCircuit(self):
        """Tells the drawing to draw the circuit"""
        self.circuitDrawing.draw()

    def writeNetList(self, filename):
        """Adds the last information to the netlist and calls the nethandler to write the file"""

        if self.choosen == 0:
            if not any("#I1" in s for s in self.netHandler.fileLines):
                self.netHandler.addLineToNetlist("I1", self.circuitDrawing.potenzialNummer, 0, 0.0, self.startFunction)
        elif self.choosen == 1:
            if not any("#V1" in s for s in self.netHandler.fileLines):
                self.netHandler.addLineToNetlist("V1", self.circuitDrawing.potenzialNummer, 0, 0.0, self.startFunction)
        self.netHandler.writeFile(self.pathToRessources + filename)

    def simulate(self, filename):
        """Start the simulation by calling the solver"""
        
       
        input_data = self.netHandler.readFile(self.pathToRessources + filename)
        schaltung = nt.Schaltung(input_data)
        schaltung.initInzidenzMatritzen()

        solver = solv.Solver(schaltung)
        self.solutionData = solver.simulate(self.t, self.t_steps)

    def getSolutionData(self):
        """Returns the solutionData
        
        :return: Simulated Values
        :rtype: list"""
        return self.solutionData

    
        

    