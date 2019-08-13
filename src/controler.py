import netlistHandler as nt
import drawCircuit as draw
import solver as solv
import os

class Controler:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        self.netHandler = nt.NetListHandler()
        self.circuitDrawing = draw.CircuitDrawing()
        self.circuitDrawing.draw()
        self.solutionData = []

        current_path = os.path.realpath(__file__)
        current_path = current_path.split("\\")
        pathToProgramm= current_path[:-2 or None]
        self.pathToRessources = ""
        for s in pathToProgramm:
            self.pathToRessources += s +"\\" 
        self.pathToRessources += "resources\\"

    def addComponent(self, component, direction, name, eFromIndex, eToIndex, value, function):
        elabel = self.circuitDrawing.addComponent(component, direction, name, eFromIndex, eToIndex)

        sign = "?"

        """if(eFromIndex ==1):
            eFromIndex = -10
        if(eToIndex == 1):
           
            eToIndex = -10"""

        if component == "Spule":
            sign = "L"
        elif component == "Widerstand":
            sign = "G"
        elif component == "Kondensator":
            sign = "C"
        elif component == "Spannungsquelle":
            sign = "V"
        elif component == "Stromquelle":
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
        if not any(name in s for s in self.netHandler.fileLines):
            self.netHandler.addPotencialLineToNetList(name, value)

    def undoAddComponent(self):
        self.netHandler.fileLines.pop()
        return self.circuitDrawing.undo()

    def drawCircuit(self):
        self.circuitDrawing.draw()

    def writeNetList(self):
        #TODO Startobjekt festlegen,nicht immer nur I1
        if not any("#I1" in s for s in self.netHandler.fileLines):
            self.netHandler.addLineToNetlist("I1", self.circuitDrawing.potenzialNummer, 0, 0.0, "i_constant")
        self.netHandler.writeFile(self.pathToRessources + "Schaltung.txt", self.circuitDrawing.potenzialNummer)

    def simulate(self):
        self.writeNetList()

       
        input_data = self.netHandler.readFile(self.pathToRessources + "Schaltung.txt")
        schaltung = nt.Schaltung(input_data)
        schaltung.initInzidenzMatritzen()


        solver = solv.Solver(schaltung)
        self.solutionData = solver.simulate()

    def getSolutionData(self):
        return self.solutionData

    
        

    