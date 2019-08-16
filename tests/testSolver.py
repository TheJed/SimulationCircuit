import unittest
import sys
sys.path.insert(0, '../src/')
import createP_Q_Matrix as cpq

import numpy as np

class SolverTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_zusammenhangskomponenteEmpty(self):
        m = np.zeros((0,4))
        cx = cpq.findConnectedComponents(m, 4)

        expected_cx = [1,1,1,1]

        self.assertEquals(cx, expected_cx)

    def test_zusammenhangskomponenteConnected(self):
        m = [[0,0], [1,1], [-1, -1], [0,0]]
        m = np.array(m).transpose()
        cx = cpq.findConnectedComponents(m, 4)

        expected_cx = [1,2,1]

        self.assertEquals(cx, expected_cx)

    def test_zusammenhangskomponenteNotConnected(self):
        m = [[1,0], [-1,0], [0, 1], [0,-1]]
        m = np.array(m).transpose()
        cx = cpq.findConnectedComponents(m, 4)

        expected_cx = [2,2]

        self.assertEquals(cx, expected_cx)

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
        print(p)
        expected_p = np.array([[1,0], [0,1], [0,0], [0,0]])

        self.assertTrue(np.array_equal(p,expected_p))

    def testIsMasse(self):
        m = np.array([[1,0], [-1,0], [0, 1], [0,-1]])
        isMasse = cpq.isMasse(m)
        self.assertFalse(isMasse)

    def testIsMasse(self):
        m = np.array([[1,0], [0,0], [0, 1], [0,-1]])
        isMasse = cpq.isMasse(m)
        self.assertTrue(isMasse)
        
        

if __name__ == '__main__':
    unittest.main()