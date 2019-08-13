import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import collections


print("############################### Begin V W Matrix Berechnung ###############################")
#u_matrix = np.array([[1,  -1, 1, 0, 0, 0], [-1, 1, 0, 0, -1, -1], [0, 0, -1, 1, 0, 1]])
u_matrix = np.array([[-1., 1.]])
#u_matrix = np.array([[-1,  1]])

def erstelleSpannbaum(matrix):
    
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
        
        #if x == 1:
        #    liste.append(len(matrix))

        neuesBauteil = False
        for x in liste:
            if x not in visitedList:
                visitedList.append(x)
                neuesBauteil = True
                #fertigeBauteile.append(column)
        if neuesBauteil:
            fertigeBauteile.append(column)

    print("visited Potenziale")
    print(visitedList)
    print("--------------------------")
    print("Bauteile des Spanningtrees")
    print(fertigeBauteile)
    print("-----------------------")
    return fertigeBauteile

def tiefensuche(u_matrix):

    #Zeile für Masseknoten hinzufügen, der mal gelöscht wurde am Anfang
    k=u_matrix.sum(axis=0)
    k =  [i * -1 for i in k]

    #Zeile zur Inzidenzmatrix hinzufügen
    #Am 1..08 weggenommen
    u_matrix = np.vstack([u_matrix,k])

    #Matrix kopieren
    matrix = np.array([elem for elem in u_matrix])

    #Erstellen einer ungerichteten Inzidenzmatrix
    for row in range(len(matrix)):
        for column in range(len(matrix[0])):
            if matrix[row][column] == -1:
                matrix[row][column] = 1

    print("undirectedMatrix:")
    print(matrix)
    print(u_matrix)

    #Berechnung des Spannungsbaums
    fertigeBauteile = erstelleSpannbaum(matrix)

    #Erstellung der Inzidenzmatritzen der Kanten des Spannungsbaums
    feb = [x for x in fertigeBauteile]
    
    spanningtree = np.array(u_matrix[:, feb.pop(0)])
    if not feb:
        #transponieren, wenn spanningtree nur aus einer einzelnen Spalte besteht
        spanningtree = np.array(spanningtree).reshape(len(spanningtree),1)
    else:
        for element in feb:
            
            k = (np.array(u_matrix[:, element]))
           
            spanningtree = np.column_stack((spanningtree,k))
            
    """k= spanningtree.sum(axis=0).tolist()
    if type(k) is list:

        k =  [i * -1 for i in k]
    else:
        k = [i * -1 for i in spanningtree]"""
    
    #Inzidenzmatritzen des Spannungsbaums
    #spanningtree = np.vstack([spanningtree,k])
    print("Spanningtree93:", spanningtree)

    #Umformung des Spannungsbaums in eine Liste aus Tupel aus Potenzialen
    tupelList = []
    for column in range(len(spanningtree[0])):
        temp = []
        for row in range(len(spanningtree)):
            if spanningtree[row][column] == 1:
                temp = [row] + temp
            elif spanningtree[row][column] == -1:
                temp.append(row)
        tupelList.append((temp))

    #print("Tupellist",tupelList)
    #Erstellung einer Liste von Bauteilen, welche nicht im Spannungsbaum sind
    bauteile = [x for x in range(len(matrix[0]))]
    for x in fertigeBauteile:
         bauteile.remove(x)

    print("Bauteile nicht im Spanningtree:",bauteile)
    #print("-------------------------------------")
    #Erstellung der Loop

    #Die, welche zum Masseknoten führen, können niemals in einer Loop sein und können daher raus
    for x in range(len(tupelList)):
        if len(tupelList[x]) == 1:
            tupelList.remove(tupelList[x])

 
    loopList = []
    kantenList = []

    for loop in bauteile:
        tempBauteileImLoop = [x for x in fertigeBauteile]
        #print("tempBauteileImLoop:", tempBauteileImLoop)
        tempBauteileImLoop.append(loop)
        tempTupelList = [x for x in tupelList]
        temp = []
        for row in range(len(u_matrix)):
            if u_matrix[row][loop] == 1:
                temp = [row] + temp
            elif u_matrix[row][loop] == -1:
                temp.append(row)
        tempTupelList.append(temp)

            #Die, welche zum Masseknoten führen, können niemals in einer Loop sein und können daher raus
        for x in range(len(tempTupelList)):
            if len(tempTupelList[x]) == 1:
                tempTupelList.remove(tempTupelList[x])
        
        #Nur Loop, wenn die einwegigen Kanten (Wegen Masse) rausgenommen wurden und die Liste nicht der des SPannungsbaums entspricht
        if not (tempTupelList) == (tupelList):
            
            unique, counts = np.unique(tempTupelList, return_counts=True)
            print("tempTupelList:", tempTupelList)
            #print("140:",np.unique(tempTupelList, return_counts=True))
            while any(n % 2 == 1 for n in counts):
                x = reduziere(tempTupelList, unique, counts)
                tempTupelList.remove(tempTupelList[x])
                tempBauteileImLoop.remove(tempBauteileImLoop[x])
                unique, counts = np.unique(tempTupelList, return_counts=True)
            #print("Ergebnis")
            #print("Kanten im Loop;", tempBauteileImLoop)
            #print("Tupelliste:", tempTupelList)
            #print("--------------")
            loopList.append(tempTupelList)
            kantenList.append(tempBauteileImLoop)
    w_matrix = buildWMatrix(loopList, kantenList, len(u_matrix[0]), u_matrix)
    v_matrix = buildVMatrix(fertigeBauteile, loopList)
    return v_matrix, w_matrix


