import numpy as np

#Vektor with Function and Ableitung (nach Variable und Zeit)
def r_change():
    function = lambda x, t: 40
    function_dx = lambda x, t: 40
    return np.array([function, function_dx])
        
def r_constant():
    function = lambda x, t: 40
    function_dx = lambda x, t: 40
    return np.array([function, function_dx])

def c_change():
    function = lambda x, t: 20
    function_dx = lambda x, t: 20
    function_dt = lambda x, t: 20
    return np.array([function, function_dx, function_dt])
    
def c_constant():
    function = lambda x, t: 40
    function_dx = lambda x, t: 40
    function_dt = lambda x, t: 40
    return np.array([function, function_dx, function_dt])

def l_change():
    function = lambda x, t: 20
    function_dx = lambda x, t: 20
    function_dt = lambda x, t: 20
    return np.array([function, function_dx, function_dt])

def l_constant():
    function = lambda x, t: 20
    function_dx = lambda x, t: 20
    function_dt = lambda x, t: 20
    return np.array([function, function_dx, function_dt])

def i_change():
    function = lambda x, t: 40
    function_dx = lambda x, t: 40
    return np.array([function, function_dx])
        
def i_constant():
    function = lambda x, t: 40
    function_dx = lambda x, t: 40
    return np.array([function, function_dx])

    
def v_change():
    function = lambda x, t: 40
    function_dx = lambda x, t: 40
    return np.array([function, function_dx])
        
def v_constant():
    function = lambda x, t: 40
    function_dx = lambda x, t: 40
    return np.array([function, function_dx])


