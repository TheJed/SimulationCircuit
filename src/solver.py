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
        print("potenzialliste:", self.potencialList)
        self.jl = 0
        self.solution = []       

    def createInzidenzMatrices(self):
        """This function creates all the reduced Inzidenz-Matrices"""

        self.inzidenz_v = self.schaltung.inzidenz_v
        self.inzidenz_c = self.schaltung.inzidenz_c
        self.inzidenz_r = self.schaltung.inzidenz_g
        self.inzidenz_l = self.schaltung.inzidenz_l
        self.inzidenz_i = self.schaltung.inzidenz_i
        
        self.g_r = self.schaltung.getGr()
        self.v_t = self.schaltung.getV_t()

        
        #Vs löschen
        self.c_v = self.findeZusammenhangskomponente(self.inzidenz_v.transpose())
        self.q_v = self.createQArray(self.c_v, self.isMasse(self.inzidenz_v))
        self.p_v = self.createPArray(self.c_v, self.isMasse(self.inzidenz_v))

        #Delete V_sources
        self.ac_v = np.dot(self.q_v.transpose(), (self.inzidenz_c))
        print("Ac_v: \n", self.ac_v)

        self.al_v = np.dot(self.q_v.transpose(), self.inzidenz_l)
        print("Al_v: \n", self.al_v)

        self.ar_v = np.dot(np.transpose(self.q_v), self.inzidenz_r)
        print("Ar_v: \n", self.ar_v)

        self.ai_v = np.dot(self.q_v.transpose(), (self.inzidenz_i))
        print("ai_v;", self.ai_v)

        #Kondesatoren
        self.c_c = self.findeZusammenhangskomponente(np.array(self.ac_v).transpose())
        self.q_c = self.createQArray(self.c_c, self.isMasse(self.ac_v))
        self.p_c = self.createPArray(self.c_c, self.isMasse(self.ac_v))

        #Delete Kondensators    
        self.al_vc = np.dot(self.q_c.transpose(), self.al_v)
        print("Al_cv: \n", self.al_vc)

        self.ai_vc = np.dot(self.q_c.transpose(), self.ai_v)
        print("Ai_vc:", self.ai_vc)

        self.ar_vc = np.dot(self.q_c.transpose(), self.ar_v)
        print("Ar_vc: \n", self.ar_vc)

        #Resistors
        self.c_r = self.findeZusammenhangskomponente(np.array(self.ar_vc).transpose())
        self.q_r = self.createQArray(self.c_r, self.isMasse(self.ar_vc))
        self.p_r = self.createPArray(self.c_r, self.isMasse(self.ar_vc))

        #Delete Resistances   
        self.al_vcr = np.dot(self.q_r.transpose(), self.al_vc)
        print("Al_vcr: \n", self.al_vcr)

        #tempMatrix = self.q_r.transpose().dot(tempMatrix)
        self.ai_vcr = np.dot(self.q_r.transpose(), self.ai_vc)
        print("Ai_vcr: \n", self.ai_vcr)

        #self.ail_vcr = np.concatenate((np.array(self.al_vcr),np.array(self.ai_vcr)),axis=1)
        #print("ail_vcr:", self.ail_vcr)

        self.v_matrix, self.w_matrix = createV_W_Matrix.tiefensuche(self.al_vcr)
        #TODO berechnen neu wegen Beispiel. hier Fehler
        #self.w_matrix = np.array([[]])
        print()
        #self.v_matrix = np.array([[1]])
        input()

    def simulate(self):
        """This function starts the simulation. 
        The simulation of future values is done by an ODE-Solver
        
        :return: Returns a list with all simulate values for specific t's.
        :rtype: list of tupels."""

        self.createInzidenzMatrices()
        self.startwertEntkopplung(self.potencialList, 0)


        #A mal Q muss nämlich immer 0 ergeben, bzw A transponiert
        #print("TEEEEST:", np.dot(self.w_matrix, np.transpose(self.ail_vcr)))
   
        print("------------Begin Calculation------------------")

        #TODO eigentlich Vektor und kein Skalar
        #ec = [2]
        #e_r = [0,0]
        j_li = [0]
        #x = ec
        t = 10

        #self.solve(ec, j_li)
        #self.e_r = [0,0]
        print("ec:", self.ec)
        x = np.concatenate((self.ec, j_li), axis=0)
        t = np.arange(0, 10, 1.0)
        print("x_start:", x)
        print("T:", t)

        """r = ode(self.cgSolve).set_integrator('zvode', method='bdf', with_jacobian=False)
        r.set_initial_value(x, 0)
        t1 = 10
        dt = 1
        while r.successful() and r.t < t1:
            r.integrate(r.t+dt)
            print("%g %g" % (r.t, r.y))"""
        y = odeint(self.cgSolve, x, t)

        
        #print(y)
        
        return self.solution

    def g_xyt(self, ec,e_r,t):
        """This function provides a for the simulation nessesary function.
        Therefore it contains no business-logic, only simple math-operations to build the function
        
        :return: Returns the builded function.
        :rtype: function."""

        funktionPart_1 = np.dot(np.transpose(self.p_r), self.ar_vc)

        parameters = np.dot(np.transpose(self.ar_vc), self.p_r)

        funktionPart_1 = np.dot(funktionPart_1, self.gr_not_vc(np.dot(parameters, e_r), ec, t))
        functionPart_2 = np.dot(np.transpose(self.p_r), self.al_vc)

        qliJl_i = self.jl - self.v_matrix.dot(self.i_star(t))

        functionPart_2 = np.dot(functionPart_2, qliJl_i)

        return np.add(np.add(funktionPart_1,functionPart_2),self.i_r(t))


    #TODO ifs wenn irgendwas leer ist
    def gr_not_vc(self, x,ec,t):
        """This function provides a for the simulation nessesary function.
        Therefore it contains no business-logic, only simple math-operations to build the function
        
        :return: Returns the builded function.
        :rtype: function."""
        
        if not (self.ar_v).tolist() or not (self.p_c).tolist():
            parameter1 = 0
        else:
            
            parameter1= self.ar_v.transpose().dot(self.p_c)
            
            parameter1= parameter1.dot(ec)

        if not self.inzidenz_r.tolist() or not self.p_v.tolist() or not self.inzidenz_v.tolist():
            parameter3 = 0
        else:
            parameter2 = np.dot(np.transpose(self.inzidenz_r), self.p_v)
        
            parameter3 = (np.dot(parameter2, self.v_star(t)))

        f = self.g_r(np.add(np.add(x,parameter1),parameter3), t)
        return f

    def matrix(self, ec, jl_i, t):
        """This function provides a for the simulation nessesary matrix.
        Therefore it contains no business-logic, only simple math-operations to build the matrix
        
        :return: Returns the builded matrix.
        :rtype: numpy.array"""
        mc = np.array(self.matrix_mc(ec, t))
        ml = self.matrix_ml(jl_i, t)
        if not mc.tolist() :
            return ml 
        elif not ml.tolist():
            return mc
        
        mc_x = len(mc[0])
        mc_y = len(mc)
        ml_x = len(ml[0])
        ml_y = len(ml)

        zeros_1 = np.zeros((ml_x, mc_y))
        zeros_2 = np.zeros((mc_x, ml_y))

        matrix = np.array([[mc, zeros_1], [zeros_2, ml]])

        mc = np.concatenate((mc, zeros_1), axis=0)
        ml = np.concatenate((zeros_2, ml), axis= 0)
        matrix= np.concatenate((mc,ml), axis=1)

        return matrix

    def matrix_mc(self, ec, t):
        """This function provides a for the simulation nessesary matrix.
        Therefore it contains no business-logic, only simple math-operations to build the matrix
        
        :return: Returns the builded matrix.
        :rtype: numpy.array"""
        
        matrix = np.dot(np.transpose(self.p_c), self.ac_v)
        parameter = np.dot(np.transpose(self.ac_v), self.p_c)
        parameter = np.dot(parameter, ec)
        matrix = np.dot(matrix, self.ableitung_c_nachx(parameter, t))
        matrix = np.array(matrix).dot(np.transpose(self.ac_v)).dot(self.p_c)
        return matrix

    def matrix_ml(self, jl_i, t):
        """This function provides a for the simulation nessesary matrix.
        Therefore it contains no business-logic, only simple math-operations to build the matrix
        
        :return: Returns the builded matrix.
        :rtype: numpy.array"""

        v_matrix = self.v_matrix

        qliJl_i = self.jl - v_matrix.dot(self.i_star(t))

        matrix = self.w_matrix.transpose().dot(self.ableitung_l_nachx(qliJl_i, t)).dot(self.w_matrix)

        return matrix

    def function(self, ec, jl_i, e_r, t):
        """This function provides a for the simulation nessesary function.
        Therefore it contains no business-logic, only simple math-operations to build the function
        
        :return: Returns the builded function.
        :rtype: function."""
        
        function1 = -self.function1(ec, jl_i, e_r, t)
        function2 = -self.function2(ec, jl_i, e_r, t)
        
        if not function1.tolist():
            
            return function2
        elif not function2.tolist():
            return function1
        function = np.array([function1, function2])
        #function = function.transpose()

        return function

    def function1(self, ec, jl_i, e_r, t):
        """This function provides a for the simulation nessesary function.
        Therefore it contains no business-logic, only simple math-operations to build the function
        
        :return: Returns the builded function.
        :rtype: function."""
        summand1 = self.p_c.transpose().dot(self.ac_v)
        parameter = np.transpose(self.ac_v).dot(self.p_c).dot(ec)
        summand1 = summand1.dot(self.ableitung_c_nacht(parameter, t))
        
        qliJl_i = self.jl - self.v_matrix.dot(self.i_star(t))
        summand2 = self.p_c.transpose().dot(self.al_v).dot(qliJl_i)

        parameter2 = self.ar_vc.transpose().dot(self.p_r).dot(e_r)
        #TODO das np.array wegnehmen
        summand3 = self.p_c.transpose().dot(self.ar_v).dot(self.gr_not_vc(parameter2, np.array(ec), t))

        summand4 = self.i_c(t)

        function1 = np.add(summand1, np.add(summand2, np.add(summand3, summand4)))
        return function1

    def function2(self, ec, jl_i, e_r, t):
        """This function provides a for the simulation nessesary function.
        Therefore it contains no business-logic, only simple math-operations to build the function
        
        :return: Returns the builded function.
        :rtype: function."""
       
        qliJl_i = self.jl - self.v_matrix.dot(self.i_star(t))
        
        minuend1 = np.transpose(self.w_matrix).dot(self.ableitung_l_nacht(qliJl_i, t))
        minuend2 = np.transpose(self.w_matrix).dot(np.transpose(self.al_v)).dot(self.p_c).dot(ec)
        minuend3 = np.transpose(self.w_matrix).dot(np.transpose(self.al_vc)).dot(self.p_r).dot(e_r)
        minuend4 = self.v_l(t)

        function2 = np.subtract(minuend1, np.subtract(minuend2, np.subtract(minuend3, minuend4)))
        return function2

    def ableitung_c_nachx(self, ec, t):
        #TODO fertig implementieren
        return [[ec[0], 0], [0, ec[1]]]

    def ableitung_c_nacht(self, ec, t):
        #TODO implementieren Jakpbo MAtrix ( also eignitlich nur die Ableitungen auf den Diagonalen)
        return ec

    def ableitung_l_nachx(self, x, t):
        #TODO fertig implementieren
        return [[x]]

    def ableitung_l_nacht(self, x, t):
        #TODO fertig implementieren
        return x

    def v_star(self,t):
        """This function provides a for the simulation nessesary function.
        It is a modifed other function, which the user selected
        Therefore it contains no business-logic, only simple math-operations to build the function
        
        :return: Returns the builded function.
        :rtype: function."""

        if not (self.inzidenz_v):
            return 0

        matrixA = np.dot(np.transpose(self.inzidenz_v), self.p_v)
        ergebnis = linalgSolver.cg(matrixA,self.v_t(t))
        return ergebnis   

    def v_t(self, t):
        #TODO implementieren
        return t

    def i_star(self, t):
        """This function provides a for the simulation nessesary function.
        It is a modifed other function, which the user selected
        Therefore it contains no business-logic, only simple math-operations to build the function
        
        :return: Returns the builded function.
        :rtype: function."""
        #TODO

        matrixA = np.dot(self.al_vcr,self.v_matrix)

        vektorB = np.dot(np.dot(self.ai_vcr,-1), self.i_s(t))
        ergebnis = linalgSolver.cg(matrixA,vektorB)

        return ergebnis[0]
   
    def i_c(self, t):
        """This function provides a for the simulation nessesary function.
        It is a modifed other function, which the user selected
        Therefore it contains no business-logic, only simple math-operations to build the function
        
        :return: Returns the builded function.
        :rtype: function."""
         #TODO fertig implementieren. VL wird berechnet aus anderen sachen !!!!
        summand1 = self.p_c.transpose().dot(self.ai_v).dot(self.i_s(t))
        summand2 = self.p_c.transpose().dot(self.al_v).dot(self.v_matrix).dot(self.i_star(t))
        function = np.add(summand1, summand2)
        return function

    def i_s(self,t):
        #TODO
        return [t]
    
    def i_r(self,t):
        """This function provides a for the simulation nessesary function.
        It is a modifed other function, which the user selected
        Therefore it contains no business-logic, only simple math-operations to build the function
        
        :return: Returns the builded function.
        :rtype: function."""
         #TODO fertig implementieren. VL wird berechnet aus anderen sachen !!!!
        print()
        
        summand1 = self.p_r.transpose().dot(self.ai_vc).dot(self.i_s(t))
        summand2 = self.p_r.transpose().dot(self.al_vc).dot(self.v_matrix).dot(self.i_star(t))
        ergebnis = np.add(summand1,summand2)
        return ergebnis

    def v_l(self, t):
        #TODO fertig implementieren. VL wird berechnet aus anderen sachen !!!!
        ergebnis = -self.w_matrix.transpose().dot(self.inzidenz_l.transpose()).dot(self.p_v).dot(self.v_star(t))
        return ergebnis

    #TODO mit anderen Solver auf Zeit vergleichen und austauschbar in eine Methode packen
    def e_l(self, e_c, e_r, t):
        """Calculates the e_l value (value of decoupled potenzials) based on e_c and e_r
        
        :param e_c: calculated e_c value from the simulation
        :param e_r: calculated e_r value from the simulation
        :return: Returns calculated e_l value.
        :rtype: vector."""

        m = self.v_matrix.transpose().dot(self.al_vcr.transpose())
        minuend1 = self.v_matrix.transpose().dot(self.ableitung_l_nacht(self.w_matrix, t))
        minuend2 = m.dot(self.al_v.transpose()).dot(self.p_c).dot(e_c)
        minuend3 = m.dot(self.al_vc.transpose()).dot(self.p_r).dot(e_r)
        minuend4 = m.dot(self.inzidenz_l.transpose()).dot(self.p_v).dot(self.v_star(t))

        if 0 in minuend1.shape and not 0 in minuend2.shape:
            b = minuend2
        elif 0 in minuend2.shape and not 0 in minuend1.shape:
            b = minuend1
        elif 0 in minuend1.shape and 0 in minuend2.shape:
            b = []
        else:
            b = np.subtract(minuend1, minuend2)
        if not 0 in minuend3.shape:    
            b = np.subtract(b, minuend3)
        if not 0 in minuend4.shape:
            b = np.subtract(b, minuend4)

        e_l = linalgSolver.cg(m,b)[0]

        return e_l

    #TODO ungeklärt
    def startwertEntkopplung(self, e, t):
        e = np.array(e)

        #e_v bestimmen
        if not 0 in self.p_v.shape:
            m = self.q_v
            
            b = np.subtract(e, self.p_v.dot(self.v_star(t)))

            self.e_v = linalgSolver.cg(m,b)[0]
        else:
            m = self.q_v
            self.e_v = linalgSolver.cg(m,e)[0]

        #ec und e_c bestimmen

        m = np.concatenate((self.p_c, self.q_c), axis= 1)
        temp = LA.solve(m,self.e_v)
        self.ec = []
        self.e_c = []
        for i in range(len(temp)):
            if i<self.p_c.shape[1]:
                self.ec.append(temp[i])
            else:
                self.e_c.append(temp[i])

        #er und el bestimmen 
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
        
        if type(ec) is np.float64:
            ec = [ec]
            
        if type(er) is np.float64:
            er = [er]

        summand1 = self.p_v.dot(self.v_star(t))
        if 0 in summand1.shape:
            summand1 = 0
        summand2 = self.q_v.dot(self.p_c).dot(ec)
        if 0 in summand2.shape:
            summand2 = 0
        summand3 = self.q_v.dot(self.q_c).dot(self.p_r).dot(er)
        if 0 in summand3.shape:
            summand3 = 0
        summand4 = self.q_v.dot(self.q_c).dot(self.q_r).dot(self.e_l(ec,er,t))
        if 0 in summand4.shape:
            summand4 = 0

        e = summand1 + summand2 + summand3 + summand4
        print(e)
        return e

    def isMasse(self, inzidenz):
        if(len(inzidenz) == 0):
            return False
        unique, count = np.unique(inzidenz, return_counts=True)

        #Gibt nur noch zwei Potenziale und der Knoten liegt nur an einem an, weil andere Masse
        if(len(count) == 1):
            #print("nur ein spezialfall")
            return True
        if(count[0] == count[2]):
            #print("False")
            return False
        else:
            #print("True")
            return True

    def findeZusammenhangskomponente(self, inzidenzMatrix):

        if not inzidenzMatrix.tolist():
            potenzialListe = list(range(self.schaltung.potenzialNumber-1))
        else:
            potenzialListe = list(range(inzidenzMatrix.shape[1]))
        
        zusammenhangskomponenteListe = []
        while len(potenzialListe) > 0:

            potenzialListe, c_x = self.deepSearchComponent(potenzialListe, potenzialListe[0], inzidenzMatrix, 0)
            zusammenhangskomponenteListe.append(c_x)

        print("ZusammenhangskomponentenListe:")
        print(zusammenhangskomponenteListe)
        return zusammenhangskomponenteListe

    def deepSearchComponent(self, notVisitedPotenziale, potenzial, inzidenzMatrix, zusammenhangskomponente):
        if len(notVisitedPotenziale) == 0:
            print("abbruch")
            return notVisitedPotenziale, zusammenhangskomponente
        zusammenhangskomponente += 1
        notVisitedPotenziale.remove(potenzial)

        for element in inzidenzMatrix:

            if element[potenzial] != 0:

                if element[potenzial] * -1 in element.tolist():
                    outputPotenzial = element.tolist().index(element[potenzial] * -1)

                    if outputPotenzial in notVisitedPotenziale:

                        notVisitedPotenziale, zusammenhangskomponente = self.deepSearchComponent(notVisitedPotenziale, outputPotenzial, inzidenzMatrix, zusammenhangskomponente)
            
        return notVisitedPotenziale, zusammenhangskomponente
        
    def createQArray(self, c_x, isMasse):
        print("Berechnung Q-Array:")
        
        if(isMasse):
            if(len(c_x) == 1 and c_x[0] == 1):
                print([])
                return np.array([])
            #qArray = np.zeros((sum(c_x), self.schaltung.potenzialNumber-1))
            qArray = np.zeros((sum(c_x), len(c_x) + 1))
            
        else:
            #eigentlich - 2
            #qArray = np.zeros((sum(c_x), self.schaltung.potenzialNumber-2))
            qArray = np.zeros((sum(c_x), len(c_x)))
        
        #Fülle die Q-Matrix
        zeile = 0
        for x in range(0, len(c_x)):
            for i in range (0,c_x[x]):
                qArray[zeile][x] = 1
                zeile += 1
        print("Q-Array:")
        print(qArray)
        return qArray
    
    def createPArray(self, c_x, isMasse):
        
        #Bestimmme Groesse:
        rows = 0
        columns = 0
        for x in c_x:
            columns = columns + x-1
        

        c_x1 = [value-1 for value in c_x]
        for x in c_x1:
            rows += x + 1
        if isMasse:
            rows += 1
            columns = columns + 1

        #Erstelle Array entsprechend der Größe
        dimension = (rows, columns)
        pArray = np.zeros(dimension)

        spalte = 0
        zeile = 0

        #Befülle Array
        for x in c_x1:

            i = x
            while i > 0:
                pArray[zeile][spalte] = 1
                i = i -1
                spalte+= 1
                zeile += 1

            zeile += 1


        #Wenn einer der Componenten an der Masse anliegt, muss die Matrix noch erweitert werden
        if(isMasse):
            if(len(c_x) == 1 and c_x[0] == 1):
                print([1])
                return np.array([1])
            pArray[len(pArray)-1][len(pArray[0])-1] = 1
                
        print("P-Array:")
        print(pArray)
        return pArray

    def cgSolve(self, x, t):

        ec = []
        j_li = []
        for i in range(len(x)):
            if i<len(self.ec):
                ec.append(x[i])
            else:
                j_li.append(x[i])        
        m = self.matrix(ec, j_li, t)
        #print("M:", m.tolist())
        e_r = self.newton(ec, t)
        b = self.function(ec, j_li , e_r , t)
        x = linalgSolver.cg(m,b)
        print("new x:", x)
        x = x[0]
        #input()
        #e = np.array(LA.solve(m,b))[0]
        #print("Ergebnis der Simulation:", x)
        #self.solution.append([x, self.er, t])
        e = self.zurueckcoppler(x[0], e_r, t)
        
        self.solution.append(([e], t))
        #TODO hier fix für zweiten Parameter, wenn einer leer ist
        return [x, 0]

    def newton(self,ec, t):
        
        f = lambda e_r: self.g_xyt(ec,e_r,t)
        #print("Hiiii", optimize.newton(f, self.e_r,tol=1e-10, maxiter=50000, full_output=True))
        self.er = optimize.newton(f, self.er,tol=1e-10, maxiter=50000, disp=False)
        return self.er
        
