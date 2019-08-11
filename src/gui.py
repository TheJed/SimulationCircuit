import sys
from PyQt4 import QtGui
import pickle

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import FigureManagerQT as Fig
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import PyQt4.QtCore as QtCore
import pyqtgraph as pg
import math

import SchemDraw as schem
import SchemDraw.elements as e
import timedPopupMessage as timedMessage


import netlistHandler as netHandler

import controler as controler
import solver as solv


import random

if "win" in sys.platform:
    import ctypes
    myappid = 'tobias_klein.Rhein-Simulator' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class Window(QtGui.QApplication):
    EXIT_CODE_REBOOT = -666
    
    def __init__(self, sys_argv):
        regexp_onlyDoubles = QtCore.QRegExp('^([-+]?\d*\.\d+|\d+)$')
        self.validator = QtGui.QRegExpValidator(regexp_onlyDoubles)

        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', '#0F9BA8')
        
      
        #super(Window, self).__init__(parent)
        super(Window, self).__init__(sys_argv)

        

        #----------------------------Variablen----------------------------#  

        self.potenzialnummer = 2
        self.potenzialList = []
        self.currentPotenzial = 1
        self.wasFullyConnectedBeforeUndo = []
        self.controler = controler.Controler()

        #----------------------------Init Applikation----------------------------# 

        css = """


       
        QMessageBox QLabel {
            color: #0F9BA8;
            background-color:white;
            font-weight: bold;
            font-size: 15px;
        }
        

        QWidget#containerMain {
            background-color:#f9f9f9;
        }

        QWidget#containerInput  {
            background-color:#0F9BA8;
            border-radius: 30px;
        }

        QWidget#containerCircuit  {
            border: 3px solid grey;
            border-radius: 30px;
        }

        QWidget#containerGraph 
        {
            background-color:white;
        }
                
        QScrollArea#scrollGraph {
            background-color:white;
        }

        QScrollArea#scrollCircuit {
            background-color:white;
        }

        QPushButton:hover{
            background-color: #ff9933;
            border:5px solid #ff9933;
            color: white;
        }

        QPushButton {
            border:5px solid #f5f5f0;
            border-radius: 10px;
            background-color:#f5f5f0;
        }

        QLabel{
            padding-left: 5px;
            padding-right: 5px;
            background-color: #c9c9c9;
        
        }

        QComboBox {
            border: 5px solid #f5f5f0;
            border-radius: 10px;
            background-color: #f5f5f0;
        }

        QComboBox:hover{
            background-color: #ff9933;
            border:5px solid #ff9933;
            color: white;
        }               

        QComboBox:on{
            
            border: 5px solid grey;
            border-radius: 10px;
        }

        QListView{
            color:              black;
            background-color:   rgb(255, 255, 255);
            font-weight:        bold;
            selection-background-color: rgb(47, 175, 178);
            show-decoration-selected: 1;  
        }

        QWidget#containerGraph {
            border: 3px solid grey;
            border-radius: 10px;
        }

        QLabel#imageCircuit {
            background-color:#f9f9f9; 
            border: 0px;
        }

        QScrollArea#scrollCircuit {
            border:0px;
        }

        

        """ 
        
        screen_resolution = self.desktop().screenGeometry()
        width, height = screen_resolution.width(), screen_resolution.height()

        


        self.main_window = QtGui.QMainWindow()
        self.main_window.setWindowTitle('ECS - Electronical Circuit Simulator')
        self.main_window.showMaximized()

        app_icon = QtGui.QIcon()
        app_icon.addFile("../resources/favicon.ico")
        app_icon.addFile('../resources/favicon.ico', QtCore.QSize(16,16))
        app_icon.addFile('../resources/favicon.ico', QtCore.QSize(24,24))
        app_icon.addFile('../resources/favicon.ico', QtCore.QSize(32,32))
        app_icon.addFile('../resources/favicon.ico', QtCore.QSize(48,48))
        app_icon.addFile('../resources/favicon.ico', QtCore.QSize(256,256))
        self.setWindowIcon(QtGui.QIcon("../resources/favicon.ico"))
        self.main_window.setWindowIcon(app_icon)


        # set the layout
        containerMain = QtGui.QWidget()
        containerMain.setObjectName("containerMain")
        #containerMain.setStyleSheet("background-color:white;")
        
        #containerMain.setStyleSheet("QWidget#containerMain {background-color:#e0e0e0;}")
        containerMain.setStyleSheet(css)
        self.main_window.setStyleSheet(css)
        mainLayout = QtGui.QVBoxLayout(containerMain)
        


        containerGraph = QtGui.QWidget()
        #containerGraph.setStyleSheet("background-color:white ;")
        containerGraph.setObjectName("containerGraph")
        #containerMain.setStyleSheet("background-color:white;")
        containerGraph.setFixedWidth(width * 0.965)
        
        #containerGraph.setStyleSheet("QWidget#containerGraph {background-color:white;}")
        graphLayout = QtGui.QVBoxLayout(containerGraph)

        
        containerCircuit = QtGui.QWidget()
        #containerCircuit.setStyleSheet("background-color:SlateGrey ;")
        #width = int(self.width() * 4)
        #height = int(self.height() * 4)
        containerCircuit.setObjectName("containerCircuit")
        containerCircuit.setFixedWidth(width * 0.7)
        containerCircuit.setFixedHeight(height * 0.45)
     
        circuitLayout = QtGui.QVBoxLayout(containerCircuit)

        containerInput = QtGui.QWidget()
        #containerInput.setStyleSheet("background-color:white; border-radius:  3px 3px 6px;padding: 0px;")
        #containerInput.setStyleSheet("QWidget#containerInput {background-color:#0F9BA8 ;border-radius: 30px;}")
        containerInput.setObjectName("containerInput")
        
        containerInput.setFixedWidth(width * 0.25)
        containerInput.setFixedHeight(height * 0.45)
        inputLayout = QtGui.QVBoxLayout(containerInput)

        containerUpperLayout = QtGui.QWidget()
        #containerUpperLayout.setStyleSheet("background-color:white;")
        upperLayout = QtGui.QHBoxLayout(containerUpperLayout)

        containerLowerLayout = QtGui.QWidget()
        #containerLowerLayout.setStyleSheet("background-color:#e0e0e0 ;")
        lowerLayout = QtGui.QHBoxLayout(containerLowerLayout)
        

        #----------------------------Main-Menue------------------------------#

        self.statusbar = self.main_window.statusBar()
    

        mainMenu = self.main_window.menuBar()

        fileMenu = mainMenu.addMenu("&File")
        editMenu = mainMenu.addMenu("&Edit")

        createNewAction = QtGui.QAction("New", self.main_window)
        createNewAction.setShortcut("Ctrl+N")
        createNewAction.setStatusTip("Create a new Circuit")
        createNewAction.triggered.connect(self.createNewCircuit)

        exitAction = QtGui.QAction("Exit", self.main_window)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.setStatusTip("Leave the Applikation")
        exitAction.triggered.connect(self.closeApplication)

        saveAction = QtGui.QAction("Save", self.main_window)
        saveAction.setShortcut("Ctrl+S")
        saveAction.setStatusTip("Save the Applikation")   
        saveAction.triggered.connect(self.save)

        loadAction = QtGui.QAction("Load", self.main_window)
        loadAction.setShortcut("Ctrl+O")
        loadAction.setStatusTip("Load the Applikation")  
        loadAction.triggered.connect(self.load)

        undoAction = QtGui.QAction("Undo", self.main_window)
        undoAction.setShortcut("Ctrl+Z")
        undoAction.setStatusTip("Undo the last Action")  
        undoAction.triggered.connect(self.undo)
        

        fileMenu.addAction(createNewAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(loadAction)
        fileMenu.addAction(exitAction)
        editMenu.addAction(undoAction)
        mainMenu.setObjectName("mainMenu")
        mainMenu.setStyleSheet("#mainMenu{padding: 3px; border-bottom: 2px solid #0F9BA8; background-color:white}")
        
        #----------------------------Graph-Layout----------------------------#
        #Layout für die Anzeige des Graphen

        # a figure instance to plot on
        self.figure = Figure()
        self.figure.gca()
        #self.figure.set_size_inches(5,5)

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
               
        self.pgGraph = pg.PlotWidget()
        self.pgGraph.setObjectName("graph")


        font=QtGui.QFont()
        font.setPixelSize(16)
        plot = self.pgGraph.getPlotItem()
        plot.getAxis("bottom").tickFont = font
        plot.getAxis("bottom").setStyle(tickTextOffset = 20)
        plot.getAxis("left").tickFont = font
        plot.getAxis("left").setStyle(tickTextOffset = 20)
        self.state = self.pgGraph.saveState()
        # Just some button connected to `plot` method
        self.buttonPlotPotenzial = QtGui.QPushButton('Plot Potenzial')
        self.buttonPlotPotenzial.clicked.connect(self.plot2)
        self.buttonPlotPotenzial.setFixedSize(100,20)

        #graphLayout.addWidget(self.canvas)
        graphLayout.addWidget(self.buttonPlotPotenzial)
        graphLayout.addWidget(self.pgGraph)


        #----------------------------Circuit-Layout----------------------------#

        
        #self.circuitDrawing = Draw.CircuitDrawing()
        #self.circuitDrawing.draw()
        

        #with open('test.pkl', 'rb') as input:
        #    self.circuitDrawing = pickle.load(input)

        
            

        

        self.circuitFigure = Figure()
        self.circuitCanvas = FigureCanvas(self.circuitFigure)
        #self.drawCircuit()
        #self.circuitCanvas.resize(500,500)

        self.image = QtGui.QLabel()
        self.image.setGeometry(50, 40, 250, 250)
        self.pixmap = QtGui.QPixmap("../resources/ergebnis.png")
        self.image.setPixmap(self.pixmap)
        self.image.setObjectName("imageCircuit")
        #image.show()
        
        #self.updateGraph()
        
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidget(self.image)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollCircuit")
        


        #buttonDummy1 = QtGui.QPushButton('Add Element to Circuit')
        #buttonDummy2 = QtGui.QPushButton('Button')
        #buttonDummy1.clicked.connect(self.drawC)

        circuitLayout.setContentsMargins(20,20,20,20)
        circuitLayout.addWidget(self.scrollArea)
        #circuitLayout.addWidget(self.image)
        #circuitLayout.addWidget(buttonDummy1)
        #circuitLayout.addWidget(buttonDummy2)

        #----------------------------Input-Layout----------------------------#

        inputNameLayout = QtGui.QHBoxLayout()

        self.componentNameInputLabel = QtGui.QLabel("Name des Bauteils")
        
        self.componentNameInput = QtGui.QLineEdit()
        self.componentNameInput.setObjectName("")
        self.componentNameInput.setText("")

        inputNameLayout.addWidget(self.componentNameInputLabel)
        inputNameLayout.addWidget(self.componentNameInput)

        inputComponentLayout = QtGui.QHBoxLayout()

        self.componentDropwDown = QtGui.QComboBox()
        self.componentDropwDown.addItem("Widerstand")
        self.componentDropwDown.addItem("Spule")
        self.componentDropwDown.addItem("Kondensator")
        self.componentDropwDown.addItem("Spannungsquelle")
        self.componentDropwDown.addItem("Stromquelle")
        self.componentDropwDown.currentIndexChanged.connect(self.on_ComponentChanged)

        self.potenzialDropDownFrom = QtGui.QComboBox()
        self.potenzialDropDownFrom.addItem("---Ausgangspotenzial---")
        self.potenzialDropDownFrom.addItem("Masse")
        self.potenzialDropDownFrom.addItem("E0")
        self.potenzialDropDownFrom.setAutoCompletion(True)
        
        self.potenzialDropDownTo = QtGui.QComboBox()
        self.potenzialDropDownTo.addItem("---Eingangspotenzial---")
        self.potenzialDropDownTo.addItem("Masse")
        self.potenzialDropDownTo.addItem("E0")
        
        
        inputComponentLayout.addWidget(self.componentDropwDown)
        inputComponentLayout.addWidget(self.potenzialDropDownFrom)
        inputComponentLayout.addWidget(self.potenzialDropDownTo)


        inputComponentLayout2 = QtGui.QHBoxLayout()


        self.directionLabel = QtGui.QLabel("Richtung")

        self.directionDropwDown = QtGui.QComboBox()
        self.directionDropwDown.addItem("left")
        self.directionDropwDown.addItem("right")
        self.directionDropwDown.addItem("up")
        self.directionDropwDown.addItem("down")

        inputComponentLayout2.addWidget(self.directionLabel)
        inputComponentLayout2.addWidget(self.directionDropwDown)


        inputComponentLayout3 = QtGui.QHBoxLayout()

        self.componentValueLabel = QtGui.QLabel("Start-Value of Component")
        self.componentValueLabel.hide()

        self.componentValueInput = QtGui.QLineEdit()
        self.componentValueInput.setObjectName("")
        self.componentValueInput.setText("0.0")
        self.componentValueInput.hide()
        self.componentValueInput.setValidator(self.validator)
        self.componentValueInput.textEdited.connect(self.on_valueInputChanged)

        self.componentValueDropDown = QtGui.QComboBox()
        
        self.componentValueDropDown.currentIndexChanged.connect(self.on_valueDropDownChanged)
        
        self.componentValueDropDown.addItem("Funktionsauswahl")
        self.componentValueDropDown.addItem("Dummy-Funktion")

        inputComponentLayout3.addWidget(self.componentValueLabel)
        inputComponentLayout3.addWidget(self.componentValueInput)
        inputComponentLayout3.addWidget(self.componentValueDropDown)

        buttonAddComponent = QtGui.QPushButton('Add Component')
        #buttonDummy3.setFixedSize(50,50)
        buttonAddComponent.clicked.connect(self.addComponentToCircuit)
        buttonUndo = QtGui.QPushButton('Simulate')
        buttonUndo.clicked.connect(self.enterPotencialValues)
        #buttonUndo.setFixedSize(50,50)

        inputLayout.addLayout(inputNameLayout)
        inputLayout.addLayout(inputComponentLayout)
        inputLayout.addLayout(inputComponentLayout2)
        inputLayout.addLayout(inputComponentLayout3)
        #inputLayout.addWidget(self.componentNameInput)
        #inputLayout.addWidget(self.componentDropwDown)
        #inputLayout.addWidget(self.directionDropwDown)
        inputLayout.addWidget(buttonAddComponent)
        inputLayout.addWidget(buttonUndo)

        inputLayout.setContentsMargins(50,50,50,50)

        #----------------------------Main-Layout----------------------------# 

        upperLayout.addWidget(containerInput)
        upperLayout.addWidget(containerCircuit)
        
        

        lowerLayout.addWidget(containerGraph)

        mainLayout.addWidget(containerUpperLayout)
        mainLayout.addWidget(containerLowerLayout)       

        self.main_window.setCentralWidget(containerMain)
        #self.setLayout(mainLayout)
        #self.setGeometry(50, 50, 1000, 700)
        
        #self.setWindowTitle('Rhein-Simulator')

    def createNewCircuit(self):
        
        #QtGui.qApp.exit(self.EXIT_CODE_REBOOT)
        initParametersDialog = QtGui.QDialog()


        layout = QtGui.QFormLayout()
        
		
        le = QtGui.QLineEdit()
        layout.addRow(le)
        btn1 = QtGui.QPushButton("get name")
		
        le1 = QtGui.QLineEdit()
        layout.addRow(btn1,le1)
        btn2 = QtGui.QPushButton("Enter an integer")
        
		
        le2 = QtGui.QLineEdit()
        layout.addRow(btn2,le2)
        initParametersDialog.setLayout(layout)
        initParametersDialog.setWindowTitle("Input Dialog demo")


        initParametersDialog.exec()
        self.load(True) 
        print()

    def save(self):

        objectsToSave = [self.controler, [self.potenzialDropDownFrom.itemText(i) for i in range(self.potenzialDropDownFrom.count())],  [self.potenzialDropDownTo.itemText(i) for i in range(self.potenzialDropDownTo.count())]]
        pathFileName = QtGui.QFileDialog.getSaveFileName(None, 'Load ECS-Project', '../saved-circuits', 'pickle(*.pickle)')
 

        with open(pathFileName, 'wb') as handle:
            pickle.dump(objectsToSave, handle, protocol=pickle.HIGHEST_PROTOCOL)

        messagebox = timedMessage.TimerMessageBox("Information", "File successfully saved",3, self.main_window)
        messagebox.exec_()

        self.statusbar.showMessage("File successfully saved", 5000)
        #message = QtGui.QMessageBox()
        #message.setIcon(QtGui.QMessageBox.Information)

        #message.setText("This is a message box")
        #message.setInformativeText("This is additional information")
        #message.setWindowTitle("MessageBox demo")
        #message.setDetailedText("The details are as follows:")
        #message.setStandardButtons(QtGui.QMessageBox.Ok)

        

    def load(self, isNew=False):


        if not isNew:
            pathFileName = QtGui.QFileDialog.getOpenFileName(None, 'Load ECS-Project', '../saved-circuits', 'pickle(*.pickle)') 
            
        else: 
            pathFileName = "Standard.pickle"

        with open(pathFileName, 'rb') as handle:
                loadedObjects = pickle.load(handle)

        
        if not isNew:
            #message = QtGui.QMessageBox.information(self.main_window, "Information", "File successfully loaded", QtGui.QMessageBox.Ok)


            messagebox = timedMessage.TimerMessageBox("Informaion", "File successfully loaded",2, self.main_window)
            messagebox.exec_()

        self.statusbar.showMessage("File successfully loaded", 5000)
        
        self.controler = loadedObjects[0]
        self.controler.drawCircuit()
        self.updateGraph()

        #count = self.potenzialDropDownFrom.count()
        #for i in range(-1,count+1):
        #    print("hi")
        #    self.potenzialDropDownFrom.removeItem(i)
        #    self.potenzialDropDownTo.removeItem(i)
        self.potenzialDropDownFrom.clear()
        self.potenzialDropDownTo.clear()

        self.potenzialDropDownFrom.addItems(loadedObjects[1])
        self.potenzialDropDownTo.addItems(loadedObjects[2])

    def closeApplication(self):
        self.quit()
        
    def undo(self):

        haveToRemove = self.controler.undoAddComponent()
        

        if haveToRemove:

            self.potenzialDropDownFrom.removeItem(self.potenzialDropDownFrom.count()-1)
            self.potenzialDropDownTo.removeItem(self.potenzialDropDownTo.count()-1)

        self.updateGraph()
    

    def on_valueInputChanged(self):
        self.componentValueDropDown.setCurrentIndex(0)

    def on_valueDropDownChanged(self):
        self.componentValueInput.setText("")

    def on_ComponentChanged(self):
        if self.componentDropwDown.currentText() == "Spule":
            self.componentValueInput.setText("0.0")
            self.componentValueInput.show()
            self.componentValueLabel.show()
        else:
            self.componentValueInput.hide()
            self.componentValueLabel.hide()

    def addComponentToCircuit(self):
        component = (str(self.componentDropwDown.currentText()))
        direction = (str(self.directionDropwDown.currentText()))
        name = (str(self.componentNameInput.text()))
        
        print(self.potenzialDropDownTo.itemText(self.potenzialDropDownTo.currentIndex()))
        print(self.potenzialDropDownTo.currentIndex())
        elabel = self.controler.addComponent(component, direction, name, self.potenzialDropDownFrom.currentIndex(), self.potenzialDropDownTo.currentIndex(), self.componentValueInput.text())


        if len(elabel) > 0:
            self.potenzialDropDownFrom.addItem(elabel)
            self.potenzialDropDownTo.addItem(elabel)


        self.potenzialDropDownFrom.setCurrentIndex(0)
        self.potenzialDropDownTo.setCurrentIndex(0)
        self.componentValueInput.setText("0.0")
        self.componentValueInput.hide()
        self.componentValueLabel.hide()


        self.updateGraph()

        

        

    def updateGraph(self):
        
        self.pixmap = QtGui.QPixmap("ergebnis.png")
        self.image.setPixmap(self.pixmap)

    def simulate(self):

        for x in range(len(self.list_potencialInputs)):
            self.controler.addPotencialValue("E" + str(x), self.list_potencialInputs[x].text())


        self.potenzialParameters.close()
        self.controler.simulate()
        



        qt = QtGui.QMessageBox()
        qt.setIcon(QtGui.QMessageBox.Critical)
        qt.setWindowTitle("An Error has occured")
        qt.setText("Noch nicht fertig implementiert")
        qt.exec()

    def enterPotencialValues(self):   
        #regexp_onlyDoubles = QtCore.QRegExp('^([01]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])$')
        
        
        self.potenzialParameters = QtGui.QDialog()

        layout = QtGui.QFormLayout()

        label_infoPotencial = QtGui.QLabel("Please insert start-value (float) for the potencials")
        self.list_potencialInputs = []

        for potencial in range(len(self.potenzialDropDownFrom)-2):
            inputPotencialLayout = QtGui.QHBoxLayout()

            potencialValueLabel = QtGui.QLabel("Value of Potencial:" + str(potencial))
            
            potencialValueInput = QtGui.QLineEdit()
            potencialValueInput.setObjectName("")
            potencialValueInput.setText("0.0")
            potencialValueInput.setValidator(self.validator)
            inputPotencialLayout.addWidget(potencialValueLabel)
            inputPotencialLayout.addWidget(potencialValueInput)
            layout.addRow(inputPotencialLayout)
            self.list_potencialInputs.append(potencialValueInput)

        button_startSimulation = QtGui.QPushButton("Start Simulation")
        button_startSimulation.clicked.connect(self.simulate)
        layout.addRow(button_startSimulation)
        #le = QtGui.QLineEdit()
        #layout.addRow(le)
        #btn1 = QtGui.QPushButton("get name")
		
        #le1 = QtGui.QLineEdit()
        #layout.addRow(btn1,le1)
        #btn2 = QtGui.QPushButton("Enter an integer")
        
		
        #le2 = QtGui.QLineEdit()
        #layout.addRow(btn2,le2)
        self.potenzialParameters.setLayout(layout)
        self.potenzialParameters.setWindowTitle("Potencial Values")


        self.potenzialParameters.exec()
        #self.load(True) 
        print()






    def plot(self):

        ''' plot some random stuff '''
        # random data
        data = [random.random() for i in range(10)]

        # create an axis
        ax = self.figure.axes[0]
        
        # discards the old graph
        ax.clear()
        

        # plot data
        ax.plot(data, '*-')
        # refresh canvas
        #self.figure.set_figheight(self.figure.get_figheight()*1.25)
        self.canvas.draw()
     
        
    def plot2(self):
        self.pgGraph.restoreState(self.state)
        data = [random.random() for i in range(10)]
        plotItem = self.pgGraph.getPlotItem()
        plotItem.clear()
        
        plotItem.plot(data, pen = pg.mkPen('#0F9BA8', width=3, style=QtCore.Qt.SolidLine) )
        

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    main = Window(sys.argv)
    #main.showMaximized()

    sys.exit(app.exec_())

    #currentExitCode = Window.EXIT_CODE_REBOOT
    #while currentExitCode == Window.EXIT_CODE_REBOOT:
    #    a = QtGui.QApplication(sys.argv)
    #    w = Window(sys.argv)
        #w.show()
    #    currentExitCode = a.exec_()
    #    a = None
    #    a = QtGui.QApplication(sys.argv)
    #    w = None