def reduziere(tempTupelList, unique, counts):
    #print("reduziere")
    #print(tempTupelList)
    i = (counts.tolist().index(1))
    for x in range(len(tempTupelList)):
        if unique[i] in tempTupelList[x]:
            return x
            #tempTupelList.remove(tempTupelList[x])
            #break;
    #print(tempTupelList)
    #return tempTupelList
    
def buildWMatrix(loopList, kantenList, numberOfKanten, u_matrix):
    w_matrix = []
    for x in range(len(loopList)):
        
        print("Loop:", loopList[x])
        loopCopy = loopList[x].copy()
        loopKanten = kantenList[x].copy()
        directionDic = {loopKanten[0] : 1}
        #direction = 1
        #directionList = [1]
        toPotenzial = loopCopy[0][1]
        loopCopy.pop(0)
        loopKanten.pop(0)
        #print(loopCopy)        
        #print(toPotenzial)
        while len(loopCopy) > 0:
            #print("Loopkanten", loopKanten)
            #finde nächste Kante für den Loop
            kante = 0
            for i in range(len(loopCopy)):
                if toPotenzial in loopCopy[i]:
                    kante = i
                    #print("kante", kante)
                    break
            
            if toPotenzial == loopCopy[kante][0]:
                #directionList.append(1)
                toPotenzial = loopCopy[kante][1]
                loopCopy.pop(kante)
                k = loopKanten.pop(kante)
                directionDic[k] = 1

            else:
                #direction = direction * -1
                #directionList.append(-1)
                toPotenzial = loopCopy[kante][0]
                loopCopy.pop(kante)
                k = loopKanten.pop(kante)
                directionDic[k] = -1
                #print("loopCopy-Reduziert:", loopCopy)
        #print("Direction-List:", directionList)
        #print("Dic", directionDic)

        w_eintrag = []
        for kante in range(numberOfKanten):
            if kante in directionDic:
                w_eintrag.append(directionDic[kante])
            else:
                w_eintrag.append(0)
        #print(w_eintrag)
        w_matrix.append(w_eintrag)

    w_matrix = np.array(w_matrix)
    print("W-Matrix: \n", w_matrix.T)

    #TODO hier schöner machen
    if not w_matrix.tolist():
        return np.array([[]])
    return w_matrix

def buildVMatrix(spanningtreeKanten, loops):

    v_matrix = np.zeros((len(spanningtreeKanten) + len(loops), len(spanningtreeKanten)))
    for x in range(len(spanningtreeKanten)):
        print(x)
        print(spanningtreeKanten[x])
        v_matrix[spanningtreeKanten[x]][x] = 1
    print("V_Matrix:\n", v_matrix)
    return v_matrix





#tiefensuche(u_matrix)


        

