'''this class handles all the data processing once the probe and reference arrays
   are acquired. this class is instantiated withing TA1.py'''
import datetime
import numpy as np

class ta_data_processing:
    '''class for processing ta data'''
    def __init__(self,probe_array,reference_array,first_pixel,num_pixels):
        '''select parts of array which contain the camera data and thus ignoring 
           dummy pixels. A copy of the entire probe array is saved as this will have
           the informaiton form the trigger (photodiode/chopper wheel)'''
        self.untrimmed_probe_array = np.array(probe_array,dtype=int)
        self.probe_array = np.array(probe_array,dtype=float)[:,first_pixel:num_pixels+first_pixel]
        self.reference_array = np.array(reference_array,dtype=float)[:,first_pixel:num_pixels+first_pixel]
        self.raw_probe_array = np.array(probe_array,dtype=float)[:,first_pixel:num_pixels+first_pixel]
        self.raw_reference_array = np.array(reference_array,dtype=float)[:,first_pixel:num_pixels+first_pixel]
        self.first_pixel = first_pixel
        self.num_pixels = num_pixels
        #self.disco_delays_array = np.array(self.untrimmed_probe_array,dtype=float)[::2,self.TDC_pixel]

        
    def update(self,probe_array,reference_array,first_pixel,num_pixels):
        '''select parts of array which contain the camera data and thus ignoring 
           dummy pixels. A copy of the entire probe array is saved as this will have
           the informaiton form the trigger (photodiode/chopper wheel)'''
        self.untrimmed_probe_array = probe_array
        self.probe_array = probe_array[:,first_pixel:num_pixels+first_pixel]
        self.reference_array = reference_array[:,first_pixel:num_pixels+first_pixel]
        self.first_pixel = first_pixel
        self.num_pixels = num_pixels
        #self.disco_delays_array = probe_array[::2,self.TDC_pixel]
        
    def set_linear_pixel_correlation(self):
        '''Mathematical correction for how IR camera reads out even and odd pixels
        differently.  Should only need to be reset once each time the program loads'''
        pr_corr = self.raw_probe_array.mean(axis=0)
        ref_corr = self.raw_reference_array.mean(axis=0)
        pr_corr[::2] = pr_corr[::2]/pr_corr[1::2]
        ref_corr[::2] = ref_corr[::2]/ref_corr[1::2]
        pr_corr[1::2] = pr_corr[1::2]/pr_corr[1::2]
        ref_corr[1::2] = ref_corr[1::2]/ref_corr[1::2]
        return pr_corr, ref_corr
        
    def linear_pixel_correlation(self,linear_corr):
        self.probe_array = self.probe_array/linear_corr[0]
        self.reference_array = self.reference_array/linear_corr[1]
        return
        
    def separate_on_off(self, tau_flip_request = True):
        '''separates on and off shots in the probe and reference arrays, note that
           when the tau flip is passed as true (long time shots where the delay was 
           offset by 1ms) the trigger is rolled over by one value to compensate. 
           Should get rid of tau flip'''
        if tau_flip_request is False:
            self.probe_on_array = self.probe_array[::2,:]
            self.probe_off_array = self.probe_array[1::2,:]
            self.reference_on_array = self.reference_array[::2,:]
            self.reference_off_array = self.reference_array[1::2,:]
        else:
            self.probe_on_array = self.probe_array[1::2,:]
            self.probe_off_array = self.probe_array[::2,:]
            self.reference_on_array = self.reference_array[1::2,:]
            self.reference_off_array = self.reference_array[::2,:]
        return
        
    def average_shots(self):
        '''simple enough - averages shots'''
        self.probe_on = self.probe_on_array.mean(axis=0)
        self.probe_off = self.probe_off_array.mean(axis=0)
        self.reference_on = self.reference_on_array.mean(axis=0)
        self.reference_off = self.reference_off_array.mean(axis=0)
        return
        
    def sub_bgd(self,bgd):
        '''subtract background which is passed as an identical class'''
        self.probe_on_array = self.probe_on_array - bgd.probe_on
        self.probe_off_array = self.probe_off_array - bgd.probe_off
        self.reference_on_array = self.reference_on_array - bgd.reference_on
        self.reference_off_array = self.reference_off_array - bgd.reference_off
        return
        
    def manipulate_reference(self,refman):
        '''manipulates reference to lower noise.
           1. Takes each spectra individually
           2. Centers them on pixel "nfScaleCenter"
           3. Multiplies the x axis by "nfScaleFactor", to scale the horizontal axis
           4. Re-centers the axis to its initial position
           5. Adds a fixed horizontal offset
           6. Interpolates the Y values mapped onto the "ajusted" horizontal
              axis back onto an unmodified axis, to fit the probe spectra'''
        vs, vo, ho, sc, sf = refman
        if vs <= 0:
            vs = 1
        if sf <= 0:
            sf = 1
        x = np.linspace(0,self.num_pixels-1,self.num_pixels)
        new_x = ((x-sc)*sf)+sc-ho
        for i,spectra in enumerate(self.reference_off_array):
            self.reference_off_array[i] = np.interp(new_x,x,spectra*vs+vo)
        for i,spectra in enumerate(self.reference_on_array):
            self.reference_on_array[i] = np.interp(new_x,x,spectra*vs+vo)
        return
        
    def correct_probe_with_reference(self):
        '''reference correct the probe'''
        self.refd_probe_on_array = self.probe_on_array/self.reference_on_array
        self.refd_probe_off_array = self.probe_off_array/self.reference_off_array
        return
        
    def average_refd_shots(self):
        '''averages the referenced shots'''
        self.refd_probe_on = self.refd_probe_on_array.mean(axis=0)
        self.refd_probe_off = self.refd_probe_off_array.mean(axis=0)
        return
        
    def calculate_dtt(self,use_reference=False,cutoff=[0,100],use_avg_off_shots=True,max_dtt=1):
        '''calculate dtt for each shot pair'''
        high_dtt = False
        if use_reference is True:
            if use_avg_off_shots is True:
                self.dtt_array = (self.refd_probe_on_array-self.refd_probe_off_array)/(self.refd_probe_off +10)
            if use_avg_off_shots is False:
                self.dtt_array = (self.refd_probe_on_array-self.refd_probe_off_array)/(self.refd_probe_off_array +10)
        if use_reference is False:
            if use_avg_off_shots is True:
                self.dtt_array = (self.probe_on_array-self.probe_off_array)/(self.probe_off +10)
            if use_avg_off_shots is False:
                self.dtt_array = (self.probe_on_array-self.probe_off_array)/(self.probe_off_array +10)
        self.dtt = self.dtt_array.mean(axis=0)
        fin_dtt = self.dtt[np.isfinite(self.dtt)]
        if np.abs(fin_dtt[cutoff[0]:cutoff[1]]).max() > max_dtt:
            high_dtt = True
            print('High dtt! '+str(datetime.datetime.now()))
        return high_dtt
        
    def calculate_dtt_error(self,use_reference=True,use_avg_off_shots=True):
        '''calculates standard deviation of the dtt array'''
        if use_reference is True:
            if use_avg_off_shots is True:
                self.probe_shot_error = np.std(2*(self.probe_on_array-self.probe_off_array)/(self.probe_on+self.probe_off),axis=0)
                self.ref_shot_error = np.std(2*(self.reference_on_array-self.reference_off)/(self.reference_on_array+self.reference_off),axis=0)
            if use_avg_off_shots is False:
                self.probe_shot_error = np.std(2*(self.probe_on_array-self.probe_off_array)/(self.probe_on_array+self.probe_off_array),axis=0)
                self.ref_shot_error = np.std(2*(self.reference_on_array-self.reference_off_array)/(self.reference_on_array+self.reference_off_array),axis=0)
            self.dtt_error = np.std(self.refd_probe_off_array,axis=0)
        if use_reference is False:
            self.probe_shot_error = np.std(2*(self.probe_on_array-self.probe_off_array)/(self.probe_on_array+self.probe_off_array),axis=0)
        return
    
