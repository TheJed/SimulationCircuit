"""
    This module creates the P and Q Matrices
    :copyright: (c) 2019 by Tobias Klein.
"""
import numpy as np

def findConnectedComponents(inzidenzMatrix, potenzialNumber):
    """This function calculates the connected components for a specific component group
    
    :param inzidenzMatrix: the inzidenz matrix of the component group
    :return: Returns a list with the connected components
    :rtype: list of integers."""

    if not inzidenzMatrix.tolist():
        potenzialListe = list(range(potenzialNumber))
    else:
        potenzialListe = list(range(inzidenzMatrix.shape[1]))
    
    zusammenhangskomponenteListe = []
    while len(potenzialListe) > 0:

        potenzialListe, c_x = deepSearchComponent(potenzialListe, potenzialListe[0], inzidenzMatrix, 0)
        zusammenhangskomponenteListe.append(c_x)

    return zusammenhangskomponenteListe

def deepSearchComponent(notVisitedPotencials, potencial, inzidenzMatrix, zusammenhangskomponente):
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

                    notVisitedPotencials, zusammenhangskomponente = deepSearchComponent(notVisitedPotencials, outputPotencial, inzidenzMatrix, zusammenhangskomponente)
        
    return notVisitedPotencials, zusammenhangskomponente


def createQArray(c_x, isMasse):
    """This function calculates the Q-Array for component-groups. The Q-Array is a kernel of the inzidenz matrix from the component-group 
    
    :param c_x: list of connected components
    :param isMasse: is one of the components connected to the mass-potencial
    :return: Returns the Q-Array
    :rtype: np.array."""

    if(isMasse):
        if(len(c_x) == 1 and c_x[0] == 1):
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

def createPArray(c_x, isMasse):

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

def isMasse(inzidenz):
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
    

        
