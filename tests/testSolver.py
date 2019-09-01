import unittest
import sys
sys.path.insert(0, '../src/')
import controler as controler
import createP_Q_Matrix as cpq
import netlistHandler as nt
import solver


import numpy as np

class SolverTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_zusammenhangskomponenteEmpty(self):
        m = np.zeros((0,4))
        cx = cpq.findConnectedComponents(m, 4)

        expected_cx = [1,1,1,1]

        self.assertEqual(cx, expected_cx)

    def test_zusammenhangskomponenteConnected(self):
        m = [[0,0], [1,1], [-1, -1], [0,0]]
        m = np.array(m).transpose()
        cx = cpq.findConnectedComponents(m, 4)

        expected_cx = [1,2,1]

        self.assertEqual(cx, expected_cx)

    def test_zusammenhangskomponenteNotConnected(self):
        m = [[1,0], [-1,0], [0, 1], [0,-1]]
        m = np.array(m).transpose()
        cx = cpq.findConnectedComponents(m, 4)

        expected_cx = [2,2]

        self.assertEqual(cx, expected_cx)

    def testQ_Array(self):
        cx = [1,1,1,1]
        isMasse = False

        q = cpq.createQArray(cx, isMasse)
        expected_q = np.array([[1, 0, 0, 0], [0,1,0,0], [0,0,1,0], [0,0,0,1]])

        self.assertTrue(np.array_equal(q,expected_q))

    def testQ_Array2(self):
        cx = [3]
        isMasse = False

        q = cpq.createQArray(cx, isMasse)
        expected_q = np.array([[1], [1], [1]])

        self.assertTrue(np.array_equal(q,expected_q))

    def testQ_Array3(self):
        cx = [3,1]
        isMasse = True

        q = cpq.createQArray(cx, isMasse)
        expected_q = np.array([[1,0], [1,0], [1,0], [0,1]])

        self.assertTrue(np.array_equal(q,expected_q))

    def testP_Array(self):
        cx = [1,1,1,1]
        isMasse = False

        p = cpq.createPArray(cx, isMasse)
        expected_p = np.zeros((4,0))

        self.assertTrue(np.array_equal(p,expected_p))

    def testP_Array2(self):
        cx = [3]
        isMasse = False

        p = cpq.createPArray(cx, isMasse)
        expected_p = np.array([[1, 0], [0, 1], [0, 0]])

        self.assertTrue(np.array_equal(p,expected_p))

    def testP_Array3(self):
        cx = [3,1]
        isMasse = True

        p = cpq.createPArray(cx, isMasse)
        expected_p = np.array([[1,0], [0,1], [0,0], [0,0]])

        self.assertTrue(np.array_equal(p,expected_p))

    def testIsMasse(self):
        m = np.array([[1,0], [-1,0], [0, 1], [0,-1]])
        isMasse = cpq.isMasse(m)
        self.assertFalse(isMasse)

    def testIsMasse2(self):
        m = np.array([[1,0], [0,0], [0, 1], [0,-1]])
        isMasse = cpq.isMasse(m)
        self.assertTrue(isMasse)

    def testFunctionGr_not_vc(self):

        netHandler = nt.NetListHandler()

        input_data = netHandler.readFile("Test-Schaltung.txt")
        schaltung = nt.Schaltung(input_data)
        schaltung.initInzidenzMatritzen()

        solv = solver.Solver(schaltung)
        solv.createInzidenzMatrices()
        solv.startwertEntkopplung(solv.potencialList, 0)

        gr_not_vc = solv.gr_not_vc([0,0], [0], 0)

        expected_gr_not_vc = [1.14,1.14]

        self.assertAlmostEqual(gr_not_vc[0], expected_gr_not_vc[0], places=15, msg=None, delta=None)
        
        self.assertAlmostEqual(gr_not_vc[1], expected_gr_not_vc[1], places=15, msg=None, delta=None)

    def testFunctionGXT(self):

        netHandler = nt.NetListHandler()

        input_data = netHandler.readFile("Test-Schaltung.txt")
        schaltung = nt.Schaltung(input_data)
        schaltung.initInzidenzMatritzen()

        solv = solver.Solver(schaltung)
        solv.createInzidenzMatrices()
        solv.startwertEntkopplung(solv.potencialList, 0)

        gxt = solv.g_xyt([0], [0,0], 0)

        expected_gxt = [-3.86, 0]

        self.assertAlmostEqual(gxt[0], expected_gxt[0], places=15, msg=None, delta=None)
        self.assertAlmostEqual(gxt[1], expected_gxt[1], places=15, msg=None, delta=None)

    def testMatrixMc(self):

        netHandler = nt.NetListHandler()

        input_data = netHandler.readFile("Test-Schaltung.txt")
        schaltung = nt.Schaltung(input_data)
        schaltung.initInzidenzMatritzen()

        solv = solver.Solver(schaltung)
        solv.createInzidenzMatrices()
        solv.startwertEntkopplung(solv.potencialList, 0)

        mc = solv.matrix_mc([-280], 1)

        expected_mc = [[2.86]]

        self.assertAlmostEqual(mc[0][0], expected_mc[0][0], places=15, msg=None, delta=None)

    def testFunction1(self):

        netHandler = nt.NetListHandler()

        input_data = netHandler.readFile("Test-Schaltung.txt")
        schaltung = nt.Schaltung(input_data)
        schaltung.initInzidenzMatritzen()

        solv = solver.Solver(schaltung)
        solv.createInzidenzMatrices()
        solv.startwertEntkopplung(solv.potencialList, 0)

        func1 = solv.function1([-90], [0], [-999, -900], 0)

        expected_func1 = [-1.14]

        self.assertAlmostEqual(func1[0], expected_func1[0], places=15, msg=None, delta=None)

    def testG_r(self):

        netHandler = nt.NetListHandler()

        input_data = netHandler.readFile("Test-Schaltung.txt")
        schaltung = nt.Schaltung(input_data)
        schaltung.initInzidenzMatritzen()

        solv = solver.Solver(schaltung)
        solv.createInzidenzMatrices()
        solv.startwertEntkopplung(solv.potencialList, 0)

        g_r = solv.g_r([-9, -900], 0)

        expected_g_r = [1.14, 1.14]

        self.assertAlmostEqual(g_r[0], expected_g_r[0], places=15, msg=None, delta=None)
        self.assertAlmostEqual(g_r[1], expected_g_r[1], places=15, msg=None, delta=None)

    # Anmerkung: Da die Ableitungen der Funktionen für jedes Element identisch aufgebaut sind, wird hier nur für ein Elemententyp
    # die Ableitungen getestet

    def testc_nachx(self):

        netHandler = nt.NetListHandler()

        input_data = netHandler.readFile("Test-Schaltung.txt")
        schaltung = nt.Schaltung(input_data)
        schaltung.initInzidenzMatritzen()

        solv = solver.Solver(schaltung)
        solv.createInzidenzMatrices()
        solv.startwertEntkopplung(solv.potencialList, 0)

        abl_c_x = solv.ableitung_c_nachx([-90, -90], 0)

        expected_abl_c_x = [[1.43, 0], [0, 1.43]]

        self.assertAlmostEqual(abl_c_x[0][0], expected_abl_c_x[0][0], places=15, msg=None, delta=None)
        self.assertAlmostEqual(abl_c_x[0][1], expected_abl_c_x[0][1], places=15, msg=None, delta=None)
        self.assertAlmostEqual(abl_c_x[1][0], expected_abl_c_x[1][0], places=15, msg=None, delta=None)
        self.assertAlmostEqual(abl_c_x[1][1], expected_abl_c_x[1][1], places=15, msg=None, delta=None)

    def testc_nacht(self):

        netHandler = nt.NetListHandler()

        input_data = netHandler.readFile("Test-Schaltung.txt")
        schaltung = nt.Schaltung(input_data)
        schaltung.initInzidenzMatritzen()

        solv = solver.Solver(schaltung)
        solv.createInzidenzMatrices()
        solv.startwertEntkopplung(solv.potencialList, 0)

        abl_c_t = solv.ableitung_c_nacht([-90, -90], 0)

        expected_abl_c_t = [0, 0]

        self.assertAlmostEqual(abl_c_t[0], expected_abl_c_t[0], places=15, msg=None, delta=None)
        self.assertAlmostEqual(abl_c_t[1], expected_abl_c_t[1], places=15, msg=None, delta=None)

    def test_istar(self):

        netHandler = nt.NetListHandler()

        input_data = netHandler.readFile("Test-Schaltung.txt")
        schaltung = nt.Schaltung(input_data)
        schaltung.initInzidenzMatritzen()

        solv = solver.Solver(schaltung)
        solv.createInzidenzMatrices()
        solv.startwertEntkopplung(solv.potencialList, 0)

        istar = solv.i_star(0)

        expected_istar = [23]

        
        self.assertAlmostEqual(istar[0], expected_istar[0], places=15, msg=None, delta=None)

    def test_ic(self):

        netHandler = nt.NetListHandler()

        input_data = netHandler.readFile("Test-Schaltung.txt")
        schaltung = nt.Schaltung(input_data)
        schaltung.initInzidenzMatritzen()

        solv = solver.Solver(schaltung)
        solv.createInzidenzMatrices()
        solv.startwertEntkopplung(solv.potencialList, 0)

        i_c = solv.i_c(0)

        expected_i_c = [0]

        self.assertAlmostEqual(i_c[0], expected_i_c[0], places=15, msg=None, delta=None)

    def test_is(self):

        netHandler = nt.NetListHandler()

        input_data = netHandler.readFile("Test-Schaltung.txt")
        schaltung = nt.Schaltung(input_data)
        schaltung.initInzidenzMatritzen()

        solv = solver.Solver(schaltung)
        solv.createInzidenzMatrices()
        solv.startwertEntkopplung(solv.potencialList, 0)

        i_s = solv.i_s(0)

        expected_i_s = [23]

        self.assertAlmostEqual(i_s[0], expected_i_s[0], places=15, msg=None, delta=None)

    def test_ir(self):

        netHandler = nt.NetListHandler()

        input_data = netHandler.readFile("Test-Schaltung.txt")
        schaltung = nt.Schaltung(input_data)
        schaltung.initInzidenzMatritzen()

        solv = solver.Solver(schaltung)
        solv.createInzidenzMatrices()
        solv.startwertEntkopplung(solv.potencialList, 0)

        i_r = solv.i_r(0)

        expected_i_r = [-23, 0]

        self.assertAlmostEqual(i_r[0], expected_i_r[0], places=15, msg=None, delta=None)
        self.assertAlmostEqual(i_r[1], expected_i_r[1], places=15, msg=None, delta=None)

    def test_startwerteEntkoppling(self):

        netHandler = nt.NetListHandler()

        input_data = netHandler.readFile("Test-Schaltung.txt")
        schaltung = nt.Schaltung(input_data)
        schaltung.initInzidenzMatritzen()

        solv = solver.Solver(schaltung)
        solv.createInzidenzMatrices()
        e_values = solv.startwertEntkopplung(solv.potencialList, 0)

        #in der Beispielschaltun gibt es keine v's und damit auch kein ev
        ec = e_values[1]
        er = e_values[2]
        el = e_values[3]

        summand1 = solv.q_v.dot(solv.p_c).dot(ec).transpose()
        summand2 = solv.q_v.dot(solv.q_c).dot(solv.p_r).dot(er)
        summand3 = solv.q_v.dot(solv.q_c).dot(solv.q_r).dot(el)

        sum = np.add(np.add(summand1,summand2),summand3)[0]

        for x in range(len(sum)):
            #self.assertAlmostEqual(sum[x], solv.potencialList[x], places=15, msg=None, delta=None)
            self.assertTrue(float(sum[x]) == float(solv.potencialList[x]))
            
    def test_zurueckKoppler(self):

        netHandler = nt.NetListHandler()

        input_data = netHandler.readFile("Test-Schaltung.txt")
        schaltung = nt.Schaltung(input_data)
        schaltung.initInzidenzMatritzen()

        solv = solver.Solver(schaltung)
        solv.createInzidenzMatrices()

        e_values = solv.startwertEntkopplung(solv.potencialList, 0)

        #in der Beispielschaltun gibt es keine v's und damit auch kein ev
        ec = e_values[1]
        er = e_values[2]
        el = e_values[3]

        e = solv.zurueckcoppler(ec, er, 0)[0]

        for x in range(len(e)):
            
            #self.assertAlmostEqual(sum[x], solv.potencialList[x], places=15, msg=None, delta=None)
            self.assertTrue(float(e[x]) == float(solv.potencialList[x]))
       
        

if __name__ == '__main__':
    unittest.main()