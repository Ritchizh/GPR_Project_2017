import numpy as np
from   scipy import interpolate

#------------------------------------------------------------------------------------------------

# Frequency and voltage values:
N0      = 200     #  default number of values
#V_MIN   = 0.0    # V 
#V_MAX   = 25.0   # V
#F_MIN   = 1216.7 # MHz
#F_MAX   = 2902.5 # 2902.5 MHz <--> 25.0 V
pic_num = 1

#------------------------------------------------------------------------------------------------

# Data from VCO ZX95-2700A+ Documentation for t=+25 C:
V_act = np.array([0.00, 0.15, 2.00, 3.00, 4.00, 6.00, 8.00, 9.00, 10.00,
                  12.00, 14.00, 15.00, 16.00, 17.00, 18.00, 19.00, 20.00, 21.00, 23.00, 25.00])
f_act = np.array([1216.7, 1229.8, 1386.4, 1465.4, 1540.2, 1710.9, 1884.5, 1975.3,
                  2067.3, 2241.6, 2396.5, 2472.0, 2537.8, 2594.3, 2646.0, 2691.5, 2734.1, 2772.7, 2842.2, 2902.5])

# Amplifier scaling coefficient: DAC's 3.3 V are later turned into 25.0 V by the amplifier:
amp_scale    = 3.3/25.0
V_act        = V_act*amp_scale
# Interpolating actual data into a regular grid with N values:
interp_func  = interpolate.interp1d(V_act, f_act)
interp_coeff = 4 # interpolation coefficient
V_act_intr   = np.linspace(0, 25*amp_scale, N0*interp_coeff, endpoint=True)
f_act_intr   = interp_func(V_act_intr)

#------------------------------------------------------------------------------------------------
# TRIANGULAR WAVE:

def W_form_triang(f_min_tr, f_max_tr, T, N=N0):
    f_triang       = np.empty(N)
    dt             = T/N # ms
    coeff_tr       = 2*(f_max_tr - f_min_tr)/T # Triangular wave tangent
    
    # Calculate VCO output frequency values [N] for a triangular wave:
    for i in range(0, N):
        t = i*dt # Current time value
        if (0 <= t and t < T/2) :
                f_triang[i]  = (coeff_tr*t + f_min_tr) # The straight line equation
        elif (T/2 <= t and t < T) :
                f_triang[i] = (-coeff_tr*t +2*f_max_tr - f_min_tr) # The straight line equation
    return f_triang

#------------------------------------------------------------------------------------------------
# RECTANGULAR WAVE:

def W_form_rectang(f_min_rec, f_max_rec, T, N=N0):
    f_rectang      = np.empty(N)
    dt             = T/N # ms
    # Calculate VCO output frequency values [N] for a rectangular wave:
    for i in range(0, N):
        t = i*dt # Current time value
        if (0 <= t and t < T/2):
            f_rectang[i]  = f_max_rec    
        elif (T/2 <= t and t < T):
            f_rectang[i] = f_min_rec
    return f_rectang

#------------------------------------------------------------------------------------------------
# SAWTOOTH WAVE:

def W_form_sawtooth(f_min_s, f_max_s, T, N=N0):
    f_sawtooth  = np.empty(N)
    dt          = T/N # ms
    coeff_s     = (f_max_s - f_min_s)/((N - 1)*dt) # Sawtooth wave tangent
    # Calculate VCO output frequency values [N] for a sawtooth wave:
    for i in range(0, N):
        t = i*dt # Current time value
        f_sawtooth[i]  = (coeff_s*t + f_min_s)  # The straight line equation
    return f_sawtooth
        
#------------------------------------------------------------------------------------------------
# NO-TRANSMISSION:

def W_form_no(f_min_n, N=N0):
    f_no        = np.empty(N)
    # Calculate VCO output frequency values [N]:
    for i in range(0, N):
        f_no[i]  = f_min_n
    return f_no
        
#------------------------------------------------------------------------------------------------

# Function for calculation and predistortion of DAC voltages for the desired VCO output:

def find_nearest(array,value):  # Function for finding a value nearest to the given value in the array:
    idx = (np.abs(array-value)).argmin()
    return array[idx],idx # Returns the nearest value and its index

# Calculates DAC voltages required for the VCO producing f_desired,
# in accordance with the documented non-linear dependence f(V):
def Predistort(f_desired): 
    N               = len(f_desired)
    f_dac           = np.empty(N) 
    DAC_values      = np.empty(N)
    # Correlate desired freq values with the documented ("actual_interpolated") values:
    for i in range(0, N):
        f_dac[i], idx = find_nearest(f_act_intr, f_desired[i]) # find actual freq value nearest to the desired freq
        DAC_values[i] = V_act_intr[idx]
    return DAC_values
