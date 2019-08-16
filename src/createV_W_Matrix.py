"""
    This module creates the W and V Matrices
    :copyright: (c) 2019 by Tobias Klein.
"""

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import collections



def erstelleSpannbaum(matrix):
    """Creates a spanningtree for a given inzidenz-matrix
    
    :param matrix: inzidenz-matrix
    :return: edges of spanningtree
    :rtype: vector"""
    
    bauteile = [x for x in range(len(matrix[0]))]
    visitedList = []
    fertigeBauteile = []
    while len(bauteile) > 0:
        column = bauteile.pop(0)
        liste = []
        x= 0
        for row in range(len(matrix)):
            if matrix[row][column] == 1:
                liste.append(row)
                x += 1

        neuesBauteil = False
        for x in liste:
            if x not in visitedList:
                visitedList.append(x)
                neuesBauteil = True
                
        if neuesBauteil:
            fertigeBauteile.append(column)

    return fertigeBauteile

def createsVW_Matrices(u_matrix):
    """Handels the calculation of the V and W Matrix for a given inzidenz matrix

    :param u_matrix: inzidenzmatrix
    :return: V and W matrix
    :rtype: tupel of matrices"""

    #--------Add row for masspotencial--------
    k=u_matrix.sum(axis=0)
    k =  [i * -1 for i in k]

    u_matrix = np.vstack([k,u_matrix])

    matrix = np.array([elem for elem in u_matrix])

    #--------create an undirected inzidenz-matrix-------
    for row in range(len(matrix)):
        for column in range(len(matrix[0])):
            if matrix[row][column] == -1:
                matrix[row][column] = 1


    #--------Calculate spanningtree--------
    fertigeBauteile = erstelleSpannbaum(matrix)

    #--------Create inzidenz-matrix of edges from spanningtree--------
    feb = [x for x in fertigeBauteile]
    
    spanningtree = np.array(u_matrix[:, feb.pop(0)])
    if not feb:
        spanningtree = np.array(spanningtree).reshape(len(spanningtree),1)
    else:
        for element in feb:
            
            k = (np.array(u_matrix[:, element]))
           
            spanningtree = np.column_stack((spanningtree,k))
            

    #--------Transform spanningtree in list of tupels--------
    tupelList = []
    for column in range(len(spanningtree[0])):
        temp = []
        for row in range(len(spanningtree)):
            if spanningtree[row][column] == 1:
                temp = [row] + temp
            elif spanningtree[row][column] == -1:
                temp.append(row)
        tupelList.append((temp))

    #--------create list of components, which are not part of the spanningtree--------
    bauteile = [x for x in range(len(matrix[0]))]
    for x in fertigeBauteile:
         bauteile.remove(x)



    #Remove?
    for x in range(len(tupelList)):
        if len(tupelList[x]) == 1:
            tupelList.remove(tupelList[x])

 
    loopList = []
    kantenList = []

    #--------Create Loops--------
    for loop in bauteile:
        tempBauteileImLoop = [x for x in fertigeBauteile]
        tempBauteileImLoop.append(loop)
        tempTupelList = [x for x in tupelList]
        temp = []
        for row in range(len(u_matrix)):
            if u_matrix[row][loop] == 1:
                temp = [row] + temp
            elif u_matrix[row][loop] == -1:
                temp.append(row)
        tempTupelList.append(temp)

        #Remove?
        for x in range(len(tempTupelList)):
            if len(tempTupelList[x]) == 1:
                tempTupelList.remove(tempTupelList[x])
        
        if not (tempTupelList) == (tupelList):
            
            unique, counts = np.unique(tempTupelList, return_counts=True)
           
            while any(n % 2 == 1 for n in counts):
                x = reduziere(tempTupelList, unique, counts)
                tempTupelList.remove(tempTupelList[x])
                tempBauteileImLoop.remove(tempBauteileImLoop[x])
                unique, counts = np.unique(tempTupelList, return_counts=True)

            loopList.append(tempTupelList)
            kantenList.append(tempBauteileImLoop)
    w_matrix = buildWMatrix(loopList, kantenList, len(u_matrix[0]), u_matrix)
    v_matrix = buildVMatrix(fertigeBauteile, loopList)
    return v_matrix, w_matrix


def reduziere(tempTupelList, unique, counts):
    """This function reduces a graph represented by the tupellist so, that it only contains a loop and no other edges
    
    :param tempTupelList: List of tupels representaing the current edges in the graph
    :param unique: List of unique numbers in tempTupelList
    :param counts: Counts of unique numbers in tempTupelList
    :return: Reduced tempTupelList
    :rtype: List"""

    i = (counts.tolist().index(1))
    for x in range(len(tempTupelList)):
        if unique[i] in tempTupelList[x]:
            return x

    
def buildWMatrix(loopList, kantenList, numberOfKanten, u_matrix):
    """Creates the W-Matrix based on the loops

    :param loopList: List of Loops
    :param kantenList: List of edges in loops
    :parm numberOfKanten: Number of edges in graph
    :param u_matrix: Inzidenz-Matrix of graph
    :return: W-Matrix
    :rtype: Array"""

    w_matrix = []
    for x in range(len(loopList)):
        
        loopCopy = loopList[x].copy()
        loopKanten = kantenList[x].copy()
        directionDic = {loopKanten[0] : 1}

        toPotenzial = loopCopy[0][1]
        loopCopy.pop(0)
        loopKanten.pop(0)

        while len(loopCopy) > 0:

            kante = 0
            for i in range(len(loopCopy)):
                if toPotenzial in loopCopy[i]:
                    kante = i
                    break
            
            if toPotenzial == loopCopy[kante][0]:

                toPotenzial = loopCopy[kante][1]
                loopCopy.pop(kante)
                k = loopKanten.pop(kante)
                directionDic[k] = 1

            else:

                toPotenzial = loopCopy[kante][0]
                loopCopy.pop(kante)
                k = loopKanten.pop(kante)
                directionDic[k] = -1
                

        w_eintrag = []
        for kante in range(numberOfKanten):
            if kante in directionDic:
                w_eintrag.append(directionDic[kante])
            else:
                w_eintrag.append(0)
      
        w_matrix.append(w_eintrag)

    if not w_matrix.tolist():
        return np.array([[]])
    return w_matrix

def buildVMatrix(spanningtreeKanten, loops):
    """Creates the V-Matrix based on the loops

    :param spanningtreeKanten: Edges of spanningtree
    :parm loops: list of loops
    :return: V-Matrix
    :rtype: Array"""

    v_matrix = np.zeros((len(spanningtreeKanten) + len(loops), len(spanningtreeKanten)))
    for x in range(len(spanningtreeKanten)):

        v_matrix[spanningtreeKanten[x]][x] = 1

    return v_matrix




        

