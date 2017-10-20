import logging
import tools.pymus_utils as pymusutil
import numpy as np
import glob

logging.basicConfig(level=logging.DEBUG)

def set_default_geometry(num_channels,pitch):
	zero_y = np.zeros(num_channels)
	zero_z = np.zeros(num_channels)
	D = num_channels*pitch
	x_line = [-0.5*D + i*pitch for i in np.arange(num_channels)]
	return np.array([x_line,zero_y,zero_z]) 

def set_flat_geometry(x_centers):
	num_channels = len(x_centers)
	zero_y = np.zeros(num_channels)
	zero_z = np.zeros(num_channels)
	return np.array([x_center,zero_y,zero_z]) 

class UnexpectedProbeFormat(Exception):
	pass

class UsProbe(object):
	def __init__(self,num_channels=128,pitch=0.,geometry=None,sampling_freq=None):
		''' Ultrasound probe:
			probe_type    : probe type ('linear')
			num_channels  : number of elements
			pitch         : distance between consecutive elements
			geometry      : (array 3 x num_channels) position of each element
			sampling_freq : sampling frequency of the probe
			'''
		self.probe_type    = 'Linear array'
		self.num_channels  = num_channels
		self.pitch         = pitch
		self.geometry      = set_default_geometry(self.num_channels,self.pitch) 
		self.sampling_freq = sampling_freq

	def __str__(self):
		res_string = ( "{typ} probe - N_channels = {nchan} "
					   " F_sampling = {fs} - pitch = {pit} "
					   " Elmts = {shp} "
					 ).format(typ=self.probe_type,
							  nchan=self.num_channels,
							  fs=self.sampling_freq,
							  pit=self.pitch,
							  shp=str(self.geometry.shape))
		return res_string

	def set_geometry(self,geom):
		if len(geom.shape) == 1:
			if len(geom) < 2:
				raise UnexpectedProbeFormat("Probe needs at leat two elements")
			self.num_channels = len(geom)
			self.pitch = geom[1] - geom[0]
			self.geometry = set_flat_geometry(geom)	
		if len(geom.shape) > 2:
			raise UnexpectedProbeFormat("Probe geometry needs to be formated 3 x num_el found %s " % geom.shape)
		x = np.where(np.array(geom.shape) == 3)
		if len(x[0]) > 2 or len(x[0]) == 0:
			raise UnexpectedProbeFormat("Probe geometry needs to be formated 3 x num_el found %s " % geom.shape)
		if x[0] != 0:
			geom = geom.T
		self.num_channels = len(geom[0])
		self.pitch = geom[0][1] - geom[0][0]
		self.geometry = np.array([geom[0],geom[1],geom[2]])			

	def write_file(self,filename,prefix=None,overwrite=False):
		data_to_write = {'geometry' : self.geometry, 'sampling_frequency' : self.sampling_freq}
		pymusutil.generic_hdf5_write(filename,prefix,overwrite,data_to_write)

	def read_file(self,filename,prefix,geom_prefix=""):
		data_from_file = {geom_prefix + 'geometry' : None, 'sampling_frequency' : None}
		res = pymusutil.generic_hdf5_read(filename,prefix,data_from_file)
		if data_from_file[geom_prefix + 'geometry'] is None:
			logging.error("geometry data not found in %s:%s " % (filename,prefix))
		else:
			self.set_geometry(data_from_file[geom_prefix + 'geometry'][:])
		if data_from_file['sampling_frequency'] is None:
			logging.error("sampling_frequency data not found in %s:%s " % (filename,prefix))
		else:
			self.sampling_freq = data_from_file['sampling_frequency'][0]


def ImportFromCreatis():
	dummy_name = "dataset_rf_in_vitro_type1_transmission_1_nbPW_3.hdf5"
	pymusutil.download_dataset(dummy_name,pymusutil.TO_DATA_TMP)
	probe = UsProbe()
	probe.read_file(pymusutil.TO_DATA_TMP + dummy_name,"US/US_DATASET0000/","probe_")
	probe.write_file(pymusutil.TO_DATA + "probe/linear_probe.hdf5","probe")
