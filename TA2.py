import sys
import os
import subprocess

from PyQt5 import QtGui, QtCore, QtWidgets
from ta_gui_class import Ui_TA_GUI
import pyqtgraph as pg
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
import numpy as np

from TA2_camera import octoplus
from ta_data_processing_class import ta_data_processing
from sweep_processing_class import sweep_processing

from delay_class import esp301_delay_stage, pink_laser_delay, disco_laser_delay

class Editor(QtWidgets.QMainWindow):
    def __init__(self,lif,pl=np.zeros((50,1)),preloaded=False):        
        super(Editor, self).__init__()
        self.ui=Ui_TA_GUI()
        self.ui.setupUi(self)
        self.show()
        self.lif = lif
        
        #######################################################################
        #######################################################################
        #######################################################################
        # Section 1: Creates Connections between GUI objects in ta_gui_class.py
        # and the methods found in this class (Editor)        
        
        self.ui.folder_btn.clicked.connect(self.exec_folder_btn)
        self.ui.filename.textChanged.connect(self.exec_file_changed)
        self.ui.metadata_pump_wave.textChanged.connect(self.metadata_changed)
        self.ui.metadata_pump_power.textChanged.connect(self.metadata_changed)
        self.ui.metadata_pump_size.textChanged.connect(self.metadata_changed)
        self.ui.metadata_probe_wave.textChanged.connect(self.metadata_changed)
        self.ui.metadata_probe_power.textChanged.connect(self.metadata_changed)
        self.ui.metadata_probe_size.textChanged.connect(self.metadata_changed)        
        
        self.ui.timefile_folder_btn.clicked.connect(self.exec_timefile_folder_btn)
        self.ui.timefile_list.activated.connect(self.update_timefile)
        self.ui.timefile_edit_btn.clicked.connect(self.exec_timefile_edit_btn)
        self.ui.timefile_new_blank_btn.clicked.connect(self.exec_timefile_new_blank_btn)
        self.ui.timefile_new_params_btn.clicked.connect(self.exec_timefile_new_params_btn)
        
        self.ui.short_t0.valueChanged.connect(self.update_short_t0)
        self.ui.long_t0.valueChanged.connect(self.update_long_t0)
        self.ui.disco_t0.valueChanged.connect(self.update_disco_t0)
        self.ui.num_shots.valueChanged.connect(self.update_num_shots)  
        self.ui.num_sweeps.valueChanged.connect(self.update_num_sweeps)
        self.ui.delay_type_list.currentIndexChanged.connect(self.update_delay_type)
        self.ui.delay_type_list.addItem('Short')
        self.ui.delay_type_list.addItem('Long')
        self.ui.delay_type_list.addItem('Disco')
        
        self.ui.use_calib.toggled.connect(self.update_use_calib)
        self.ui.calib_pixel_low.valueChanged.connect(self.update_calib)
        self.ui.calib_pixel_high.valueChanged.connect(self.update_calib)
        self.ui.calib_wave_low.valueChanged.connect(self.update_calib)
        self.ui.calib_wave_high.valueChanged.connect(self.update_calib)
        
        self.ui.use_cutoff.toggled.connect(self.update_use_cutoff)
        self.ui.cutoff_pixel_low.valueChanged.connect(self.update_cutoff)
        self.ui.cutoff_pixel_high.valueChanged.connect(self.update_cutoff)
        
        self.ui.run_btn.clicked.connect(self.exec_run_btn)
        self.ui.stop_btn.clicked.connect(self.exec_stop_btn)
        self.ui.pause_btn.clicked.connect(self.exec_pause_btn)
        self.ui.exit_btn.clicked.connect(self.exec_exit_btn)
        
        self.ui.kinetic_pixel.valueChanged.connect(self.update_kinetic_pixel)
        self.ui.spectra_timestep.valueChanged.connect(self.update_spectra_timestep)
        self.ui.plot_log_t.toggled.connect(self.update_plot_log_t)
        self.ui.plot_timescale.toggled.connect(self.update_plot_timescale)
        
        self.ui.d_refman_vertrical_stretch.valueChanged.connect(self.update_refman)
        self.ui.d_refman_vertical_offset.valueChanged.connect(self.update_refman)
        self.ui.d_refman_horiz_offset.valueChanged.connect(self.update_refman)
        self.ui.d_refman_scale_center.valueChanged.connect(self.update_refman)
        self.ui.d_refman_scale_factor.valueChanged.connect(self.update_refman)
        
        self.ui.d_use_calib.toggled.connect(self.update_d_use_calib)
        self.ui.d_calib_pixel_low.valueChanged.connect(self.update_d_calib)
        self.ui.d_calib_pixel_high.valueChanged.connect(self.update_d_calib)
        self.ui.d_calib_wave_low.valueChanged.connect(self.update_d_calib)
        self.ui.d_calib_wave_high.valueChanged.connect(self.update_d_calib)
        
        self.ui.d_use_cutoff.toggled.connect(self.update_d_use_cutoff)
        self.ui.d_cutoff_pixel_low.valueChanged.connect(self.update_d_cutoff)
        self.ui.d_cutoff_pixel_high.valueChanged.connect(self.update_d_cutoff)
        
        self.ui.d_short_t0.valueChanged.connect(self.update_d_short_t0)
        self.ui.d_long_t0.valueChanged.connect(self.update_d_long_t0)
        self.ui.d_disco_t0.valueChanged.connect(self.update_d_disco_t0)
        self.ui.d_num_shots.valueChanged.connect(self.update_d_num_shots)
        self.ui.d_delay_type_list.currentIndexChanged.connect(self.update_d_delay_type)
        self.ui.d_delay_type_list.addItem('Short')
        self.ui.d_delay_type_list.addItem('Long')
        self.ui.d_delay_type_list.addItem('Disco')
        self.ui.d_display_mode.addItem('Average')
        self.ui.d_display_mode.addItem('Raw')
        self.ui.d_display_mode_spectra.addItem('Probe')
        self.ui.d_display_mode_spectra.addItem('[Reference]')
        self.ui.d_time.valueChanged.connect(self.update_d_time)
        self.ui.d_move_to_time_btn.clicked.connect(self.exec_d_move_to_time)
        self.ui.d_threshold_pixel.valueChanged.connect(self.update_threshold)
        self.ui.d_threshold_value.valueChanged.connect(self.update_threshold)
        self.ui.d_set_linear_corr_btn.clicked.connect(self.exec_d_set_linear_corr_btn)
        
        self.ui.d_run_btn.clicked.connect(self.exec_d_run_btn)
        self.ui.d_stop_btn.clicked.connect(self.exec_d_stop_btn)
        self.ui.d_pause_btn.clicked.connect(self.exec_d_pause_btn)
        self.ui.d_exit_btn.clicked.connect(self.exec_d_exit_btn)
        
        self.ui.progressBar.setValue(0)
        self.metadata = {}
        self.kinetic_pixel = 0
        self.spectra_timestep = 0
        
        #######################################################################
        #######################################################################
        #######################################################################
        # Section 2: Initializing values in the gui
        
        self.times = np.array([0,1,2,3,4,5])
