import matplotlib.pyplot as plt
from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import random

class ScrollableWindow(QtGui.QMainWindow):
    def __init__(self, fig):
        self.qapp = QtGui.QApplication([])

        QtGui.QMainWindow.__init__(self)
        self.widget = QtGui.QWidget()
        self.setCentralWidget(self.widget)
        self.widget.setLayout(QtGui.QVBoxLayout())
        self.widget.layout().setContentsMargins(0,0,0,0)
        self.widget.layout().setSpacing(0)

        self.fig = fig
        self.canvas = FigureCanvas(self.fig)
        self.canvas.draw()
        self.scroll = QtGui.QScrollArea(self.widget)
        self.scroll.setWidget(self.canvas)

        self.nav = NavigationToolbar(self.canvas, self.widget)
        self.widget.layout().addWidget(self.nav)
        self.widget.layout().addWidget(self.scroll)

        self.canvas.mpl_connect("scroll_event", self.scrolling)

        #self.show()
        #exit(self.qapp.exec_())

    def exit(self):
        exit(self.qapp.exec_())

    def scrolling(self, event):
        val = self.scroll.verticalScrollBar().value()
        if event.button =="down":
            self.scroll.verticalScrollBar().setValue(val+100)
        else:
            self.scroll.verticalScrollBar().setValue(val-100)


class test:

    def __init__(self):
        # create a figure and some subplots
        fig = plt.figure()
        #for ax in axes.flatten():
        #    data = [random.random() for i in range(10)]
        data = [random.random() for i in range(10)]
                # create an axis
        axes = fig.add_subplot(111)
            #ax.plot([2,3,5,1])
        axes.clear()

                # plot data
        axes.plot(data, '*-')


        # pass the figure to the custom window
        self.a = ScrollableWindow(fig)

    def destroy(self):
        self.a.destroy()
