#PyTA: Transient absorption acquisition software written in pure python
The following is a description of the layout, structure, and functionality of the PyTA acquisition software. Please read this short documentation to familiarize yourself with how the code is running.

In order to keep the code general for any future TA setup. Avoid deleting or editing large blocks of code (unless a bug is found). Adding another function to the code will in almost all cases allow for specific changes to be made while retaining compatiblity on other setups with the same codebase.

## Version 0.1
Matt Menke, October 2016

### Hardware
- Stresing camera and control box
- Thorlabs 300mm delay stage
- Pink laser

### Software
-  Windows 32 bit
-  Python 3.5
-  Spyder IDE
-  Qt Creator

### Main files
- TA.py (TA1.py, etc.)
- ta_gui_class.py
- update_ta_gui_class_file.py
- ta_data_processing_class.py
- sweep_processing_class.py
- ESLSCDLL_wrapper.py
- delay_class.py
- PyAPT (PyAPT.py, APT.dll, APT.lib)

### Graphical User Interface
The graphical user interface (GUI) was developed in Qt Creator. If adding a new object to the GUI ensure to give it a practical name beyond the default. Note that objects in the diagnostics tab should be preceeded with a "d_" to distinguish between objects which would appear on both the acquisition and diagnostics tabs.

Signals and slots do not need to be updated through this program. Connections to objects will be handled within the main body of the progam (TA.py)

After an update has been made to the TA_GUI project, the ta_gui_class.py file needs to be updated. This file is automatically generated by running the update_ta_gui_class_file.py script directly from Spyder

### The TA Editor Class
This is the main file which connects the objects in the GUI to the functions which perform the TA acquisition and initial data analsysis and saving. At a basic level, the software is importing the ta_gui_class that is autogenerated (see above section) and linking this with a new application window. It does this by subclassing the ta_gui_class. The main result is that variables and objects preceded with "self." will be wholly consistent within the application and objects preceeded by "self.ui." are those which can be found in the GUI.

#### Section 1: Signals
This is where the connections to the objects in the GUI are made. Depending of the type of object in the GUI, it will emit a signal when something occurs (button pressed, value changed, etc). When a signal is emitted the connected function will execute.

#### Section 2: Initialization
When the GUI first loads there are two options: (1) Load from default values and (2) Load from values save when the last instance of the program was exited. If the file last_instance_values.txt is present in the folder, these values will be loaded instead of the default values.

Note that if this section of code is edited ensure that the correct order of the values loaded from the .txt file is maintained. In future versions a more robust method to load initialization values could be implemented.

#### Section 3: Connected Functions
These are the functions which are called from the signal connections described in Section 1. In many instances, these simple functions serve to take a value from an object within "self.ui." and place it within "self." by moving the value up a level it can be set from different parts of the GUI or during a function call and remain consistent across future function calls. Any variable which may be used from more than one place in the GUI should be treated in this manner.

#### Section 4: Plots
This section contains the functions for initializing and plotting data within the various tabs in the GUI. The module pyqtgraph (pg) has been used for plotting as other plotting modules (e.g. matplotlib) are intended for publicatino quality figures and can be prone to membory leaks. Pyqtgraph is a less polished module in terms of functionality but plots faster and more reliably.

#### Section 5: Messages
These functions are for pop messages which can be used to alert the user of certain events. In future versions these messages can also be merged with functions which open and close shutters automatically. In such a realisation, creating a tab with manual control of the shutters should also be implemented (potentially drawn over a schematic of the system)

#### Section 6: Runtime Functions
This section contains the functions which launch the program into any data acquistion mode (run, test run, diagnostics, etc.). Some of the functions called can be found in the same section. Others will be found in either sweep_processing_class.py or ta_data_processing_class.py. This is because each sweep is subclassed and each data acquistion is subclassed. This allows for relevant methods to be grouped rationally.

At various points you will see a line "QtGui.QApplication.processEvents()". I added this because it allows for the requested events (function calls) to catch up before proceeding. This ensures some degree of stability (i.e. variables are not requested before they are stored) but I think it is not the ideal way of handling these. Future versions might consider employing dedicated Qthreads to properly handle event execution.

#### Section 7: Main
This is the main function of the program. It simply exists to load the Editor class into the window and close the program when exit is called. No edits should be required here unless if loading the last instance values is decided to be handled differently.

### The TA Data Processing Class
This class takes in what is directly output from the camera acquire function. Any function which will manipulate the data should be implemented here. For this version, I have included the data processing steps that can be found the in the TA data processing subvi in Labview.

### The Sweep Processing Class
The sweep processing class handles all the data from the current sweep (current_data) as well as the average data from all sweeps (average_data). This allows for easy saving of data throughout the measurement.

### Communicating with the Stresing Camera
Communicating with the Stresing camera is accomplished by wrapping the ESLSCDLL.dll in Python using the ctypes module. I have wrapped most of the functions according to their descriptions found in the drivers supplied from Stresing and these should never be edited unless there are exceptional circumstances. The top functions call these dll functions in the same order as found in the Stresing acquistion subvis (ReadFFLoop.vi, etc). These might be able to be optimised for speed when reading from the camera. Changing the init values should allow for any camera control box from Stresing to be read with this wrapper (though perhaps not 64bit?)

### Communicating with Delays
The delay class is where all functions which deal with time delays should be placed. Of importance is that the names and inputs of the functions should be self consistent so they can be used in the runtime functions with as few of differences as possible (i.e. it should always have a move_to, check_times, check_time)

#### Delay Stage
In this initial version a thorlabs 300mm delay stage is used to create time delays up to 2ns. Controlling the stage is managed with the PyAPT module which I found on GitHub. To use this module the PyAPT.py, .dll, and lib files should remain in the current folder. 

Connecting to another brand of delay stage will require an additional class. Note that it can be simply added to this file and selected from the GUI rather than overwriting.

#### Pink Laser
Setting a delay for the pink laser is done by sending a command over gpib to a digital delay generator. These commands were also copied from the corresponding labview subvis written previously.
