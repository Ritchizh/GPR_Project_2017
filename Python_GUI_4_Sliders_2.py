"""
Created on Fri Mar 24 12:44:18 2017

@authors: Andrea & Margarita
"""
import  serial
from    numpy   import append
from    tkinter import Scale,Button, VERTICAL, Tk, Menu, messagebox, Label, TclError
from    PIL     import ImageTk
from    struct  import pack

import  Calc_DAC_with_Predistortion as dac # Functions available: W_form_triang //
                            #W_form_rectang() // W_form_sawtooth() // Predistort()

#-------------------------------------------------------------------------------------------
# Configure the Serial port:
# change COM number according to your PC connection!
ser = serial.Serial("COM20", baudrate=9600, bytesize=8, parity='N',
                    stopbits=1, timeout=None, rtscts=1)

# DEFAULT SIGNAL PARAMETERS:
# (F_max should be changed for the new RF-chain with the voltage amplifier)
num_values  = 200       # must be even
F_min_df    = 1216.7    # Minimum frequency of the radar signal [MHz]  # 0.0 V <-> 1216.7 MHz
F_max_df    = 2902.5    # Maximum frequency of the radar signal [MHz]  # 3.3 V <-> 1439.3 MHz, 25.0 V <-> 2902.5 MHz
T_df        = 20        # Period of the signal in [ms]
W_form_df   = 1         # 1 - triangular, 2 - rectangular, 3 - sawtooth waveforms, (4 - no transmission)

#------------------------------------------------------------------------------------------

# Create a MAIN WINDOW named "master":
master = Tk()  

# Set geometry and title of the main window:           
master.geometry ('1100x400+200+100') # Size of the window(x,y) + position on screen (x,y)
master.minsize(width=1000, height=300)
master.title('GPR Control Panel')
try:
    master.iconbitmap("gpr_icon.ico") # Icon of the window
    
except TclError:
    print ('No ico file found')
    
# Load the logo image:
logo = ImageTk.PhotoImage(file="GPR_logo.gif")

# Add presentation text:
WelcomeImm = Label(master, image=logo).pack(side="right", expand=1) # Place the logo image
explanation =  "GPR tool to set radar signal parameters:\n Frequency range (Fmin, Fmax) and Period (T) of the Waveform\n"
WelcomeText = Label(master, 
           font=("Baskerville Old Face", "10", "bold"),foreground = 'blue',
           text=explanation).pack(side="top")

# Function "HelpBox" to show info about the program:
def helpBox():
     messagebox.showinfo(title= "Help", message="To change the frequency range set Fmin[MHz] value with the first slider "
                         "and Fmax[MHz] value with the second slider. Set the period T[ms] of the waveform with the third slider, "
                                  "set the desired waveform with the fourth slider:\n\n\
     1. Set the desired values of the four sliders\n\n\
     2. Press confirm button to send the new instruction to\n         the microcontroller\n\n\
     3. Press stop button to stop the GPR")
     
# Function "About" to show the version of the program:
def about():
    messagebox.showinfo(title= "About", message="GpR Tools v1.0")
    
# Function to close the program:
def closeWindow():
    risposta=messagebox.askokcancel(title = "Exit", message = "Do you want to exit?")
    if risposta:
        master.destroy()   #Destroy the main window        

# Creation of the MENU:
bar_menu = Menu(master)

menu_file= Menu(bar_menu, tearoff=0)                         # tearoff=1 to get external menu
bar_menu.add_cascade (label  = "File",  menu = menu_file)    # Create One Menu
menu_file.add_command (label = "Help",  command=helpBox)     # Adding Sub-Menu//recall "helpBox" function 
menu_file.add_command (label = "About", command=about)       # Command to recall         "about" function
menu_file.add_command (label = "Exit",  command=closeWindow) # Command to recall   "closeWindow" function
master.config(menu=bar_menu) # Configuration of the Menu

#------------------------------------------------------------------------------------------

