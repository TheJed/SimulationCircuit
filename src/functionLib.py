"""
    This module is a library and stores just different functions for components
    :copyright: (c) 2019 by Tobias Klein.
"""

import numpy as np
import math

#Vektor with Function and Ableitung (nach Variable und Zeit)
def r_change():
    function = lambda x, t: x + 40 +t
    function_dx = lambda x, t: 1
    return np.array([function, function_dx])
        
def r_constant():
    function = lambda x, t: 1.14
    function_dx = lambda x, t: 1.14
    return np.array([function, function_dx])

def c_change():
    function = lambda x, t: x+20 + 23*t
    function_dx = lambda x, t: 1
    function_dt = lambda x, t: 23
    return np.array([function, function_dx, function_dt])
    
def c_constant():
    function = lambda x, t: 1.43*x
    function_dx = lambda x, t: 1.43
    function_dt = lambda x, t: 0
    return np.array([function, function_dx, function_dt])

def l_change():
    function = lambda x, t: x+20 +11*t
    function_dx = lambda x, t: 1
    function_dt = lambda x, t: 20
    return np.array([function, function_dx, function_dt])

def l_constant():
    function = lambda x, t: 2.34*x + t
    function_dx = lambda x, t: 2.34
    function_dt = lambda x, t: 1
    return np.array([function, function_dx, function_dt])

def i_change():
    function = lambda t: math.sin(t) + 23
    return np.array([function])
        
def i_constant():
    function = lambda t: math.sin(t) + 23
    return np.array([function])

    
def v_change():
    function = lambda t: 40
    return np.array([function])
        
def v_constant():
    function = lambda t: 0.5*t
    return np.array([function])


