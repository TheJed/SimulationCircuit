"""
    This module creates and handels the GUI for the simulation
    :copyright: (c) 2019 by Tobias Klein.
"""

from PyQt4 import QtGui
import PyQt4.QtCore as QtCore

import sys
import pickle
import math
import inspect
import random
import os

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import FigureManagerQT as Fig
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import SchemDraw as schem
import SchemDraw.elements as e

import timedPopupMessage as timedMessage
import netlistHandler as netHandler
import controler as controler
import solver as solv
import functionLib


if "win" in sys.platform:
    import ctypes
    myappid = 'tobias_klein.Rhein-Simulator' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class Window(QtGui.QApplication):
    """This class holds/is the main windows of the GUI"""

    EXIT_CODE_REBOOT = -666
    
    def __init__(self, sys_argv):
        """Inits/ Builds the GUI"""
        super(Window, self).__init__(sys_argv)

        #----------------------------Setting path to resources folder----------------------------#
        current_path = os.path.realpath(__file__)
        current_path = current_path.split("\\")
        pathToProgramm= current_path[:-2 or None]
        self.path = ""
        for s in pathToProgramm:
            self.path += s +"\\" 
        
        #----------------------------Validator for float inputs----------------------------#
        regexp_onlyDoubles = QtCore.QRegExp('^([-+]?\d*\.\d+|\d+)$')
        self.validator = QtGui.QRegExpValidator(regexp_onlyDoubles)


        #----------------------------Variablen----------------------------#  

        self.potenzialnummer = 2
        self.potenzialList = []
        self.currentPotenzial = 1
        self.wasFullyConnectedBeforeUndo = []
        self.potencial = 0
        
        self.controler = controler.Controler()

        #----------------------------Init Main Window----------------------------# 

        cssFile = self.path + "\\resources\\css-gui.txt"
        css = ""
        with open(cssFile,"r") as fh:
            css += (fh.read())

       
        screen_resolution = self.desktop().screenGeometry()
        width, height = screen_resolution.width(), screen_resolution.height()


        self.main_window = QtGui.QMainWindow()
        self.main_window.setWindowTitle('ECS - Electronical Circuit Simulator')
        self.main_window.showMaximized()

        #Set Icon
        self.setAppIcon()

        # set the layout
        containerMain = QtGui.QWidget()
        containerMain.setObjectName("containerMain")
       
        containerMain.setStyleSheet(css)
        self.main_window.setStyleSheet(css)
        mainLayout = QtGui.QVBoxLayout(containerMain)
        
        containerGraph = QtGui.QWidget()
        containerGraph.setObjectName("containerGraph")
        containerGraph.setFixedWidth(width * 0.965)
        
        graphLayout = QtGui.QVBoxLayout(containerGraph)

        containerCircuit = QtGui.QWidget()

        containerCircuit.setObjectName("containerCircuit")
        containerCircuit.setFixedWidth(width * 0.7)
        containerCircuit.setFixedHeight(height * 0.4)
     
        circuitLayout = QtGui.QVBoxLayout(containerCircuit)

        containerInput = QtGui.QWidget()
        containerInput.setObjectName("containerInput")
        
        containerInput.setFixedWidth(width * 0.25)
        containerInput.setFixedHeight(height * 0.4)
        inputLayout = QtGui.QVBoxLayout(containerInput)

        containerUpperLayout = QtGui.QWidget()
        upperLayout = QtGui.QHBoxLayout(containerUpperLayout)

        containerLowerLayout = QtGui.QWidget()
        lowerLayout = QtGui.QHBoxLayout(containerLowerLayout)
        containerLowerLayout.setFixedHeight(height * 0.4)
        

        #----------------------------Main-Menue------------------------------#

        self.setMenu()
        self.createDropDowns()
        #----------------------------Graph-Layout----------------------------#
       
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        self.toolbar = NavigationToolbar(self.canvas, containerGraph) 
        
        self.buttonPlotPotenzial = QtGui.QPushButton('Plot First Potenzial ')
        self.buttonPlotPotenzial.clicked.connect(self.plot2)
        self.buttonPlotPotenzial.hide()
        self.buttonPlotPotenzial.setFixedSize(120,20)

        graphInputLayout = QtGui.QHBoxLayout()
        graphInputLayout.addWidget(self.potenzialDropDown)
        graphInputLayout.addWidget(self.buttonPlotPotenzial)

        graphInputWidget = QtGui.QWidget()
        graphInputWidget.setLayout(graphInputLayout)
        graphInputWidget.setFixedSize(350,30)
        
        graphLayout.addWidget(self.toolbar)
        graphLayout.addWidget(graphInputWidget)
        graphLayout.addWidget(self.canvas)

        #----------------------------Circuit-Layout----------------------------#

        self.createCircuitFigure()
        circuitLayout.setContentsMargins(20,20,20,20)
        circuitLayout.addWidget(self.scrollArea)

        #----------------------------Input-Layout----------------------------#

        inputNameLayout = QtGui.QHBoxLayout()
        
        self.createFunctionDropwDowns()

        self.componentNameInputLabel = QtGui.QLabel("Name des Bauteils")

        self.componentNameInput = QtGui.QLineEdit()
        self.componentNameInput.setObjectName("")
        self.componentNameInput.setText("")

        inputNameLayout.addWidget(self.componentNameInputLabel)
        inputNameLayout.addWidget(self.componentNameInput)

        inputComponentLayout = QtGui.QHBoxLayout()
        inputComponentLayout.addWidget(self.componentDropwDown)
        inputComponentLayout.addWidget(self.potenzialDropDownFrom)
        inputComponentLayout.addWidget(self.potenzialDropDownTo)

        inputComponentLayout2 = QtGui.QHBoxLayout()

        self.directionLabel = QtGui.QLabel("Direction")
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
        #self.componentValueInput.textEdited.connect(self.on_valueInputChanged)

        inputComponentLayout3.addWidget(self.componentValueLabel)
        inputComponentLayout3.addWidget(self.componentValueInput)
        inputComponentLayout3.addWidget(self.function_c_DropwDown)
        inputComponentLayout3.addWidget(self.function_i_DropwDown)
        inputComponentLayout3.addWidget(self.function_r_DropwDown)
        inputComponentLayout3.addWidget(self.function_v_DropwDown)
        inputComponentLayout3.addWidget(self.function_l_DropwDown)

        buttonAddComponent = QtGui.QPushButton('Add Component')
        buttonAddComponent.clicked.connect(self.addComponentToCircuit)
        buttonUndo = QtGui.QPushButton('Simulate')
        buttonUndo.clicked.connect(self.enterPotencialValues)

        inputLayout.addLayout(inputNameLayout)
        inputLayout.addLayout(inputComponentLayout)
        inputLayout.addLayout(inputComponentLayout2)
        inputLayout.addLayout(inputComponentLayout3)

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

        self.createNewCircuit()


    def setAppIcon(self):
        """This function loads and sets the application icon"""

        app_icon = QtGui.QIcon()
        app_icon.addFile(self.path + "\\resources\\favicon.ico")
        app_icon.addFile(self.path + "\\resources\\favicon.ico", QtCore.QSize(16,16))
        app_icon.addFile(self.path + "\\resources\\favicon.ico", QtCore.QSize(24,24))
        app_icon.addFile(self.path + "\\resources\\favicon.ico", QtCore.QSize(32,32))
        app_icon.addFile(self.path + "\\resources\\favicon.ico", QtCore.QSize(48,48))
        app_icon.addFile(self.path + "\\resources\\favicon.ico", QtCore.QSize(256,256))
        self.setWindowIcon(QtGui.QIcon(self.path + "\\resources\\favicon.ico"))
        self.main_window.setWindowIcon(app_icon)

    def setMenu(self):
        """This function create the Window-Menue"""

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
        
    def createFunctionDropwDowns(self):
        """This function creates the Drop-Downs for Function selection based ond the funcitonLib"""

        all_functions = inspect.getmembers(functionLib, inspect.isfunction) 

        self.c_functions = []
        self.i_functions = []
        self.r_functions = []
        self.v_functions = []
        self.l_functions = []

        for functionTupel in all_functions:
            if "c_" in functionTupel[0]:
                self.c_functions.append(functionTupel)

            elif "i_" in functionTupel[0]:
                self.i_functions.append(functionTupel)
            elif "r_" in functionTupel[0]:
                self.r_functions.append(functionTupel)
            elif "v_" in functionTupel[0]:
                self.v_functions.append(functionTupel)
            elif "l_" in functionTupel[0]:
                self.l_functions.append(functionTupel)

       
        self.function_c_DropwDown = QtGui.QComboBox()
        self.function_c_DropwDown.addItem("Choose Function")
        self.function_i_DropwDown = QtGui.QComboBox()
        self.function_i_DropwDownNew = QtGui.QComboBox()
        self.function_i_DropwDown.addItem("Choose Function")
        self.function_i_DropwDownNew.addItem("Choose Function")
        self.function_r_DropwDown = QtGui.QComboBox()
        self.function_r_DropwDown.addItem("Choose Function")
        self.function_v_DropwDown = QtGui.QComboBox()
        self.function_v_DropwDownNew = QtGui.QComboBox()
        self.function_v_DropwDown.addItem("Choose Function")
        self.function_v_DropwDownNew.addItem("Choose Function")
        self.function_l_DropwDown = QtGui.QComboBox()
        self.function_l_DropwDown.addItem("Choose Function")

        for functionTupel in self.c_functions:
            self.function_c_DropwDown.addItem(functionTupel[0])

        for functionTupel in self.i_functions:
            self.function_i_DropwDown.addItem(functionTupel[0])
            self.function_i_DropwDownNew.addItem(functionTupel[0])

        for functionTupel in self.r_functions:
            self.function_r_DropwDown.addItem(functionTupel[0])
        
        for functionTupel in self.v_functions:
            self.function_v_DropwDown.addItem(functionTupel[0])
            self.function_v_DropwDownNew.addItem(functionTupel[0])

        for functionTupel in self.l_functions:
            self.function_l_DropwDown.addItem(functionTupel[0])

        self.function_c_DropwDown.hide()
        self.function_i_DropwDown.hide()
        self.function_r_DropwDown.hide()
        self.function_v_DropwDown.hide()
        self.function_l_DropwDown.hide()
        
    def createCircuitFigure(self):
        """This function creates the visiual representation of the circuit"""

        self.circuitFigure = Figure()
        self.circuitCanvas = FigureCanvas(self.circuitFigure)


        self.image = QtGui.QLabel()
        self.image.setGeometry(50, 40, 250, 250)

        self.image.setObjectName("imageCircuit")
    
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidget(self.image)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollCircuit")

    def createDropDowns(self):
        """This function creates multile Drop-Downs for the GUI. Mostly used for the input of components"""

        self.componentDropwDown = QtGui.QComboBox()
        self.componentDropwDown.addItem("Resistor")
        self.componentDropwDown.addItem("Coil")
        self.componentDropwDown.addItem("Capacitator")
        self.componentDropwDown.addItem("V-Source")
        self.componentDropwDown.addItem("I-Source")
        self.componentDropwDown.currentIndexChanged.connect(self.on_ComponentChanged)

        self.potenzialDropDownFrom = QtGui.QComboBox()
        self.potenzialDropDownFrom.addItem("---Potencial From---")
        self.potenzialDropDownFrom.addItem("E-Last")
        self.potenzialDropDownFrom.addItem("E-Masse")
        self.potenzialDropDownFrom.setAutoCompletion(True)
        
        self.potenzialDropDownTo = QtGui.QComboBox()
        self.potenzialDropDownTo.addItem("---Potencial To---")
        self.potenzialDropDownTo.addItem("E-Last")
        self.potenzialDropDownTo.addItem("E-Masse")
        self.potenzialDropDownFrom.setAutoCompletion(True)

        self.directionDropwDown = QtGui.QComboBox()
        self.directionDropwDown.addItem("left")
        self.directionDropwDown.addItem("right")
        self.directionDropwDown.addItem("up")
        self.directionDropwDown.addItem("down")

        self.potenzialDropDown = QtGui.QComboBox()
        self.potenzialDropDown.setFixedSize(200,20)
        self.potenzialDropDown.hide()
        self.potenzialDropDown.currentIndexChanged.connect(self.onPotencialChanged)

    def onPotencialChanged(self):
        """Sets the choosen potencial for plotting graph when Potencial-Drop-Down changed"""
        self.potencial = self.potenzialDropDown.currentIndex()

    def createNewCircuit(self):
        """This function handels the initial creating dialog for creating a new circuit"""

        all_functions = inspect.getmembers(functionLib, inspect.isfunction)   
        print(all_functions)
       
        self.i_functions = []
        self.v_functions = []

        for functionTupel in all_functions:
            
            if "i_" in functionTupel[0]:
                self.i_functions.append(functionTupel)
           
            elif "v_" in functionTupel[0]:
                self.v_functions.append(functionTupel)


        self.function_i_DropwDownNew = QtGui.QComboBox()
        self.function_i_DropwDownNew.addItem("Choose Function")
        self.function_v_DropwDownNew = QtGui.QComboBox()
        self.function_v_DropwDownNew.addItem("Choose Function")
        
       
        for functionTupel in self.i_functions:
            self.function_i_DropwDownNew.addItem(functionTupel[0])

       
        for functionTupel in self.v_functions:
            self.function_v_DropwDownNew.addItem(functionTupel[0])

        self.function_v_DropwDownNew.hide()
        self.function_i_DropwDownNew.show()
        self.initParametersDialog = QtGui.QDialog()


        layout = QtGui.QFormLayout()
        
        startLabel = QtGui.QLabel("Choose a start Circuit")
        
        self.choosen = 0
        
        self.beginningCircuit = QtGui.QComboBox()
        self.beginningCircuit.addItem("Start with a I-Source")
        self.beginningCircuit.addItem("Start with a V-Source")
        self.beginningCircuit.currentIndexChanged.connect(self.onNewDropChanged)

        okButton = QtGui.QPushButton("Create New Circuit")
        okButton.clicked.connect(self.setStartingValues)

        layout.addRow(startLabel,self.beginningCircuit)
        layout.addWidget(self.function_v_DropwDownNew)
        layout.addWidget(self.function_i_DropwDownNew)
        layout.addRow(okButton)
        self.initParametersDialog.setLayout(layout)
        self.initParametersDialog.setWindowTitle("Create a new Circuit")
        
        self.initParametersDialog.exec()

        self.controler = controler.Controler()
        self.controler.createCircuit(self.choosen, self.function)

        self.potenzialDropDownFrom.clear()
        self.potenzialDropDownFrom.addItem("---Ausgangspotenzial---")
        self.potenzialDropDownFrom.addItem("E-Last")
        self.potenzialDropDownFrom.addItem("E-Masse")

        self.potenzialDropDownTo.clear()
        self.potenzialDropDownTo.addItem("---Eingangspotenzial---")
        self.potenzialDropDownTo.addItem("E-Last")
        self.potenzialDropDownTo.addItem("E-Masse")

        self.updateGraph()

    def setStartingValues(self):
        """Sets function when function-drop-downs changed. It has influence on the function for the starting element"""
        if self.choosen == 0:
            self.function = self.function_i_DropwDownNew.currentText()
        else:
            self.function = self.function_v_DropwDownNew.currentText()
        self.initParametersDialog.close()
        
    def onNewDropChanged(self):
        """Sets choosen when beginningCircuit - drop-down changed. It determins if the starting element is a voltage or a power-source"""
        self.choosen = self.beginningCircuit.currentIndex()
        if self.choosen == 1:
            self.function_v_DropwDownNew.show()
            self.function_i_DropwDownNew.hide()
            
        else:
            self.function_i_DropwDownNew.show()
            self.function_v_DropwDownNew.hide()

    def save(self):
        """Saves the current project / current simulation without the simulation data"""

        objectsToSave = [self.controler, [self.potenzialDropDownFrom.itemText(i) for i in range(self.potenzialDropDownFrom.count())],  [self.potenzialDropDownTo.itemText(i) for i in range(self.potenzialDropDownTo.count())]]
        pathFileName = QtGui.QFileDialog.getSaveFileName(None, 'Load ECS-Project', self.path + '\\saved-circuits', 'pickle(*.pickle)')
 
        with open(pathFileName, 'wb') as handle:
            pickle.dump(objectsToSave, handle, protocol=pickle.HIGHEST_PROTOCOL)

        messagebox = timedMessage.TimerMessageBox("Information", "File successfully saved",3, self.main_window)
        messagebox.exec_()

        self.statusbar.showMessage("File successfully saved", 5000)
 
    def load(self):
        """This function handels the loading of a circuit"""
        
        self.potenzialDropDown.hide()
        self.buttonPlotPotenzial.hide()

        pathFileName = QtGui.QFileDialog.getOpenFileName(None, 'Load ECS-Project', self.path + '\\saved-circuits', 'pickle(*.pickle)')
        with open(pathFileName, 'rb') as handle:
            loadedObjects = pickle.load(handle)

        messagebox = timedMessage.TimerMessageBox("Informaion", "File successfully loaded",2, self.main_window)
        messagebox.exec_()

        self.statusbar.showMessage("File successfully loaded", 5000)
    
        self.controler = loadedObjects[0]
        self.controler.drawCircuit()
        self.updateGraph()
        self.potenzialDropDownFrom.clear()
        self.potenzialDropDownTo.clear()

        self.potenzialDropDownFrom.addItems(loadedObjects[1])
        self.potenzialDropDownTo.addItems(loadedObjects[2])

    def closeApplication(self):
        """Closes the GUI"""
        self.quit()
        
    def undo(self):
        """Undo the last modification to the circuit"""

        haveToRemove = self.controler.undoAddComponent()
        
        if haveToRemove:

            self.potenzialDropDownFrom.removeItem(self.potenzialDropDownFrom.count()-1)
            self.potenzialDropDownTo.removeItem(self.potenzialDropDownTo.count()-1)

        self.updateGraph()
    
    """def on_valueInputChanged(self):
        self.componentValueDropDown.setCurrentIndex(0)"""

    def on_valueDropDownChanged(self):
        """Resets the written component value"""
        self.componentValueInput.setText("")

    def on_ComponentChanged(self):
        """Makes certain input-field visible and hide others if the user selectets a different component"""

        self.function_c_DropwDown.hide()
        self.function_i_DropwDown.hide()
        self.function_r_DropwDown.hide()
        self.function_v_DropwDown.hide()
        self.function_l_DropwDown.hide()

        self.componentValueInput.hide()
        self.componentValueLabel.hide()

        if self.componentDropwDown.currentText() == "Coil":
            self.componentValueInput.setText("0.0")
            self.componentValueInput.show()
            self.componentValueLabel.show()

            self.function_l_DropwDown.show()

        elif self.componentDropwDown.currentText() == "Resistor":
            self.function_r_DropwDown.show()

        elif self.componentDropwDown.currentText() == "Capacitator":
            self.function_c_DropwDown.show()

        elif self.componentDropwDown.currentText() == "V-Source":
            self.function_v_DropwDown.show()

        elif self.componentDropwDown.currentText() == "I-Source":
            self.function_i_DropwDown.show()
       #else:
            #self.componentValueInput.hide()
            #self.componentValueLabel.hide()

    def addComponentToCircuit(self):
        """Handels the adding of a new component to the circuit"""

        component = (str(self.componentDropwDown.currentText()))
        function = "0"

        if component == "Capacitator":
            function = self.function_c_DropwDown.currentText()

        if component == "I-Source":
            function = self.function_i_DropwDown.currentText()

        if component == "Resistor":
            function = self.function_r_DropwDown.currentText()

        if component == "V-Source":
            function = self.function_v_DropwDown.currentText()

        if component == "Coil":
            function = self.function_l_DropwDown.currentText()

        direction = (str(self.directionDropwDown.currentText()))
        name = (str(self.componentNameInput.text()))

        elabel = self.controler.addComponent(component, direction, name, self.potenzialDropDownFrom.currentIndex(), self.potenzialDropDownTo.currentIndex(), self.componentValueInput.text(), function)


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
        """Updates the current visual representation of the circuit"""
        
        self.pixmap = QtGui.QPixmap(self.path + "\\resources\\ergebnis.png")
        self.image.setPixmap(self.pixmap)

    def simulate(self):
        """Collects all nessesary inputs to the start the simulation and starts it"""

        self.potenzialDropDown.clear()
        for x in range(len(self.list_potencialInputs)):
            self.controler.addPotencialValue("E" + str(x), self.list_potencialInputs[x].text())

        self.controler.setTValues(float(self.list_timeInputs[0].text()), float(self.list_timeInputs[1].text()))

        self.potenzialParameters.close()

        try:
            self.controler.simulate()
            qt = QtGui.QMessageBox()
            qt.setIcon(QtGui.QMessageBox.Information)
            qt.setWindowTitle("Info")
            qt.setText("Simulation was successfull!")
            qt.exec()
        except:
            qt = QtGui.QMessageBox()
            qt.setIcon(QtGui.QMessageBox.Critical)
            qt.setWindowTitle("An Error Occured")
            qt.setText("The circuit could not be simulated \nThe circuit might not be valid")
            qt.exec()

        for potencial in range(len(self.potenzialDropDownFrom)-2):
            self.potenzialDropDown.addItem("Potencial " + str(potencial))

        self.potenzialDropDown.show()
        self.buttonPlotPotenzial.show()

    def enterPotencialValues(self):   
        """Creates the input fields for the starting values of the simulation"""
        
        self.potenzialParameters = QtGui.QDialog()

        layout = QtGui.QFormLayout()

        label_t = QtGui.QLabel("Please insert the time to simulate")
        t_input = QtGui.QLineEdit()
        t_input.setObjectName("")
        t_input.setText("1.0")
        t_input.setValidator(self.validator)

        label_t_steps = QtGui.QLabel("Please insert the steps you want to split the time")
        t_steps_input = QtGui.QLineEdit()
        t_steps_input.setObjectName("")
        t_steps_input.setText("1.0")
        t_steps_input.setValidator(self.validator)

        layout.addRow(label_t, t_input)
        layout.addRow(label_t_steps, t_steps_input)

        self.list_timeInputs = [t_input, t_steps_input]

        label_infoPotencial = QtGui.QLabel("Please insert start-value (float) for the potencials")
        self.list_potencialInputs = []

        for potencial in range(len(self.potenzialDropDownFrom)-2):
            inputPotencialLayout = QtGui.QHBoxLayout()

            potencialValueLabel = QtGui.QLabel("Value of Potencial:" + str(potencial))
            
            potencialValueInput = QtGui.QLineEdit()
            potencialValueInput.setObjectName("")
            potencialValueInput.setText("1.0")
            potencialValueInput.setValidator(self.validator)
            inputPotencialLayout.addWidget(potencialValueLabel)
            inputPotencialLayout.addWidget(potencialValueInput)
            layout.addRow(inputPotencialLayout)
            self.list_potencialInputs.append(potencialValueInput)

        button_startSimulation = QtGui.QPushButton("Start Simulation")
        button_startSimulation.clicked.connect(self.simulate)
        layout.addRow(button_startSimulation)

        self.potenzialParameters.setLayout(layout)
        self.potenzialParameters.setWindowTitle("Potencial Values")


        self.potenzialParameters.exec()
 
    def plot2(self):
        """Plots the simulated data for a choosen potencial"""

        x = []
        y = []
        data = self.controler.getSolutionData()

        for entry in data:

            x.append(entry[0][0][self.potencial])
            y.append(entry[1])
 
        ax = self.figure.add_subplot(111)
 
        ax.clear()

        ax.set_xlabel("Time")
        ax.set_ylabel("Potencial Value")

        ax.plot(y,x)
        self.figure.tight_layout()

        self.canvas.draw()
        self.figure.delaxes(ax)
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    main = Window(sys.argv)

    sys.exit(app.exec_())