#==============================================================================
#     def calculate_delay_array(self):
#         self.current_delays = self.TDCcalib*(self.disco_delay_array - self.TDCoffset)
#         return
#         
#==============================================================================
        
#==============================================================================
#     def disco_binning(self,bin_length,upper_limit):
#         '''assigns each shot pair to a bin'''
#         self.num_bins = int((2*upper_limit)/bin_length)+1
#         self.bin_edges = np.linspace(self.time-upper_limit-(0.5*bin_length),self.time+upper_limit+(0.5*bin_length),self.num_bins+1)
#         self.bin_centres = np.around(self.bin_edges[0:self.bin_edges.size-1]+0.5*bin_length, decimals = 3)
#         self.bin_time_indices = np.zeros(self.num_bins,dtype=int)
#         self.staged_dtt = np.zeros((self.times.size,self.num_pixels))
#         self.staged_weight = np.zeros(self.full_time_file.size)
# 
#         '''create array of indices telling us which time points in disco time array
#         relate to the times in the current set of bin centres'''
#         for idx, centre in enumerate(self.bin_centres):
#             self.bin_time_indices[idx] = np.where(self.disco_times == centre)[0][0]
#         
#         '''do the actual binning - create array (shot pairs bin array) of which bin
#         each delay belongs in. each entry in the array is the index for the bin that
#         the delay at that index in the delay array is assigned to'''
#         self.shot_pairs_bin_array = np.digitize(self.current_delays, self.bin_edges)
# 
#         '''bin by bin, add the relevant dtt data to staged_dtt array and update 
#         staged_weight to keep track of how many data points are in each bin'''
#         for idx, centre in enumerate(self.bin_centres):
#             self.temp_array = np.where(self.shot_pairs_bin_array == idx+1)[0]
#             self.staged_weight[self.bin_time_indices[idx]]= self.temp_array.size
#             if self.temp_array.size != 0:
#                 s = np.zeros(self.num_pixels)
#                 for shotpair in self.temp_array:
#                     s[:] = s[:] + self.current_dtt[shotpair,:]
#                 self.staged_dtt[self.bin_time_indices[idx],:] = s[:]/self.temp_array.size
#         return
#==============================================================================
    