#        self.bin_length = 0.1
#        self.disco_times = np.linspace(min(self.times),max(self.times),((max(self.times)-min(self.times))/self.bin_length)+1)
        self.num_pixels = 2048
        self.ui.filename.setText(r'E:/default_datafile')
        self.idle = True
        self.ui.use_calib.toggle()
        self.ui.use_cutoff.toggle()
        self.ui.plot_log_t.toggle()
        self.ui.plot_log_t.toggle()
        self.ui.plot_timescale.toggle()
        self.ui.d_use_linear_corr.setChecked(False)
        self.ui.d_use_reference.setChecked(False)
        self.ui.d_use_ir_gain.setChecked(False)
        
        if preloaded is False:
            self.ui.cutoff_pixel_low.setValue(100)
            self.ui.cutoff_pixel_high.setValue(400)
            self.ui.calib_pixel_low.setValue(100)
            self.ui.calib_pixel_high.setValue(400)
            self.ui.calib_wave_low.setValue(500)
            self.ui.calib_wave_high.setValue(800)
            self.ui.num_shots.setValue(200)
            self.ui.num_sweeps.setValue(500)
            self.ui.kinetic_pixel.setValue(100)
            self.ui.spectra_timestep.setValue(4)
            self.ui.delay_type_list.setCurrentIndex(0)
            self.ui.d_display_mode.setCurrentIndex(0)
            self.ui.d_display_mode_spectra.setCurrentIndex(0)
            self.ui.short_t0.setValue(1800)
            self.ui.long_t0.setValue(999995)
            self.ui.disco_t0.setValue(10000)
            self.ui.kinetic_pixel.setValue(0)
            self.ui.spectra_timestep.setValue(0)
            self.ui.d_refman_horiz_offset.setValue(0)
            self.ui.d_refman_scale_center.setValue(250)
            self.ui.d_refman_scale_factor.setValue(1)
            self.ui.d_refman_vertical_offset.setValue(0)
            self.ui.d_refman_vertrical_stretch.setValue(1)
            self.ui.d_use_linear_corr.setChecked(1)
            self.ui.d_threshold_pixel.setValue(554)
            self.ui.d_threshold_value.setValue(15000)
            self.ui.d_time.setValue(1)
        else:
            self.ui.cutoff_pixel_low.setValue(pl[0])
            self.ui.cutoff_pixel_high.setValue(pl[1])
            self.ui.calib_pixel_low.setValue(pl[2])
            self.ui.calib_pixel_high.setValue(pl[3])
            self.ui.calib_wave_low.setValue(pl[4])
            self.ui.calib_wave_high.setValue(pl[5])
            self.ui.num_shots.setValue(pl[6])
            self.ui.num_sweeps.setValue(pl[7])
            self.ui.kinetic_pixel.setValue(pl[8])
            self.ui.spectra_timestep.setValue(int(pl[9]))
            self.ui.delay_type_list.setCurrentIndex(pl[10])
            self.ui.d_display_mode.setCurrentIndex(pl[11])
            self.ui.d_display_mode_spectra.setCurrentIndex(pl[12])
            self.ui.short_t0.setValue(pl[13])
            self.ui.long_t0.setValue(pl[14])
            self.ui.disco_t0.setValue(pl[25])
            self.ui.kinetic_pixel.setValue(0)
            self.ui.spectra_timestep.setValue(0)
            self.ui.d_refman_horiz_offset.setValue(pl[17])
            self.ui.d_refman_scale_center.setValue(pl[18])
            self.ui.d_refman_scale_factor.setValue(pl[19])
            self.ui.d_refman_vertical_offset.setValue(pl[20])
            self.ui.d_refman_vertrical_stretch.setValue(pl[21])
            self.ui.d_threshold_pixel.setValue(pl[22])
            self.ui.d_threshold_value.setValue(pl[23])
            self.ui.d_time.setValue(1)

        
    ###########################################################################
    ###########################################################################
    ###########################################################################
    # Section 3: Methods which define signals connected in Section 1
        
    def save_gui_data(self):
        output = np.array([self.ui.cutoff_pixel_low.value(),
                        self.ui.cutoff_pixel_high.value(),
                        self.ui.calib_pixel_low.value(),
                        self.ui.calib_pixel_high.value(),
                        self.ui.calib_wave_low.value(),
                        self.ui.calib_wave_high.value(),
                        self.ui.num_shots.value(),
                        self.ui.num_sweeps.value(),
                        self.ui.kinetic_pixel.value(),
                        self.ui.spectra_timestep.value(),
                        self.ui.delay_type_list.currentIndex(),
                        self.ui.d_display_mode.currentIndex(),
                        self.ui.d_display_mode_spectra.currentIndex(),
                        self.ui.short_t0.value(),
                        self.ui.long_t0.value(),
                        self.ui.kinetic_pixel.value(),
                        self.ui.spectra_timestep.value(),
                        self.ui.d_refman_horiz_offset.value(),
                        self.ui.d_refman_scale_center.value(),
                        self.ui.d_refman_scale_factor.value(),
                        self.ui.d_refman_vertical_offset.value(),
                        self.ui.d_refman_vertrical_stretch.value(),
                        self.ui.d_threshold_pixel.value(),
                        self.ui.d_threshold_value.value(),
                        self.ui.d_time.value(),
                        self.ui.disco_t0.value()])
        np.savetxt(self.lif,output,newline='\r\n')

        
    def exec_folder_btn(self):
        '''execute on clicking folder button - store filename and display'''
        self.filename = QtGui.QFileDialog.getOpenFileName(None, 'Select Folder', 'E:')
        self.ui.filename.setText(self.filename[0])
        return
        
    def exec_file_changed(self):
        '''execute on filename change - stores filename'''
        self.filename = self.ui.filename.toPlainText()
        return
        
    def metadata_changed(self):
        self.metadata['pump wavelength'] = self.ui.metadata_pump_wave.text()
        self.metadata['pump power'] = self.ui.metadata_pump_power.text()
        self.metadata['pump size'] = self.ui.metadata_pump_size.text()
        self.metadata['probe wavelengths'] = self.ui.metadata_probe_wave.text()
        self.metadata['probe power'] = self.ui.metadata_probe_power.text()
        self.metadata['probe size'] = self.ui.metadata_probe_power.text()
    
    def update_metadata(self):
        self.metadata_changed()
        if self.delay_type == 0:
            self.metadata['delay type'] = 'Short'
            self.metadata['time zero'] = self.short_t0
        if self.delay_type == 1:
            self.metadata['delay type'] = 'Long'
            self.metadata['time zero'] = self.long_t0
        if self.delay_type == 2:
            self.metadata['delay type'] = 'Disco'
            self.metadata['timezero'] = self.disco_t0
        self.metadata['num shots'] = self.num_shots
        self.metadata['calib pixel low'] = self.calib[0]
        self.metadata['calib pixel high'] = self.calib[1]
        self.metadata['calib wave low'] = self.calib[2]
        self.metadata['calib wave high'] = self.calib[3]
        self.metadata['cutoff low'] = self.cutoff[0]
        self.metadata['cutoff high'] = self.cutoff[1]
        self.metadata['use reference'] = self.ui.d_use_reference.isChecked()
        self.metadata['avg off shots'] = self.ui.d_use_avg_off_shots.isChecked()
        self.metadata['use ref manip'] = self.ui.d_use_ref_manip.isChecked()
        self.metadata['use calib'] = self.ui.d_use_calib.isChecked()
        
        
    def exec_timefile_folder_btn(self):
        '''execute on timefile folder button - store filename and update list'''
        self.timefile = QtGui.QFileDialog.getOpenFileName(None, 'Select File in Folder', 'E:')
        self.timefile_folder = os.path.dirname(self.timefile[0])
        if self.timefile_folder.endswith('/'):
            self.timefile_folder = self.timefile_folder[:-1]
        self.timefile = os.path.basename(self.timefile[0])
        self.load_timefiles_to_list()
        return
        
    def load_timefiles_to_list(self):
        '''loads all .txt files in timefile folder and puts them in drop down list'''
        self.ui.timefile_list.clear()
        self.timefiles = []
        try:
            for file in os.listdir(self.timefile_folder):
                if file.endswith('.tf'):
                    self.timefiles.append(file)
            current_index = 0
            for i,timefile in enumerate(self.timefiles):
                self.ui.timefile_list.addItem(timefile)
                if timefile == self.timefile:
                    current_index = i
            self.ui.timefile_list.setCurrentIndex(current_index)
            self.update_timefile(current_index)
        except:
            self.append_history('Error loading timefiles in folder')
        return
        
    def update_timefile(self,i):
        '''execute when new timefile selected'''
        self.timefile = self.timefiles[self.ui.timefile_list.currentIndex()]
        self.update_times()
        return
        
    def update_times(self):
        '''load times from timefile and store them'''
        self.times = np.genfromtxt(self.timefile_folder+'/'+self.timefile,dtype=float) #timefile to use for delay generator
        #if self.delay_type == 2:
         #   self.disco_times = np.linspace(min(self.times),max(self.times),((max(self.times)-min(self.times))/self.bin_length)+1) #timefile to use for binning
        return
        
    def exec_timefile_new_blank_btn(self):
        '''opens blank notepad to create timefile, ensure to save as .tf'''
        subprocess.call(['notepad.exe'])
        self.load_timefiles_to_list()
        return
        
    def exec_timefile_edit_btn(self):
        '''executes when timefile edit button clicked - opens notepad and throws
           error when no timefile was initially selected'''
        try:
            subprocess.call(['notepad.exe',self.timefile_folder+'/'+self.timefile])
            self.update_times()
        except:
            self.ui.history.appendPlainText('Error loading times: make sure to select timefile')
        return
        
    def exec_timefile_new_params_btn(self):
        '''creates a new timefile from the parameters listed on the gui'''
        mins = [self.ui.timefile_t1_min,self.ui.timefile_t2_min,self.ui.timefile_t3_min]
        maxes = [self.ui.timefile_t1_max,self.ui.timefile_t2_max,self.ui.timefile_t3_max]
        steps = [self.ui.timefile_t1_steps,self.ui.timefile_t2_steps,self.ui.timefile_t3_steps]
        uses = [self.ui.timefile_uset1, self.ui.timefile_uset2, self.ui.timefile_uset3]
        logs = [self.ui.timefile_logt1, self.ui.timefile_logt2, self.ui.timefile_logt3]
        new_times = []
        for use,log,_min,_max,_steps in zip(uses,logs,mins,maxes,steps):
            if use.isChecked():
                if log.isChecked():
                    for value in np.logspace(np.log10(_min.value()),np.log10(_max.value()),num=_steps.value(),dtype=int):
                        new_times.append(value)
                else:
                    for value in np.linspace(_min.value(),_max.value(),num=_steps.value(),dtype=int):
                        new_times.append(value)
        try:
            new_filename = QtGui.QFileDialog.getSaveFileName(None,'Save File As:',self.timefile_folder)
        except:
            self.append_history('Error Saving Timefile: Make sure a timefile folder is selected')
        new_filename = new_filename[0]
        if new_filename[-3:] != '.tf':
            new_filename = new_filename+'.tf'
        np.savetxt(new_filename,new_times,fmt='%i',newline='\r\n')
        self.load_timefiles_to_list()
        return
        
    def update_short_t0(self):
        '''executes when the short time t0 is changed - keeps consistent between tabs'''
        self.short_t0 = self.ui.short_t0.value()
        self.ui.d_short_t0.setValue(self.short_t0)
        return
        
    def update_d_short_t0(self):
        '''diagostics tab equivalent to update_short_t0'''
        self.short_t0 = self.ui.d_short_t0.value()
        self.ui.short_t0.setValue(self.short_t0)
        return
        
    def update_long_t0(self):
        '''executes when the long time t0 is changed - keeps consistent between tabs'''
        self.long_t0 = self.ui.long_t0.value()
        self.ui.d_long_t0.setValue(self.long_t0)
        return
        
    def update_d_long_t0(self):
        '''diagnostics tab equivalent to update_long_t0'''
        self.long_t0 = self.ui.d_long_t0.value()
        self.ui.long_t0.setValue(self.long_t0)
        return
    
    def update_disco_t0(self):
        '''executes when the disco time t0 is changed - keeps consistent between tabs'''
        self.disco_t0 = self.ui.disco_t0.value()
        self.ui.d_disco_t0.setValue(self.disco_t0)
        return
        
    def update_d_disco_t0(self):
        '''diagnostics tab equivalent to update_disco_t0'''
        self.disco_t0 = self.ui.d_disco_t0.value()
        self.ui.disco_t0.setValue(self.disco_t0)
        return
        
    def update_num_shots(self):
        '''executes when the number of shotes is updated - note that this is total
           number of shots and is shots/2 number of TA averages'''
        if self.idle is True:
            self.num_shots = self.ui.num_shots.value()
            self.ui.d_num_shots.setValue(self.num_shots)
        return
        
    def update_d_num_shots(self):
        '''diagnostic equivalent of update_num_shots'''
        if self.idle is True:
            self.num_shots = self.ui.d_num_shots.value()
            self.ui.num_shots.setValue(self.num_shots)
        return
            
    def update_num_sweeps(self):
        '''executes when the number of sweeps changes'''
        if self.idle is True:
            self.num_sweeps = self.ui.num_sweeps.value()
        return
        
    def update_delay_type(self):
        '''updates when delay types (short vs long vs disco) has changed'''
        self.delay_type = self.ui.delay_type_list.currentIndex()
        self.ui.d_delay_type_list.setCurrentIndex(self.delay_type)
        return
        
    def update_d_delay_type(self):
        '''diagnostic equivalent of update_delay_type'''
        self.delay_type = self.ui.d_delay_type_list.currentIndex()
        self.ui.delay_type_list.setCurrentIndex(self.delay_type)
        return
        
    def update_use_calib(self):
        '''stores calibration boolean'''
        self.use_calib = self.ui.use_calib.isChecked()
        self.ui.d_use_calib.setChecked(self.use_calib)
        return
        
    def update_d_use_calib(self):
        '''diagnostic equivalent of update_use_calib'''
        self.use_calib = self.ui.d_use_calib.isChecked()
        self.ui.use_calib.setChecked(self.use_calib)
        return
        
    def update_calib(self):
        '''stores calibration data when values change'''
        self.calib  = [self.ui.calib_pixel_low.value(),
                       self.ui.calib_pixel_high.value(),
                       self.ui.calib_wave_low.value(),
                       self.ui.calib_wave_high.value()]
        self.ui.d_calib_pixel_low.setValue(self.calib[0])
        self.ui.d_calib_pixel_high.setValue(self.calib[1])
        self.ui.d_calib_wave_low.setValue(self.calib[2])
        self.ui.d_calib_wave_high.setValue(self.calib[3])
        return
        
    def update_d_calib(self):
        '''diagnostic equivalent of update_calib'''
        self.calib  = [self.ui.d_calib_pixel_low.value(),
                       self.ui.d_calib_pixel_high.value(),
                       self.ui.d_calib_wave_low.value(),
                       self.ui.d_calib_wave_high.value()]
        self.ui.calib_pixel_low.setValue(self.calib[0])
        self.ui.calib_pixel_high.setValue(self.calib[1])
        self.ui.calib_wave_low.setValue(self.calib[2])
        self.ui.calib_wave_high.setValue(self.calib[3])
        return
             
    def update_use_cutoff(self):
        '''stores cutoff boolean'''
        self.use_cutoff = self.ui.use_cutoff.isChecked()
        self.ui.d_use_cutoff.setChecked(self.use_cutoff)
        return
        
    def update_d_use_cutoff(self):
        '''diagnostic equivalent of use_cutoff'''
        self.use_cutoff = self.ui.d_use_cutoff.isChecked()
        self.ui.use_cutoff.setChecked(self.use_cutoff)
        return
             
    def update_cutoff(self):
        '''stores cutoff data when values change'''
        if self.ui.cutoff_pixel_high.value() > self.ui.cutoff_pixel_low.value():
            self.cutoff = [self.ui.cutoff_pixel_low.value(),
                           self.ui.cutoff_pixel_high.value()]
            self.ui.d_cutoff_pixel_low.setValue(self.cutoff[0])
            self.ui.d_cutoff_pixel_high.setValue(self.cutoff[1])
        else:
            self.append_history('Cutoff Values Incompatible')
        return
              
    def update_d_cutoff(self):
        '''diagnostic equivalent of update_cutoff'''
        if self.ui.d_cutoff_pixel_high.value() > self.ui.d_cutoff_pixel_low.value():
            self.cutoff = [self.ui.d_cutoff_pixel_low.value(),
                           self.ui.d_cutoff_pixel_high.value()]
            self.ui.cutoff_pixel_low.setValue(self.cutoff[0])
            self.ui.cutoff_pixel_high.setValue(self.cutoff[1])
        else:
            self.append_history('Cutoff Values Incompatible')
        return
        
    def update_kinetic_pixel(self):
        '''stores value for which pixel to display kinetic in graph'''
        self.kinetic_pixel = self.ui.kinetic_pixel.value()
        if self.kinetic_pixel > self.num_pixels:
            self.kinetic_pixel = self.num_pixels-1
        self.ui.kinetic_pixel.setValue(self.kinetic_pixel)
        return
        
    def update_spectra_timestep(self):
        '''stores values for which timestep to display spectra in graph'''
        self.spectra_timestep = self.ui.spectra_timestep.value()
        if self.spectra_timestep > len(self.times):
            self.spectra_timestep = len(self.times)-1
        self.ui.spectra_timestep.setValue(self.spectra_timestep)
        return
        
    def update_plot_log_t(self):
        '''stores booliean for logscale'''
        self.use_logscale = self.ui.plot_log_t.isChecked()
        return
        
    def update_plot_timescale(self):
        '''stores boolean for using actual times'''
        self.use_actual_times = self.ui.plot_timescale.isChecked()
        return
        
    def update_refman(self):
        '''stores referance manipulation data'''
        self.refman = [self.ui.d_refman_vertrical_stretch.value(),
                       self.ui.d_refman_vertical_offset.value(),
                       self.ui.d_refman_horiz_offset.value(),
                       self.ui.d_refman_scale_center.value(),
                       self.ui.d_refman_scale_factor.value()]
        return
        
    def update_threshold(self):
        '''stores threshold information for tiggering'''
        self.threshold = [self.ui.d_threshold_pixel.value(),
                          self.ui.d_threshold_value.value()]
        return
        
    def update_d_time(self):
        '''stores time to move to in diagnostics'''
        self.d_time = self.ui.d_time.value()
        return
        
    def exec_d_set_linear_corr_btn(self):
        '''exectues routine to recalculate linear pixel correction'''
        try:
            self.linear_corr = self.bgd.set_linear_pixel_correlation()
            self.append_history('Successfully set linear pixel correction')
            print(self.linear_corr)
        except:
            self.append_history('Error setting linear pixel correction')
        
    def append_history(self,message):
        self.ui.history.appendPlainText(message)
        self.ui.d_history.appendPlainText(message)
        
    def update_progress_bar(self,i):
        self.ui.progressBar.setValue(i)
        
    ###########################################################################
    ###########################################################################
    ###########################################################################
    # Section 4: Plots
                       
    def create_plots(self):
        '''defines defaults for each graph'''
        self.ui.last_shot_graph.plotItem.setLabels(left='dtt',bottom='Wavelength / Pixel')
        self.ui.last_shot_graph.plotItem.showAxis('top',show=True)
        self.ui.last_shot_graph.plotItem.showAxis('right',show=True)
        
        self.ui.kinetic_graph.plotItem.setLabels(left='dtt',bottom='Time / Timepoint')
        self.ui.kinetic_graph.plotItem.showAxis('top',show=True)
        self.ui.kinetic_graph.plotItem.showAxis('right',show=True)
        
        self.ui.spectra_graph.plotItem.setLabels(left='dtt',bottom='Wavelength / Pixel')
        self.ui.spectra_graph.plotItem.showAxis('top',show=True)
        self.ui.spectra_graph.plotItem.showAxis('right',show=True)
        
        self.ui.d_last_shot_graph.plotItem.setLabels(left='dtt',bottom='Wavelength / Pixel') 
        self.ui.d_last_shot_graph.plotItem.showAxis('top',show=True)
        self.ui.d_last_shot_graph.plotItem.showAxis('right',show=True)
        
        self.ui.d_error_graph.plotItem.setLabels(left='Error',bottom='Wavelength / Pixel')
        self.ui.d_error_graph.plotItem.showAxis('top',show=True)
        self.ui.d_error_graph.plotItem.showAxis('right',show=True)
        
        #self.ui.d_trigger_graph.plotItem.setLabels(left='Trigger Signal',bottom='Shot')
        #self.ui.d_trigger_graph.plotItem.showAxis('top',show=True)
        #self.ui.d_trigger_graph.plotItem.showAxis('right',show=True)
        
        self.ui.d_probe_ref_graph.plotItem.setLabels(left='Counts',bottom='Wavelength / Pixel')
        self.ui.d_probe_ref_graph.plotItem.showAxis('top',show=True)
        self.ui.d_probe_ref_graph.plotItem.showAxis('right',show=True)
        self.lr = pg.LinearRegionItem([self.calib[2],self.calib[3]])
        self.lr.setZValue(-10)
        self.ui.d_probe_ref_graph.addItem(self.lr)
        self.lr.sigRegionChanged.connect(self.region_updated)
        return
        
    def region_updated(self,regionItem):
        px1,px2 = regionItem.getRegion()
        self.ui.d_vline1.display(px1)
        self.ui.d_vline2.display(px2)
        return
        
    def create_plot_waves_and_times(self):
        '''updates all plots within the gui. Note that it will only plot the ones
           that are displayed. When an acquisition is running, it is possible to
           switch between the acquire and diagnostics tab and the plots will update
           accordingly'''
        self.waves = self.pixels_to_waves()
        if self.use_calib is True:
            self.plot_waves = self.pixels_to_waves()
        else:
            self.plot_waves = np.linspace(0,self.num_pixels-1,self.num_pixels)
        
        if self.use_actual_times is True:
            self.plot_times = self.times
        else:
            self.plot_times = np.linspace(0,self.times.size-1,self.times.size)
        
        if self.use_logscale is True:
            self.plot_times = np.log10(self.plot_times)
            
        self.ui.kinetic_wave.display(self.plot_waves[self.kinetic_pixel])
        self.ui.spectra_time.display(self.times[self.spectra_timestep]) #changed to always show actual time
        
        if self.diagnostics_on is False:
            self.plot_dtt = self.current_sweep.avg_data[:]
        self.plot_ls = self.current_data.dtt[:]
        self.plot_probe_shot_error = self.current_data.probe_shot_error[:]
        if self.ui.d_use_reference.isChecked() is True:
            self.plot_ref_shot_error = self.current_data.ref_shot_error[:]
            self.plot_dtt_error = self.current_data.dtt_error[:]
        self.plot_probe_on = self.current_data.probe_on[:]
        self.plot_reference_on = self.current_data.reference_on[:]
        self.plot_probe_on_array = self.current_data.probe_on_array[:]
        self.plot_reference_on_array = self.current_data.reference_on_array[:]
        if self.use_cutoff is True:
            self.plot_waves = self.plot_waves[self.cutoff[0]:self.cutoff[1]]
            if self.diagnostics_on is False:
                self.plot_dtt = self.plot_dtt[:,self.cutoff[0]:self.cutoff[1]]
            self.plot_ls = self.plot_ls[self.cutoff[0]:self.cutoff[1]]
            self.plot_probe_shot_error = self.plot_probe_shot_error[self.cutoff[0]:self.cutoff[1]]
            if self.ui.d_use_reference.isChecked() is True:
                self.plot_ref_shot_error = self.plot_ref_shot_error[self.cutoff[0]:self.cutoff[1]]
                self.plot_dtt_error = self.plot_dtt_error[self.cutoff[0]:self.cutoff[1]]
            self.plot_probe_on = self.plot_probe_on[self.cutoff[0]:self.cutoff[1]]
            self.plot_reference_on = self.plot_reference_on[self.cutoff[0]:self.cutoff[1]]
            self.plot_probe_on_array = self.plot_probe_on_array[:,self.cutoff[0]:self.cutoff[1]]
            self.plot_reference_on_array = self.plot_reference_on_array[:,self.cutoff[0]:self.cutoff[1]]        
        return
        
    def pixels_to_waves(self):
        '''uses calibration values to transform pixels to wavelength values'''
        slope = (self.calib[3]-self.calib[2])/(self.calib[1]-self.calib[0])
        y_int = self.calib[2]-slope*self.calib[0]
        return np.linspace(0,self.num_pixels-1,self.num_pixels)*slope+y_int
                
    def ls_plot(self):
        '''last shot plot on acquire tab'''
        try:
            self.ui.last_shot_graph.plotItem.plot(self.plot_waves,self.plot_ls,clear=True,pen='b')
        except:
            self.append_history('Error Plotting Last Shot')
        return
        
    def top_plot(self):
        '''top plot on acquire tab'''
        try:
            self.ui.top_graph.setImage(self.plot_dtt,scale=(len(self.plot_waves)/len(self.plot_times),1))
        except:
            self.append_history('Error Plotting Top Plot')
        return
        
    def kin_plot(self):
        '''kinetic plot on acquire tab'''
        self.update_kinetic_pixel()
        if self.use_logscale is True:
            plot_times = self.plot_times[np.isfinite(self.plot_times)]
        else:
            plot_times = self.plot_times
        try:
            self.ui.kinetic_graph.plotItem.plot(plot_times,self.plot_dtt[np.isfinite(self.plot_times),self.kinetic_pixel-self.cutoff[0]],pen='r',clear=True)
        except:
            self.append_history('Error Plotting Kinetic Plot')
        return
        
    def spec_plot(self):
        '''spectra plot on acquire tab'''
        self.update_spectra_timestep()
        try:
            self.ui.spectra_graph.plotItem.plot(self.plot_waves,self.plot_dtt[self.spectra_timestep,:],pen='g',clear=True)
        except:
            self.append_history('Error Plotting Spectra Plot')
        return
        
    def d_error_plot(self):
        '''error plot on diagnostics tab'''
        try:
            self.ui.d_error_graph.plotItem.plot(self.plot_waves,np.log10(self.plot_probe_shot_error),pen='r',clear=True,fillBrush='r')
            if self.ui.d_use_reference.isChecked() is True:         
                self.ui.d_error_graph.plotItem.plot(self.plot_waves,np.log10(self.plot_ref_shot_error),pen='g',clear=False,fillBrush='g')    
                self.ui.d_error_graph.plotItem.plot(self.plot_waves,np.log10(self.plot_dtt_error),pen='b',clear=False,fillBrush='b')
        except:
            self.append_history('Error plotting error!')
        self.ui.d_error_graph.plotItem.setYRange(-4,1,padding=0)
        return
        
    def d_trigger_plot(self):
        '''trigger plot on diagnostics tab'''
        try:
            self.ui.d_trigger_graph.plotItem.plot(np.arange(self.num_shots),self.current_data.trigger,pen=None,symbol='o',clear=True)
        except:
            self.append_history('Error Plotting Trigger')
        return
        
    def d_probe_ref_plot(self):
        '''probe and reference spectra plot on diagnostics tab'''
        for item in self.ui.d_probe_ref_graph.plotItem.listDataItems():
            self.ui.d_probe_ref_graph.plotItem.removeItem(item)
        try:
            if self.ui.d_display_mode.currentIndex() == 0:
                self.ui.d_probe_ref_graph.plotItem.plot(self.plot_waves,self.plot_probe_on,pen='r')
                if self.ui.d_use_reference.isChecked() is True:
                    self.ui.d_probe_ref_graph.plotItem.plot(self.plot_waves,self.plot_reference_on,pen='b')
            if self.ui.d_display_mode.currentIndex() == 1:
                if self.ui.d_display_mode_spectra.currentIndex() == 0:
                    for spec in self.plot_probe_on_array:
                        self.ui.d_probe_ref_graph.plotItem.plot(self.plot_waves,spec,pen='r')
                if self.ui.d_display_mode_spectra.currentIndex() == 1:
                    for spec in self.plot_reference_on_array:
                        self.ui.d_probe_ref_graph.plotItem.plot(self.plot_waves,spec,pen='b')
        except:
            self.append_history('Error Plotting Probe and/or Reference Spectra')
        return
        
    def d_ls_plot(self):
        '''last shot plot on diagnostics tab'''
        try:
            self.ui.d_last_shot_graph.plotItem.plot(self.plot_waves,self.plot_ls,pen='b',clear=True)
        except:
            self.append_history('Error Plotting Last Shot')
        return
        
    ###########################################################################
    ###########################################################################
    ###########################################################################
    # Section 5: Messages
        
    def message_block(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Block Probe and Reference")
        msg.setInformativeText("Just press once (be patient)")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        retval = msg.exec_()
        return retval
        
    def message_unblock(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Unblock Probe and Reference")
        msg.setInformativeText("Just press once (be patient)")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        retval = msg.exec_()
        return retval
        
    def message_time_points(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("One or more time point exceeds limit!")
        msg.setInformativeText("Don't be greedy...")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        retval = msg.exec_()
        return retval
        
    def message_error_saving(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Error Saving File")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        retval = msg.exec_()
        return retval
    
    def message_pause(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Measurement Paused")
        msg.setInformativeText("Just press Ok once to resume (be patient)")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        retval = msg.exec_()
        return retval
    
        
        
    ###########################################################################
    ###########################################################################
    ###########################################################################
    # Section 6: Run functions for acquire and diagnostics tab. In general, at 
    # the start of a run a new connection to the camera is made which initialzes
    # an array which can hold the correct amount of data given the number of shots
    # If the number of shots is updated, the run needs to be restarted, even in 
    # diagnostics mode. Also note that connections to the delay method are shared 
    # after the type of delay is chosen. This allow for simpler execution by wrapping
    # the delay functions the same - see delay_class.py
        
    def running(self):
        self.idle = False
        self.ui.run_btn.setDisabled(True)
        self.ui.d_run_btn.setDisabled(True)
        self.ui.file_box.setDisabled(True)
        self.ui.timefile_box.setDisabled(True)
        self.ui.acquire_options_box.setDisabled(True)
        self.ui.calib_box.setDisabled(True)
        self.ui.d_set_linear_corr_btn.setDisabled(True)
        if self.diagnostics_on is False:
            self.ui.d_time_box.setDisabled(True)
            self.ui.d_other_box.setDisabled(True)
            self.ui.d_calib_box.setDisabled(True)
            self.ui.d_refmanip_box.setDisabled(True)
            self.ui.d_acquire_options_box.setDisabled(True)
        return
            
        
    def idling(self):
        self.idle = True
        self.ui.run_btn.setDisabled(False)
        self.ui.d_run_btn.setDisabled(False)
        self.ui.file_box.setDisabled(False)
        self.ui.file_box.setDisabled(False)
        self.ui.timefile_box.setDisabled(False)
        self.ui.acquire_options_box.setDisabled(False)
        self.ui.calib_box.setDisabled(False)
        self.ui.d_refmanip_box.setDisabled(False)
        self.ui.d_acquire_options_box.setDisabled(False)
        self.ui.d_other_box.setDisabled(False)
        self.ui.d_calib_box.setDisabled(False)
        self.ui.d_time_box.setDisabled(False)
        self.ui.d_set_linear_corr_btn.setDisabled(False)
        return
        
    def acquire(self):
        '''acquire data from camera'''
        self.append_history('Acquiring '+str(self.num_shots)+' shots')
        self.camera.start_acquire.emit()
        return
        
    def post_acquire(self,probe,reference,first_pixel,num_pixels):
        '''process ta data according to functions found in ta_data_processing.py'''
        try:
            self.current_data.update(probe,
                                     reference,
                                     first_pixel,
                                     num_pixels)
        except:
             self.current_data = ta_data_processing(probe,
                                                    reference,
                                                    first_pixel,
                                                    num_pixels)
        if self.ui.d_use_linear_corr.isChecked():
            try:
                self.current_data.linear_pixel_correlation(self.linear_corr)
            except:
                self.append_history('Error using linear pixel correction')
        self.high_trig_std = self.current_data.separate_on_off(self.tau_flip_request)
        if self.ui.test_run_btn.isChecked() is False:
            self.current_data.sub_bgd(self.bgd)
        if self.ui.d_use_ref_manip.isChecked() is True:
            self.current_data.manipulate_reference(self.refman)
        self.current_data.average_shots()
        if self.ui.d_use_reference.isChecked() is True:
            self.current_data.correct_probe_with_reference()
            self.current_data.average_refd_shots()
            self.high_dtt = self.current_data.calculate_dtt(use_reference=True,cutoff=self.cutoff,use_avg_off_shots=self.ui.d_use_avg_off_shots.isChecked(),max_dtt=np.abs(self.ui.d_max_dtt.value()))
            self.current_data.calculate_dtt_error(use_reference=True,use_avg_off_shots=self.ui.d_use_avg_off_shots.isChecked())
        else:
            self.high_dtt = self.current_data.calculate_dtt(use_reference=False,cutoff=self.cutoff,use_avg_off_shots=self.ui.d_use_avg_off_shots.isChecked(),max_dtt=np.abs(self.ui.d_max_dtt.value()))
            self.current_data.calculate_dtt_error(use_reference=False,use_avg_off_shots=self.ui.d_use_avg_off_shots.isChecked())
        
# =============================================================================
#         if self.delay_type == 2:
#             try:
#                 self.binfail = False
#                 self.current_data.calculate_delay_array
#                 self.current_data.disco_binning(self.bin_length,self.upper_limit)           
#             except:
#                 self.append_history('Binning failed for last point')
#                 self.binfail = True
# =============================================================================
            
        
        if (self.high_trig_std is False) and (self.high_dtt is False):
# =============================================================================
#             if self.delay_type == 2:
#                 if self.binfail == True:
#                     self.current_sweep.add_current_data(self.current_data.dtt,time_point=self.timestep)
#                 else:    
#                     self.current_sweep.add_current_data_disco(self.current_data.staged_dtt,self.current_data.staged_weight)
#             else:
# =============================================================================
            self.current_sweep.add_current_data(self.current_data.dtt,time_point=self.timestep)
        else:
            self.append_history('Did not add last point')
            
        self.create_plot_waves_and_times()
        if self.ui.acquire_tab.isVisible() is True:
            self.ls_plot()
            self.top_plot()
            self.kin_plot()
            self.spec_plot()
        if self.ui.diagnos_tab.isVisible() is True:
            self.d_ls_plot()
            self.d_error_plot()
            #self.d_trigger_plot()
            self.d_probe_ref_plot()        
            
        if self.stop_request is True:
            self.finish()
        elif self.timestep == len(self.times)-1:
            self.post_sweep()
        else:
            if self.pause_request is True:
                self.append_history('Measurement paused')
                self.message_pause()
                self.pause_request = False
                self.append_history('Measurement resumed')
            self.timestep = self.timestep+1
            self.time = self.times[self.timestep]
            self.ui.time_display.display(self.time)
            self.ui.progressBar.setValue(self.timestep+1)
            self.move(self.time)
            self.acquire()
        return
   
    def acquire_bgd(self):
        '''acquire data from camera for background - increases shots by 10x'''
        self.append_history('Acquiring '+str(self.num_shots)+' shots')
        self.camera.start_acquire.emit()
        return
        
    def post_acquire_bgd(self,probe,reference,first_pixel,num_pixels):      
        '''process background data'''
        self.message_unblock()
        self.bgd = ta_data_processing(probe,
                                      reference,
                                      first_pixel,
                                      num_pixels)
        if self.ui.d_use_linear_corr.isChecked():
            try:
                self.bgd_data.linear_pixel_correlation(self.linear_corr)
            except:
                self.append_history('Error using linear pixel correction')
        self.bgd.separate_on_off(self.threshold)
        self.bgd.average_shots() 
        self.camera.Exit()
        self.run()          
        return    
    
    def exec_run_btn(self):
        '''executes when run on aquire tab is pressed, if test mode is selected
           data will not be saved. This function loops over the number of sweeps'''
        if self.ui.test_run_btn.isChecked() is True:
            self.append_history('Launching Test Run!')
        else:
            self.append_history('Launching Run!')
        
        self.stop_request = False
        self.pause_request = False
        self.diagnostics_on = False
        self.running()
        self.update_num_shots()
        
        if self.delay_type == 0:
            self.append_history('Connecting to delay stage')
            self.delay = esp301_delay_stage(self.short_t0)
        if self.delay_type == 1:
            self.append_history('Connecting to delay generator')
            self.delay = pink_laser_delay(self.long_t0)
        if self.delay_type == 2:
            self.append_history('Connecting to delay generator')
            self.delay = disco_laser_delay(self.disco_t0,"COM3",38400)
            
        if self.delay.initialized is False:
            self.append_history('Stage Not Initialized Correctly')
            self.idling()
            return
        
        success = self.delay.check_times(self.times)
        if success is False:
            self.message_time_points()
            self.idling()
            return
        
        self.append_history('Initializing Camera')
        self.acquire_thread = QtCore.QThread()
        self.acquire_thread.start()
        
        self.camera = octoplus()
        self.num_pixels = self.camera.num_pixels
        self.camera.moveToThread(self.acquire_thread)
        self.camera.start_acquire.connect(self.camera.Acquire)
        self.camera.data_ready.connect(self.post_acquire_bgd)
        
        if self.ui.test_run_btn.isChecked() is False:
            #self.camera.Initialize(number_of_scans=self.num_shots*10,exposure_time_us=1,use_ir_gain=self.ui.d_use_ir_gain.isChecked())
            self.camera.Initialize(lines_per_frame = self.num_shots)
            self.message_block()
            self.append_history('Taking Background')
            self.acquire_bgd()
        else:
            self.run()
        return
            
    def run(self):
        self.update_metadata()
        self.current_sweep = sweep_processing(self.times,self.num_pixels,self.filename,self.metadata)    
        
        self.camera.data_ready.disconnect(self.post_acquire_bgd)
        self.camera.data_ready.connect(self.post_acquire)
        self.camera.Initialize(lines_per_frame = self.num_shots)
        #self.camera.Initialize(number_of_scans=self.num_shots,exposure_time_us=1,use_ir_gain=self.ui.d_use_ir_gain.isChecked())
        
        self.append_history('Starting Sweep '+str(self.current_sweep.sweep_index+1))
        self.ui.sweep_display.display(self.current_sweep.sweep_index+1)
        self.ui.progressBar.setMaximum(len(self.times))
        self.start_sweep()
        
    def finish(self):
        self.camera.Exit()
        self.acquire_thread.quit()
        self.idling()
        try:
            self.delay.close()
        except:
            pass
        return
        
    def start_sweep(self):
        '''loop over number of timesteps in timefile and plots after acquisition'''
        #self.sweep_dtt = np.zeros((self.disco_times.size,self.num_pixels))
        #self.sweep_weight = np.zeros(self.disco_times.size, dtype = int)
        self.timestep = 0
        self.time = self.times[self.timestep]
        self.ui.time_display.display(self.time)
        self.ui.progressBar.setValue(self.timestep+1)
        self.move(self.time)
        self.acquire()
        return
        
    def post_sweep(self):
        if self.ui.test_run_btn.isChecked() is False:
            self.append_history('Saving Sweep '+str(self.current_sweep.sweep_index))
            try:
                self.current_sweep.save_current_data(self.waves)
                self.current_sweep.save_avg_data(self.waves)
                self.current_sweep.save_metadata_each_sweep(self.current_data.probe_on,
                                                            self.current_data.reference_on,
                                                            self.current_data.probe_shot_error)
            except:
                self.message_error_saving()
        
        self.current_sweep.next_sweep()
        
        if self.current_sweep.sweep_index == self.num_sweeps:
            self.finish()
        else:
            self.append_history('Starting Sweep '+str(self.current_sweep.sweep_index))
            self.ui.sweep_display.display(self.current_sweep.sweep_index+1)
            self.start_sweep()
        return

        
    def exec_stop_btn(self):
        '''stops acquisition from running'''
        self.append_history('Stopped')
        self.stop_request=True
        return
        
    def exec_pause_btn(self):
        '''stops acquisition from running'''
        self.append_history('Pausing measurement')
        self.pause_request=True
        return
        
    def exec_exit_btn(self):
        '''will exit from gui. some safeguarding in case exit is called before stop'''
        self.append_history('Stopped')
        if self.idle is False:
            self.finish()
        self.save_gui_data()
        self.close()
        return
        
    def move(self,new_time): 
        '''move to new timepoint. Note that as short and long time delay methods
           are wrapped with the same function calls in delay_class.py this function
           can work for both. Tau flip request is a boolean which takes care of when
           electronic delay swaps on/off probe pulses'''
        self.append_history('Moving to next time: '+str(new_time))
        self.tau_flip_request = self.delay.move_to(new_time)
        if self.delay_type==2 and self.delay.DG_output_state is True:
            self.append_history(self.delay.DG_out)
        return
        
    ###########################################################################
    ###########################################################################
    ###########################################################################
   
    def d_acquire(self):
        '''acquire data from camera'''
        self.append_history('Acquiring '+str(self.num_shots)+' shots')
        self.camera.start_acquire.emit()
        return
        
    def d_post_acquire(self,probe,reference,first_pixel,num_pixels):
        '''process ta data according to functions found in ta_data_processing.py'''
        try:
            self.current_data.update(probe,
                                     reference,
                                     first_pixel,
                                     num_pixels)
        except:
             self.current_data = ta_data_processing(probe,
                                                    reference,
                                                    first_pixel,
                                                    num_pixels)
        if self.ui.d_use_linear_corr.isChecked():
            try:
                self.current_data.linear_pixel_correlation(self.linear_corr)
            except:
                self.append_history('Error using linear pixel correction')
        self.current_data.separate_on_off(self.tau_flip_request)
        if self.ui.test_run_btn.isChecked() is False:
            self.current_data.sub_bgd(self.bgd)
        if self.ui.d_use_ref_manip.isChecked() is True:
            self.current_data.manipulate_reference(self.refman)
        self.current_data.average_shots()
        if self.ui.d_use_reference.isChecked() is True:
            self.current_data.correct_probe_with_reference()
            self.current_data.average_refd_shots()
            self.current_data.calculate_dtt(use_reference=True,cutoff=self.cutoff,use_avg_off_shots=self.ui.d_use_avg_off_shots.isChecked())
            self.current_data.calculate_dtt_error(use_reference=True,use_avg_off_shots=self.ui.d_use_avg_off_shots.isChecked())
        else:
            self.current_data.calculate_dtt(use_reference=False,cutoff=self.cutoff,use_avg_off_shots=self.ui.d_use_avg_off_shots.isChecked())
            self.current_data.calculate_dtt_error(use_reference=False,use_avg_off_shots=self.ui.d_use_avg_off_shots.isChecked())

        self.create_plot_waves_and_times()
        self.d_ls_plot()
        self.d_error_plot()
        #self.d_trigger_plot()
        self.d_probe_ref_plot()
        
        if self.pause_request is True:
            self.append_history('Measurement paused')
            self.message_pause()
            self.pause_request = False
            self.append_history('Measurement resumed')
            self.d_acquire()
        elif self.stop_request is True:
            self.d_finish()
        else:
            self.d_acquire()
        return
        
    def d_acquire_bgd(self):
        '''acquire data from camera for background - increases shots by 10x'''
        self.append_history('Acquiring '+str(self.num_shots)+' shots')
        self.camera.start_acquire.emit()
        return
        
    def d_post_acquire_bgd(self,probe,reference,first_pixel,num_pixels):
        '''process background data'''
        self.bgd = ta_data_processing(probe,
                                      reference,
                                      first_pixel,
                                      num_pixels)
        if self.ui.d_use_linear_corr.isChecked():
            try:
                self.bgd.linear_pixel_correlation(self.linear_corr)
            except:
                self.append_history('Error using linear pixel correction')
        self.bgd.separate_on_off(self.tau_flip_request)
        self.bgd.average_shots() 
        self.camera.Exit()
        self.d_run()          
        return
        
    def exec_d_run_btn(self):
        '''executes when diagnostics run button is pressed - uses a while loop
           as no for loop over sweeps or times is needed'''
        self.append_history('Launching Diagnostics!')
        self.stop_request = False
        self.pause_request = False
        self.diagnostics_on = True
        self.tau_flip_request = False
        self.running()
        self.ui.test_run_btn.setChecked(0)
        self.update_d_num_shots()
        
        if self.delay_type == 0:
            self.append_history('Connecting to delay stage')
            self.delay = esp301_delay_stage(self.short_t0)
        if self.delay_type == 1:
            self.append_history('Connecting to delay generator')
            self.delay = pink_laser_delay(self.long_t0)
        if self.delay_type == 2:
            self.append_history('Connecting to delay generator')
            self.delay = disco_laser_delay(self.disco_t0,"COM3",38400)
        
        if self.delay.initialized is False:
            self.append_history('Stage/DG Not Initialized Correctly')
            self.idling()
        else:
            self.append_history('Connected')
        
        success = self.delay.check_time(self.d_time)
        if success is False:
            self.message_time_points()
            self.idling()
            return
        
        self.append_history('Initializing Camera')
        
        self.acquire_thread = QtCore.QThread()
        self.acquire_thread.start()
        
        self.camera = octoplus()
        self.num_pixels = self.camera.num_pixels
        self.camera.moveToThread(self.acquire_thread)
        self.camera.start_acquire.connect(self.camera.Acquire)
        self.camera.data_ready.connect(self.d_post_acquire_bgd)
        
        self.camera.Initialize(lines_per_frame = self.num_shots)
        #self.camera.Initialize(number_of_scans=self.num_shots*10,exposure_time_us=1,use_ir_gain=self.ui.d_use_ir_gain.isChecked())
        self.message_block()
        self.append_history('Taking Background')
        self.d_acquire_bgd()

    def d_run(self):
        self.move(self.d_time)
        
        self.camera.data_ready.disconnect(self.d_post_acquire_bgd)
        self.camera.data_ready.connect(self.d_post_acquire)
        self.camera.Initialize(lines_per_frame = self.num_shots)
        #self.camera.Initialize(number_of_scans=self.num_shots,exposure_time_us=1,use_ir_gain=self.ui.d_use_ir_gain.isChecked())

        self.d_acquire()
        
    def d_finish(self):  
        self.camera.Exit()
        self.acquire_thread.quit()
        self.idling()
        try:
            self.delay.close()
        except:
            pass
        return
    
    def exec_d_pause_btn(self):
        '''executes when pause button is pressed on diagnostics tab'''
        self.pause_request = True
        return
        
    def exec_d_stop_btn(self):
        '''executes when stop button is pressed on diagnostics tab'''
        self.stop_request = True
        return
        
    def exec_d_exit_btn(self):
        '''will exit from gui - some safeguarding in case exit is called before stop'''
        if self.idle is False:
            self.d_finish()        
        self.save_gui_data()
        self.close()
        return
        
    def exec_d_move_to_time(self):
        '''function which allows changing time delay from diagnostics tab'''
        self.move(self.d_time)
        return
        
    ###########################################################################        
    ###########################################################################
    ###########################################################################
    # Section 7: launches gui and creates plots
        
def main():
    app = QtWidgets.QApplication(sys.argv)
    last_instance_filename = r'C:\Users\mysfe\OneDrive\Desktop\ASRC_TA\last_instance_values.txt'
    try:
        last_instance_values = np.genfromtxt(last_instance_filename)
        ex = Editor(last_instance_filename,pl=last_instance_values,preloaded=True)
    except:
        ex = Editor(last_instance_filename)


    ex.show()
    ex.create_plots()
    sys.exit(app.exec_())
    
    

if __name__ == '__main__':
    main()
