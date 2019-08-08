import matplotlib
matplotlib.use('Agg')

#from matplotlib import pyplot as plt

import SchemDraw as schem
import SchemDraw.elements as e

import netlistHandler as netHandler

class CircuitDrawing():
    def __init__(self):

        

        self.fileLine = []

        self.potenzialList = []

        self.circuitDrawing = schem.Drawing()

        self.circuitDrawing.push()

        self.potenzialNummer = 1

        self.fromPotenzial = 0

        self.wasFullyConnectedBeforeUndo = []
        
        
        i1 = self.circuitDrawing.add(e.SOURCE_I, label="I1", d="left", reverse = True)
        self.potenzialList.append(self.circuitDrawing.add(e.DOT, label = "E_Masse", xy = i1.end ))
        self.potenzialList.append(self.circuitDrawing.add(e.DOT, label = "E0", xy = i1.start))

        

        


    def addComponent(self, component, direction, name, eFromIndex, eToIndex):
        
        eFrom = self.potenzialList[eFromIndex-1]
        eTo = self.potenzialList[eToIndex-1]
        

        sign = "?"

        if component == "Spule":
            componentType = e.INDUCTOR2
            sign = "L"
        if component == "Widerstand":
            componentType = e.RBOX
            sign = "G"
        if component == "Kondensator":
            componentType = e.CAP
            sign = "C"
        if component == "Spannungsquelle":
            componentType = e.SOURCE_V
            sign = "V"
        if component == "Stromquelle":
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
            print("a")
        elif eFromIndex-1 > 0 and eToIndex-1 < 0:
            k = self.circuitDrawing.add(componentType, d=direction, xy=eFrom.start)
            self.circuitDrawing.labelI(k, name)
            elabel = "E" + str(self.potenzialNummer)
            self.potenzialList.append(self.circuitDrawing.add(e.DOT, d=direction, label= elabel))
            
            self.potenzialNummer+=1

            self.fromPotenzial = eFromIndex - 1
            self.wasFullyConnectedBeforeUndo.append(False)
            print("b")
        else:
            k = self.circuitDrawing.add(componentType, d=direction, xy=self.circuitDrawing._elm_list[-1].end)
            self.circuitDrawing.labelI(k, name)
            elabel = "E" + str(self.potenzialNummer)
            self.potenzialList.append(self.circuitDrawing.add(e.DOT, d=direction, label= elabel))
            
            self.potenzialNummer+=1
            self.fromPotenzial = (self.potenzialNummer - 1)
            self.wasFullyConnectedBeforeUndo.append(False)
            print("c")
        self.circuitDrawing.draw()
        self.circuitDrawing.save("ergebnis.png")
        
        return elabel

    def undo(self):

        isPotenzialListeAndWasNozFullyConnectedBeforeUndo = False
    
        if(len(self.potenzialList) > 2):
            self.circuitDrawing._elm_list.pop()
            self.circuitDrawing._elm_list.pop()
    
            if not self.wasFullyConnectedBeforeUndo.pop():
                self.wasFullyConnectedBeforeUndo
                self.circuitDrawing._elm_list.pop()
                self.potenzialList.pop()
                self.potenzialNummer-=1
                print("Pop")
                isPotenzialListeAndWasNozFullyConnectedBeforeUndo = True
                
            
        self.draw() 
        return isPotenzialListeAndWasNozFullyConnectedBeforeUndo
          

    def draw(self):
        self.circuitDrawing.draw()
        self.circuitDrawing.save("ergebnis.png")

