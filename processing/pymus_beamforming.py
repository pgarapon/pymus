import setup.pymus_scan_region as pymus_scan
import setup.pymus_us_dataset as pymus_dataset
import processing.pymus_apodization as pymus_apod
import result.pymus_image as pymus_image
from scipy import interpolate
import h5py
import numpy as np
import matplotlib.pyplot as plt
import logging

logging.basicConfig(level=logging.DEBUG)

S_DEBUG = False

class BeamFormer(object):
	''' Plane Wave beamformer holds:
		scan_region : scanning region object
		probe       : probe object
		apodizer    : apodization object
		bf_data     : beamformed data
		bf_image    : beamformed image '''
	def __init__(self,scan_reg,probe,apod_type):
		self.scan = scan_reg
		self.probe = probe
		self.bf_data = np.zeros((scan_reg.Npixels,))
		self.bf_image = pymus_image.EchoImage(scan_reg)
		self.apod = pymus_apod.AxialApodization(self.probe,self.scan,apod_type)

	def load_apodizer(self,from_file=None,prefix=None):
		if self.apod.apod_type == "none":
			logging.info(" No apodization - skipping calc ")
			return
		if from_file is not None:
			res = self.apod.read_file(from_file,prefix)
			if res == 0:
				logging.error("Attempted and failed to read apod data in %s " % from_file)
				self.apod.calc_apodizer()
			else:
				logging.info(" Loaded apodization from file ")
		else:
			self.apod.calc_apodizer()

	def save_apodizer(self,to_file,prefix=None):
		self.apod.write_file(to_file,prefix=prefix,overwrite=True)
	
	def beamform(self,sequence,data):
		dataset = pymus_dataset.UsDataSet("no_name",self.probe,sequence)
		r = dataset.set_data(data)
		if r > 0: 
			raise pymus_dataset.IncompatibleDatasetSettings(" incompatible data - impossible to beamform ")
		dataset.sound_speed = 1540. # TODO
		angls = sequence.angles
		logging.info(" Beamforming signal ... ")
		''' CODA in time unit '''
		time_vector = sequence.initial_time + np.arange(dataset.num_samples)/self.probe.sampling_freq

		for w_i, angle_i in zip(range(len(angls)),angls):
			logging.info(" 		Angle = %s " % angle_i) 
			''' transmit delay of each pixel - ie: time of arrival of excitation signal to pixel (x,z) '''
			transmit_distance = self.scan.z*np.cos(angle_i)+self.scan.x*np.sin(angle_i);
			for n_x in np.arange(self.probe.num_channels):
				''' receive delay from pixel (x,z) to element n_x '''
				sqr_x_dist = (self.probe.geometry[0,n_x]-self.scan.x)**2
				sqr_z_dist = (self.probe.geometry[2,n_x]-self.scan.z)**2
				receive_distance = np.sqrt( sqr_x_dist + sqr_z_dist );
				''' total delay on the pixel array '''
				delay = ( transmit_distance + receive_distance )/dataset.sound_speed;
				if delay.max() > time_vector.max():
					logging.error(" Inconsistent data - code too short to probe farthest elements ")
					continue
				''' beamformed data '''
				f_interp = interpolate.interp1d(time_vector,data[w_i,n_x,:],kind='slinear',bounds_error=False)
				delayed_inc = f_interp(delay)
				''' apodization '''
				apod = self.apod.apodizer[:,n_x]
				''' Debugging log '''
				log_shapes = ""
				if S_DEBUG:
					s_1 = str(time_vector.shape)
					s_2 = str(dataset.data[w_i,n_x,:].shape)
					s_3 = str(delay.shape)
					s_4 = str(self.bf_data.shape)
					s_5 = str(np.array(delayed_inc).shape)
					log_shapes = ( " TimeGrid->{tv}pts [{dim}   {diM}] - DataSlots->{ds}pts "
								   " Delays->{dl}pts [{dlm}  {dlM}] - "
								   " BF data->{bf}pts "
								   " Delay(intrp)->{ic}pts [{dim}   {diM}] "
								 ).format(tv=str(time_vector.shape),
										  ds=str(dataset.data[w_i,n_x,:].shape),
										  dl=str(delay.shape),
									      bf=str(self.bf_data.shape),
										  ic=str(np.array(delayed_inc).shape),
										  dlm=delay.min(),
										  dlM=delay.max(),
										  dim=time_vector.min(),
										  diM=time_vector.max())
				else:
					log_shapes = ""
				log_sequence = "n_X=%s - Ang=%s - shapes: %s " % ( n_x,angle_i,log_shapes) 
				logging.debug(log_sequence)
				self.bf_data += apod*delayed_inc

		self.bf_image.import_data(self.bf_data)
		im_title  = " PW Beamforming \n"
		im_title += " %s angles " % len(angls)
		self.bf_image.set_title(im_title) 

	def write_image(self,path_to_img):
		self.bf_image.write_file(path_to_img,prefix=None,overwrite=True)

	def show_image(self):
		self.bf_image.show_image(dbScale=False,dynamic_range=60)