# Create SLIDER function:
def getSlider():
    if  (sldFmin.get()<sldFmax.get()):
        # Get values from sliders:
        F_min   = sldFmin.get()
        F_max   = sldFmax.get()
        T       = sldT.get()
        W_form  = sldW.get()
        
        # Calculate desired VCO frequencies:
        if W_form   == 1:
            f_desired   = dac.W_form_triang(F_min, F_max, T)
        elif W_form == 2:
            f_desired   = dac.W_form_rectang(F_min, F_max, T)
        elif W_form == 3:
            f_desired   = dac.W_form_sawtooth(F_min, F_max, T)
           
        # Calculate DAC voltage for f_desired:
        DAC_values  = dac.Predistort(f_desired)

        #!!!
        # TRANSMIT DATA TO MBED:
        dt          = T*1000/num_values  # *1000 - ms-->us, dt is time between DAC's updates
        DAC_values /= 3.3                # normalize by 3.3 V for mbed Analog Output ( - accepts 0...1)

        values_to_pack  = append(DAC_values, dt) # uniting two arrays
        str_packed      = pack('%sf' % len(values_to_pack), *values_to_pack) # pack each value into a float - 4 bytes
        num_bytes       = ser.write(str_packed) # Sending data to Mbed through Serial
   
        # Warning if F_min < F_max:
    else:
        messagebox.showinfo(title= "Warning", message="Minimum frequency value (Fmin) cannot be higher than maximum frequency "
        "value (Fmax), please adjust the frequency border")

        
# Create no-transmission function:      
def stopGPR():
    F_min   = F_min_df # Using default values
    T       = T_df

    # Calculate desired VCO frequencies:
    f_desired   = dac.W_form_no(F_min)      
    # Calculate DAC voltage for f_desired:
    DAC_values  = dac.Predistort(f_desired)
    #!!!
    # TRANSMIT DATA TO MBED:
    dt              = T*1000/num_values  # *1000 - ms-->us, dt is time between DAC's updates
    DAC_values      /= 3.3               # normalize by 3.3 V for mbed Analog Output ( - accepts 0...1)
    values_to_pack  = append(DAC_values, dt)
    str_packed      = pack('%sf' % len(values_to_pack), *values_to_pack) # pack each value into a float - 4 bytes
    num_bytes       = ser.write(str_packed) # Sending data to Mbed through Serial

# CONFIRMATION BUTTON to get the Sliders values and send them to Mbed:
getB = Button(master, text ="Confirm and send to Microcontroller", command = getSlider)  
getB.pack(side = "bottom", expand = 1, fill = "none")  #Place at the bottom of the window
getB.configure(font=("Baskerville Old Face", "10", "bold"), foreground = 'blue')

# Stop button:
stopB = Button(master, text ="Stop", command = stopGPR)
stopB.pack(side = "bottom", expand = 1, fill = "none")
stopB.configure(font=("Adobe Hebrew", "9", "bold"))

#------------------------------------------------------------------------------------------

# Create four SLIDERS to set Fmin, Fmax, T  and Waveform:
# 'tickinterval' - desplayed slider steps, 'resolution' - actual slider steps

# F_min Slider
sldFmin = Scale(master, from_=F_min_df, to=F_max_df, orient=VERTICAL, length =300, width=20, sliderlength=50, tickinterval=20,resolution=5 )
sldFmin.set(0)
sldFmin.pack(side = "left", expand = 1) # side = "left" to place all sliders in the same row

freqmin = "Fmin\n[MHz]"
label1 = Label(text=freqmin, font=("Adobe Hebrew", "10", "bold")) # Insert Label Fmin near its slider
label1.pack(side="left")

# F_max Slider
sldFmax = Scale(master, from_=F_min_df, to=F_max_df, orient=VERTICAL, length =300, width=20, sliderlength=50,tickinterval=20,resolution=5)
sldFmax.set(F_max_df)
sldFmax.pack(side = "left", expand = 1)

freqmax = "Fmax\n[MHz]"
label2 = Label(text=freqmax, font=("Adobe Hebrew", "10", "bold"))
label2.pack(side="left")

# T Slider
sldT= Scale(master, from_=10, to=100, orient=VERTICAL, length =300, width=20, sliderlength=50,tickinterval=10,resolution=10)
sldT.set(0)
sldT.pack(side = "left", expand = 1)

period = "Period\nT[ms]"
label3 = Label(text=period,  font=("Adobe Hebrew", "10", "bold"))
label3.pack(side="left", expand = 1)

# W_form Slider
sldW= Scale(master, from_=1, to=3, orient=VERTICAL, length =300, width=20, sliderlength=50,tickinterval=1,resolution=1)
sldW.set(0)
sldW.pack(side = "left", expand = 1)

wave = "Waveform:\n\n1=triangular,\n\n2=rectangular,\n\n3=sawtooth"
label4 = Label(text=wave,  font=("Adobe Hebrew", "10", "bold"))
label4.pack(side="left", expand = 1)

#------------------------------------------------------------------------------------------

# Start the Main loop:
master.mainloop()
