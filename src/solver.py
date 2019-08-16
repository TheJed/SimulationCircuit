"""
    This module handels the mathe behind the simulation
    :copyright: (c) 2019 by Tobias Klein.
"""

import numpy as np
import createV_W_Matrix
from sympy import Matrix
from scipy import optimize
from scipy.sparse import linalg as linalgSolver
from scipy.integrate import odeint
from scipy.integrate import ode
from scipy.sparse.csgraph import minimum_spanning_tree as spanningTree
from scipy.sparse.csgraph import breadth_first_tree as bfTree
import numpy.linalg as LA
from scipy.sparse.linalg import lsqr

class Solver:

    def __init__(self, schaltung):
        self.schaltung = schaltung
        self.potencialList = schaltung.potencialList
        self.jl = self.schaltung.getjl()
        self.solution = [] 
        self.gr = self.schaltung.getGr()
        self.vt = self.schaltung.getV_t()
        self.it = self.schaltung.getI_t()
        self.c_dx = self.schaltung.getC_dx()
        self.c_dt = self.schaltung.getC_dt()
        self.l_dx = self.schaltung.getL_dx()
        self.l_dt = self.schaltung.getL_dt()      

    def createInzidenzMatrices(self):
        """This function creates all the reduced Inzidenz-Matrices"""

        self.inzidenz_v = self.schaltung.inzidenz_v
        self.inzidenz_c = self.schaltung.inzidenz_c
        self.inzidenz_r = self.schaltung.inzidenz_g
        self.inzidenz_l = self.schaltung.inzidenz_l
        self.inzidenz_i = self.schaltung.inzidenz_i

                
        #-----------Delete voltage sources-----------
        self.c_v = self.findConnectedComponents(self.inzidenz_v.transpose())
        self.q_v = self.createQArray(self.c_v, self.isMasse(self.inzidenz_v))
        self.p_v = self.createPArray(self.c_v, self.isMasse(self.inzidenz_v))

        self.ac_v = self.inzidenz_c
        if not 0 in self.inzidenz_c.shape:  
            self.ac_v = np.dot(self.q_v.transpose(), (self.inzidenz_c))

        self.al_v = self.inzidenz_l
        if not 0 in self.inzidenz_l.shape:  
            self.al_v = np.dot(self.q_v.transpose(), self.inzidenz_l)

        self.ar_v = self.i_r
        if not 0 in self.inzidenz_r.shape:  
            self.ar_v = np.dot(np.transpose(self.q_v), self.inzidenz_r)

        self.ai_v = self.inzidenz_i
        if not 0 in self.inzidenz_i.shape:  
            self.ai_v = np.dot(self.q_v.transpose(), (self.inzidenz_i))

        #-----------Delete capacitors-----------
        self.c_c = self.findConnectedComponents(np.array(self.ac_v).transpose())
        self.q_c = self.createQArray(self.c_c, self.isMasse(self.ac_v))
        self.p_c = self.createPArray(self.c_c, self.isMasse(self.ac_v))

        self.al_vc = self.inzidenz_l
        if not 0 in self.inzidenz_l.shape:   
            self.al_vc = np.dot(self.q_c.transpose(), self.al_v)

        self.ai_vc = self.inzidenz_i
        if not 0 in self.inzidenz_i.shape:  
            self.ai_vc = np.dot(self.q_c.transpose(), self.ai_v)

        self.ar_vc = self.inzidenz_r
        if not 0 in self.inzidenz_r.shape:  
            self.ar_vc = np.dot(self.q_c.transpose(), self.ar_v)

        #-----------Delete Resistors-----------
        self.c_r = self.findConnectedComponents(np.array(self.ar_vc).transpose())
        self.q_r = self.createQArray(self.c_r, self.isMasse(self.ar_vc))
        self.p_r = self.createPArray(self.c_r, self.isMasse(self.ar_vc))

        self.al_vcr = self.inzidenz_l
        if not 0 in self.inzidenz_l.shape:  
            self.al_vcr = np.dot(self.q_r.transpose(), self.al_vc)

        self.ai_vcr = self.inzidenz_i
        if not 0 in self.inzidenz_i.shape:  
            self.ai_vcr = np.dot(self.q_r.transpose(), self.ai_vc)

        #-----------Calculate Loops-----------
        self.v_matrix = np.array([])
        self.w_matrix = np.array([])
        if not 0 in self.inzidenz_l.shape:
            self.v_matrix, self.w_matrix = createV_W_Matrix.tiefensuche(self.al_vcr)

    def simulate(self, t, t_steps):
        """This function starts the simulation. 
        The simulation of future values is done by an ODE-Solver
        
        :param t: time to simulate to
        :param t_steps: time-interval the time is divided into
        :return: Returns a list with all simulate potencial-values for specific t's.
        :rtype: list of tupels."""

        #--------initialize needed Values--------
        self.createInzidenzMatrices()
        self.startwertEntkopplung(self.potencialList, 0)

        j_li = self.jl_i(self.jl)
        t = np.arange(0, t, t_steps)

        #--------Check Input Parameters and start Simulation--------
        if 0 in self.ec.shape and not 0 in j_li.shape:
            x = []
            for i in j_li.tolist():
                x.append(i[0])
            odeint(self.cgSolve, x, t)

        elif not 0 in self.ec.shape and 0 in j_li.shape:
            x = []
            for i in self.ec.tolist():
                x.append(i[0])
            odeint(self.cgSolve, x, t)

        elif 0 in self.ec.shape and 0 in j_li.shape:
            x = np.array([0])
            for x in t:
                self.newton2(x)
        else:   
            x = []
            for i in self.ec.tolist():
                x.append(i[0])
            for i in j_li.tolist():
                x.append(i[0])
            odeint(self.cgSolve, x, t)
        
        return self.solution

    def g_xyt(self, ec,e_r,t):
        """This function provides a for the simulation nessesary function (simulation of resistors).
        Therefore it contains no business-logic, only simple math-operations to build the function
        
        :param ec: decoppeld potencial value for capacitors
        :param e_r: decoppeld potencial value for resistors
        :param t: actual point in time the simulation is at
        :return: Returns the builded function.
        :rtype: function."""

        funktionPart_1 = np.dot(np.transpose(self.p_r), self.ar_vc)
        parameters = np.dot(np.transpose(self.ar_vc), self.p_r)
        funktionPart_1 = np.dot(funktionPart_1, self.gr_not_vc(np.dot(parameters, e_r), ec, t))

        functionPart_2 = 0
        if not 0 in self.inzidenz_l.shape:

            functionPart_2 = np.dot(np.transpose(self.p_r), self.al_vc)
            qliJl_i = self.jl - self.v_matrix.dot(self.i_star(t))
            functionPart_2 = np.dot(functionPart_2, qliJl_i)

        return np.add(np.add(funktionPart_1,functionPart_2),self.i_r(t))

    def gr_not_vc(self, x,ec,t):
        """This function provides a for the simulation nessesary function (simulation of resistors).
        Therefore it contains no business-logic, only simple math-operations to build the function
        
        :param x: decoppeld and modified potencial value for resistors
        :param ec: decoppeld potencial value for capacitors
        :param t: actual point in time the simulation is at
        :return: Returns the builded function.
        :rtype: function."""
        
        if 0 in self.ar_v.shape or 0 in self.p_c.shape:
            parameter1 = 0
        else:   
            parameter1= self.ar_v.transpose().dot(self.p_c) 
            parameter1= parameter1.dot(ec)

        if 0 in self.inzidenz_r.shape or 0 in self.p_v.shape or not self.inzidenz_v.shape:
            parameter3 = 0
        else:
            parameter2 = np.dot(np.transpose(self.inzidenz_r), self.p_v)
        
            parameter3 = (np.dot(parameter2, self.v_star(t)))

        f = self.g_r(np.add(np.add(x,parameter1),parameter3), t)
        return f

    def matrix_mc(self, ec, t):
        """This function provides a for the simulation nessesary matrix (simulation of capacitors).
        Therefore it contains no business-logic, only simple math-operations to build the matrix
        
        :param ec: decoppeld potencial value for capacitors
        :param t: actual point in time the simulation is at
        :return: Returns the builded matrix.
        :rtype: numpy.array"""
        
        if 0 in self.p_c.shape or 0 in self.ac_v.shape:
            return np.array([])
        matrix = np.dot(np.transpose(self.p_c), self.ac_v)
        parameter = np.dot(np.transpose(self.ac_v), self.p_c)
        parameter = np.dot(parameter, ec)
        matrix = np.dot(matrix, self.ableitung_c_nachx(parameter, t))
        matrix = np.array(matrix).dot(np.transpose(self.ac_v)).dot(self.p_c)
        return matrix

    def matrix_ml(self, jl_i, t):
        """This function provides a for the simulation nessesary matrix (simulation of coils).
        Therefore it contains no business-logic, only simple math-operations to build the matrix
        
        :param jl_i: decoppeld potencial value for coils
        :param t: actual point in time the simulation is at
        :return: Returns the builded matrix.
        :rtype: numpy.array"""

        qliJl_i = self.jl - self.v_matrix.dot(self.i_star(t))

        matrix = self.w_matrix.transpose().dot(self.ableitung_l_nachx(qliJl_i, t)).dot(self.w_matrix)

        return matrix

    def function1(self, ec, jl_i, e_r, t):
        """This function provides a for the simulation nessesary function (simulation of capacitors).
        Therefore it contains no business-logic, only simple math-operations to build the function
        
        :param ec: decoppeld potencial value for capacitors
        :param jl_i: decoppeld potencial value for coils
        :param e_r: decoppeld potencial value for resistors
        :param t: actual point in time the simulation is at
        :return: Returns the builded function.
        :rtype: function."""

        summand1 = 0
        if not 0 in self.ac_v.shape:
            summand1 = self.p_c.transpose().dot(self.ac_v)
            parameter = np.transpose(self.ac_v).dot(self.p_c).dot(ec)
            summand1 = summand1.dot(self.ableitung_c_nacht(parameter, t))
        
        summand2 = 0
        if not 0 in self.al_v.shape:
            qliJl_i = self.jl - self.v_matrix.dot(self.i_star(t))
            summand2 = self.p_c.transpose().dot(self.al_v).dot(qliJl_i)

        summand3 = 0
        if not 0 in self.ar_vc.shape:
            parameter2 = self.ar_vc.transpose().dot(self.p_r).dot(e_r)
            summand3 = self.p_c.transpose().dot(self.ar_v).dot(self.gr_not_vc(parameter2, np.array(ec), t))

        summand4 = self.i_c(t)

        function1 = np.add(summand1, np.add(summand2, np.add(summand3, summand4)))

        return function1

    def function2(self, ec, jl_i, e_r, t):
        """This function provides a for the simulation nessesary function (simulation of coils).
        Therefore it contains no business-logic, only simple math-operations to build the function
        
        :param ec: decoppeld potencial value for capacitors
        :param jl_i: decoppeld potencial value for coils
        :param e_r: decoppeld potencial value for resistors
        :param t: actual point in time the simulation is at
        :return: Returns the builded function.
        :rtype: function."""
       
        qliJl_i = self.jl - self.v_matrix.dot(self.i_star(t))
        
        minuend1 = np.transpose(self.w_matrix).dot(self.ableitung_l_nacht(qliJl_i, t))
        minuend2 = 0
        minuend3 = 0
        minuend4 = 0
        if not 0 in self.al_v.shape:
            minuend2 = np.transpose(self.w_matrix).dot(np.transpose(self.al_v)).dot(self.p_c).dot(ec)
            minuend3 = np.transpose(self.w_matrix).dot(np.transpose(self.al_vc)).dot(self.p_r).dot(e_r)
            minuend4 = self.v_l(t)

        function2 = np.subtract(minuend1, np.subtract(minuend2, np.subtract(minuend3, minuend4)))
        return function2

    def g_r(self, x, t):
        """This function returns the values of the resistors of a specific voltage and point in time
        
        :param x: voltage-value
        :param t: actual point in time the simulation is at
        :return: Returns the builded function.
        :rtype: resistor values."""

        ergebnis = []
        for i in range(len(self.gr)):
            ergebnis.append(self.gr[i](x[i],t))

        return np.array(ergebnis)

    def ableitung_c_nachx(self, ec, t):
        """This function returns the derivative (for voltage) values of the capacitors of a specific voltage and point in time
        
        :param ec: voltage-value
        :param t: actual point in time the simulation is at
        :return: Returns the builded function.
        :rtype: function."""

        ergebnis = []

        for i in range (len(self.c_dx)):
            zeile = [0 for k in range(len(self.c_dx))]
            zeile[i] = self.c_dx[i](ec,t)
            ergebnis.append(zeile)

        return np.array(ergebnis)

    def ableitung_c_nacht(self, ec, t):
        """This function returns the derivative (for time) values of the capacitors of a specific voltage and point in time
        
        :param ec: voltage-value
        :param t: actual point in time the simulation is at
        :return: Returns the builded function.
        :rtype: function."""

        ergebnis = []
        for function in self.c_dt:
            ergebnis.append(function(ec,t))

        return np.array(ergebnis)

    def ableitung_l_nachx(self, x, t):
        """This function returns the derivative (for voltage) values of the capacitors of a specific voltage and point in time
        
        :param x: voltage-value
        :param t: actual point in time the simulation is at
        :return: Returns the builded function.
        :rtype: function."""

        ergebnis = []
        for i in range (len(self.l_dx)):
            zeile = [0 for k in range(len(self.l_dx))]
            zeile[i] = self.l_dx[i](x,t)
            ergebnis.append(zeile)

        return np.array(ergebnis)

    def ableitung_l_nacht(self, x, t):
        """This function returns the derivative (for voltage) values of the capacitors of a specific voltage and point in time
        
        :param x: voltage-value
        :param t: actual point in time the simulation is at
        :return: Returns the builded function.
        :rtype: function."""

        ergebnis = []
        for function in self.l_dt:
            ergebnis.append(function(x,t))

        return np.array(ergebnis)

    def v_star(self,t):
        """This function provides a for the simulation nessesary function.
        It is a list of modifed other function, which the user selected for the behavior of voltage-sources.
        Therefore it contains no business-logic, only simple math-operations to build the function

        :param t: actual point in time the simulation is at
        :return: Returns the builded function.
        :rtype: function."""

        if not (self.inzidenz_v):
            return np.zeros((self.p_v.shape))

        matrixA = np.dot(np.transpose(self.inzidenz_v), self.p_v)
        ergebnis = linalgSolver.cg(matrixA,self.v_t(t))
        return ergebnis   

    def v_t(self, t):
        """This function returns the voltage values of the voltage-sources for a point in time

        :param t: actual point in time the simulation is at
        :return: Returns the builded function.
        :rtype: voltage values."""

        ergebnis = []
        for function in self.vt:
            ergebnis.append(function(0,t))

        return np.array(ergebnis)

    def i_star(self, t):
        """This function provides a for the simulation nessesary function.
        It is a list of modifed other function, which the user selected for the behavior of power-sources.
        Therefore it contains no business-logic, only simple math-operations to build the function
        
        :param t: actual point in time the simulation is at
        :return: Returns the builded function.
        :rtype: function."""

        if 0 in self.inzidenz_l.shape:
            return 0
        matrixA = np.dot(self.al_vcr,self.v_matrix)

        vektorB = np.dot(np.dot(self.ai_vcr,-1), self.i_s(t))
        ergebnis = linalgSolver.cg(matrixA,vektorB)

        return ergebnis[0]
   
    def i_c(self, t):
        """This function provides a for the simulation nessesary function.
        Therefore it contains no business-logic, only simple math-operations to build the function
        
        :param t: actual point in time the simulation is at
        :return: Returns the builded function.
        :rtype: function."""
        

        summand1 = 0
        if not 0 in self.ai_v.shape and not 0 in self.p_c:
            summand1 = self.p_c.transpose().dot(self.ai_v).dot(self.i_s(t))

        summand2 = 0
        if not 0 in self.al_v.shape:
            summand2 = self.p_c.transpose().dot(self.al_v).dot(self.v_matrix).dot(self.i_star(t))
        function = np.add(summand1, summand2)
        return function

    def i_s(self,t):
        """This function returns the values of the power-sourcesfor a point in time
        
        :param t: actual point in time the simulation is at
        :return: Returns the builded function.
        :rtype: power-values."""

        ergebnis = []
        for function in self.it:
            ergebnis.append(function(t))

        return np.array(ergebnis)
    
    def i_r(self,t):
        """This function provides a for the simulation nessesary function.
        Therefore it contains no business-logic, only simple math-operations to build the function
        
        :param t: actual point in time the simulation is at
        :return: Returns the builded function.
        :rtype: function."""

        summand1 = 0
        summand2 = 0
        if not 0 in self.inzidenz_i.shape:
            summand1 = self.p_r.transpose().dot(self.ai_vc).dot(self.i_s(t))
            if not 0 in self.inzidenz_l.shape:
                summand2 = self.p_r.transpose().dot(self.al_vc).dot(self.v_matrix).dot(self.i_star(t))
        ergebnis = np.add(summand1,summand2)
        return ergebnis

    def v_l(self, t):
        """This function provides a for the simulation nessesary function.
        Therefore it contains no business-logic, only simple math-operations to build the function
        
        :param t: actual point in time the simulation is at
        :return: Returns the builded function.
        :rtype: function."""

        ergebnis = -self.w_matrix.transpose().dot(self.inzidenz_l.transpose()).dot(self.p_v).dot(self.v_star(t))
        return ergebnis

    def e_l(self, e_c, e_r, t):
        """Calculates the e_l value (value of decoupled potenzials) based on e_c and e_r
        
        :param e_c: calculated e_c value from the simulation
        :param e_r: calculated e_r value from the simulation
        :param t: actual point in time the simulation is at
        :return: Returns calculated e_l value.
        :rtype: vector."""

        m = np.array([])
        minuend1 = 0
        minuend2 = 0
        minuend3 = 0
        minuend4 = 0

        if not 0 in self.inzidenz_l.shape and not 0 in self.v_matrix:
            m = self.v_matrix.transpose().dot(self.al_vcr.transpose())
            if not 0 in self.p_c.shape:
                minuend2 = m.dot(self.al_v.transpose()).dot(self.p_c).dot(e_c)
            if not 0 in self.p_r.shape:
                minuend3 = m.dot(self.al_vc.transpose()).dot(self.p_r).dot(e_r)
            if not 0 in self.p_v.shape:
                minuend4 = m.dot(self.inzidenz_l.transpose()).dot(self.p_v).dot(self.v_star(t))
            minuend1 = self.v_matrix.transpose().dot(self.ableitung_l_nacht(self.w_matrix, t))

            b = np.subtract(minuend1, minuend2)  
            b = np.subtract(b, minuend3)
            b = np.subtract(b, minuend4)
            
            e_l = linalgSolver.cg(m,b)[0]

            return e_l

        return 0

    def jl_i(self, t):
        """Calculates the j_li value (value of decoupled coils) for a specific point in time

        :param t: actual point in time the simulation is at
        :return: Returns calculated jl_i value.
        :rtype: vector."""

        if 0 in self.inzidenz_l.shape:
            return np.zeros((1,0))
        if 0 in self.w_matrix.shape:
            return np.zeros((self.jl.shape[0], 1))
        b = self.jl - self.v_matrix.dot(self.i_star(t))
        m = self.w_matrix

        e = LA.solve(m,b)
        return e

    def startwertEntkopplung(self, e, t):
        """This function decoppels the starting-potencials for simulation
        
        :param e: list of starting values for the potencials
        :param t: actual point in time the simulation is at
        """
        e = np.array(e)

        #--------calculate e_v--------
        if not 0 in self.p_v.shape:
            m = self.q_v
            
            b = np.subtract(e, self.p_v.dot(self.v_star(t)))

            self.e_v = linalgSolver.cg(m,b)[0]
        else:
            m = self.q_v
            self.e_v = linalgSolver.cg(m,e)[0]

        #--------calculate ec and e_c--------

        m = np.concatenate((self.p_c, self.q_c), axis= 1)
        temp = LA.solve(m,self.e_v)
        if self.p_c.shape[1] == 0:
            self.ec = np.zeros((self.p_c.shape))
        else:
            self.ec = np.zeros((self.p_c.shape[1], 1))
        self.e_c = []
        for i in range(len(temp)):
            if i<self.p_c.shape[1]:
                self.ec[i] = (temp[i])
            else:
                self.e_c.append(temp[i])

        #--------calculate er and el-------- 
        m = np.concatenate((self.p_r, self.q_r), axis= 1)
        temp = LA.solve(m,self.e_c)
        self.er = []
        el = []
        for i in range(len(temp)):
            if i<self.p_r.shape[1]:
                self.er.append(temp[i])
            else:
                el.append(temp[i])  
      
    def zurueckcoppler(self, ec, er, t):
        """This function calculates the values of the potencials for a specific point in time based on the decoppeld potencial values

        :param ec: decoppeld potencial value for capacitors
        :param e_r: decoppeld potencial value for resistors
        :param t: actual point in time the simulation is at
        :return: Returns calculated potencial value.
        :rtype: vector."""

        if type(ec) is np.float64:
            ec = [ec]
            
        if type(er) is np.float64:
            er = [er]

        summand1 = 0
        if not 0 in self.p_v.shape:
            summand1 = self.p_v.dot(self.v_star(t))

        summand2 = 0
        if not 0 in self.q_v.shape and 0 not in self.p_c.shape:
            summand2 = self.q_v.dot(self.p_c).dot(ec)

        summand3 = 0
        
        if not 0 in self.q_c.shape and 0 not in self.p_r.shape and 0 not in self.q_v.shape:
            summand3 = self.q_v.dot(self.q_c).dot(self.p_r).dot(er)

        summand4 = 0
        
        if 0 not in self.q_v.shape and 0 not in self.q_c.shape and 0 not in self.q_r.shape and not 0 in self.inzidenz_l.shape:
            summand4 = self.q_v.dot(self.q_c).dot(self.q_r).dot(self.e_l(ec,er,t))

        e = summand1 + summand2 + summand3 + summand4
        return e

    def isMasse(self, inzidenz):
        """This function checks if at least one component of a component group is connected to the mass-potencial
        
        :param inzidenz: the inzidenz matrix of the component group
        :return: Returns if at least one component of a component group is connected to the mass-potencial.
        :rtype: boolean."""
        
        if 0 in inzidenz.shape:
            return False
        unique, count = np.unique(inzidenz, return_counts=True)

        #-------There are only two potencials left and one of them is the mass-potencial--------
        if(len(count) == 1):
            return True
        if(count[0] == count[-1]):
            return False
        else:
            return True

    def findConnectedComponents(self, inzidenzMatrix):
        """This function calculates the connected components for a specific component group
        
        :param inzidenzMatrix: the inzidenz matrix of the component group
        :return: Returns a list with the connected components
        :rtype: list of integers."""

        if not inzidenzMatrix.tolist():
            potenzialListe = list(range(self.schaltung.potenzialNumber-1))
        else:
            potenzialListe = list(range(inzidenzMatrix.shape[1]))
        
        zusammenhangskomponenteListe = []
        while len(potenzialListe) > 0:

            potenzialListe, c_x = self.deepSearchComponent(potenzialListe, potenzialListe[0], inzidenzMatrix, 0)
            zusammenhangskomponenteListe.append(c_x)

        return zusammenhangskomponenteListe

    def deepSearchComponent(self, notVisitedPotencials, potencial, inzidenzMatrix, zusammenhangskomponente):
        """This function finds the connected components for a specific component group with depth-search
        
        :param notVisitedPotencials: list of unvisited potencials
        :param potencial: current potencial
        :param inzidenzMatrix: the inzidenzMatrix of the component group
        :param zusammenhangscomponente: current number of connected components
        :return: Returns a list with the unvisited potencials and the number of connected components
        :rtype: list, integer."""

        if len(notVisitedPotencials) == 0:
            return notVisitedPotencials, zusammenhangskomponente
        zusammenhangskomponente += 1
        notVisitedPotencials.remove(potencial)

        for element in inzidenzMatrix:

            if element[potencial] != 0:

                if element[potencial] * -1 in element.tolist():
                    outputPotencial = element.tolist().index(element[potencial] * -1)

                    if outputPotencial in notVisitedPotencials:

                        notVisitedPotencials, zusammenhangskomponente = self.deepSearchComponent(notVisitedPotencials, outputPotencial, inzidenzMatrix, zusammenhangskomponente)
            
        return notVisitedPotencials, zusammenhangskomponente
        
    def createQArray(self, c_x, isMasse):
        """This function calculates the Q-Array for component-groups. The Q-Array is a kernel of the inzidenz matrix from the component-group 
        
        :param c_x: list of connected components
        :param isMasse: is one of the components connected to the mass-potencial
        :return: Returns the Q-Array
        :rtype: np.array."""

        if(isMasse):
            if(len(c_x) == 1 and c_x[0] == 1):
                print([])
                return np.array([[1]])
            qArray = np.zeros((sum(c_x), len(c_x)))
        else:
            qArray = np.zeros((sum(c_x), len(c_x)))

        zeile = 0
        for x in range(0, len(c_x)):
            for i in range (0,c_x[x]):
                qArray[zeile][x] = 1
                zeile += 1
        return qArray

    def createPArray(self, c_x, isMasse):

        """This function calculates the P-Array for component-groups.
        
        :param c_x: list of connected components
        :param isMasse: is one of the components connected to the mass-potencial
        :return: Returns the P-Array
        :rtype: np.array."""

        rows = 0
        columns = 0
        for x in c_x:
            columns = columns + x-1
            rows += x-1 + 1
        
        dimension = (rows, columns)
        pArray = np.zeros(dimension)

        c_x1 = [value-1 for value in c_x]
        spalte = 0
        zeile = 0
        for x in c_x1:

            i = x
            while i > 0:
                pArray[zeile][spalte] = 1
                i = i -1
                spalte+= 1
                zeile += 1

            zeile += 1

        return pArray
        
    def cgSolve(self, x, t):
        """This is function is part of the simulation and calculates new ec and jl_i values for a specific point in time

        :param x: vector consiting of ec and jl_i values
        :param t: point in time
        :return: Returns the new ec and jl_i values
        :rtype: vector."""

        j_li = []
        ec = []
    
        for i in range(len(x)):
            if i<len(self.ec):
                ec.append(x[i])
            else:
                j_li.append(x[i])        

        e_r = self.newton(ec, t)

        if not 0 in self.inzidenz_c.shape:
            mc = self.matrix_mc(ec, t)
            if not 0 in mc.shape:
                ec = linalgSolver.cg(mc, self.function1(ec, j_li, e_r, t))[0]

        if not 0 in self.inzidenz_l.shape:
            ml = self.matrix_ml(j_li, t)
            if not 0 in ml.shape:
                j_li = linalgSolver.cg(ml, self.function2(ec, j_li, e_r, t))[0]

        e = self.zurueckcoppler(ec, e_r, t)
        self.solution.append(([e], t))

        if not type(ec) == list:
            ec = ec.tolist()
        if not type(j_li) == list:
            j_li = j_li.tolist()
        
        x_new = ec
        for i in j_li:
            x_new.append(i)
        return x_new

    def newton(self,ec, t):
        """This is function is part of the simulation and calculates new er values for a specific point in time

        :param ec: Old ec values
        :param t: point in time
        :return: new er value
        :rtype: vector."""
        
        if 0 in self.inzidenz_r.shape:
            return self.er
        f = lambda e_r: self.g_xyt(ec,e_r,t)
        if type(self.er) == list:
            if len(self.er) == 1:
                self.er = self.er[0]
        self.er = optimize.newton(f, self.er,tol=1e-10, maxiter=50000, disp=False)
        return self.er
        
    def newton2(self, t):
        """This is function is modified version of the other newton function and is choosen if a circuit has no capacitors and coils

        :param t: point in time
        :return: new er value
        :rtype: vector."""

        if 0 in self.inzidenz_r.shape:
            return self.er
        f = lambda e_r: self.g_xyt(self.ec,e_r,t)
        if type(self.er) == list:
            if len(self.er) == 1:
                self.er = self.er[0]

        self.er = optimize.newton(f, self.er,tol=1e-10, maxiter=50000, disp=False)
        e = self.zurueckcoppler(self.ec, self.er, t)
        self.solution.append(([e], t))
        return self.er