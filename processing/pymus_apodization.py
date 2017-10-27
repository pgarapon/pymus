import setup.pymus_scan_region as pymus_scan
import tools.pymus_utils as pymusutil
from scipy import interpolate
import numpy as np
import logging

logging.basicConfig(level=logging.DEBUG)

S_NO_APOD = lambda x: x[0]

class ApodizationWindow(object):
	''' Apodization window '''
	@staticmethod
	def ApodBoxCar(distances,z):
		return (distances <= 0.5*z).astype(float)

	def __init__(self,apod_type):
		self.a_window = S_NO_APOD
		if apod_type == "boxcar":
			self.a_window = ApodizationWindow.ApodBoxCar

	def apodize(self,distances,z):
		return self.a_window(distances,z)				

class IncompatibleDatasetSettings(Exception):
	pass 

class AxialApodization(object):
	def __init__(self,probe,scan,apod_type="boxcar"):
		''' Axial Apodization function:
			probe    : probe
			scan     : scan region
			apod_type: apodization window type
			apodizer : apodization array '''
		self.probe = probe
		self.scan = scan
		self.apod_type = apod_type
		self.apod_window = ApodizationWindow(apod_type)
		self.apodizer = np.ones((self.scan.Npixels,self.probe.num_channels)) 

	def set_apodizer(self,data):
		dpx, dnc = data.shape
		if dpx != self.scan.Npixels or dnc != self.probe.num_channels:
			err_log = " incompatible apodization data %s (expect %s %s) " % (str(data.shape),self.scan.Npixels,self.probe.num_channels) 
			raise IncompatibleDatasetSettings(err_log)
		self.apodizer = data

	def read_file(self,filename,prefix):
		data_from_file = {'apodization/apodizer' : None,'apodization/apod_type' : None}
		res = pymusutil.generic_hdf5_read(filename,prefix,data_from_file)
		if data_from_file['apodization/apodizer'] is None:
			logging.error("apodization data not found in %s:%s " % (filename,prefix))
			return 0
		else:
			r = self.set_apodizer(data_from_file['apodization/apodizer'][:])
		if data_from_file['apodization/apod_type'] is None:
			logging.error("apodization type not found in %s:%s " % (filename,prefix))
			return 0
		else:
			self.apod_type = data_from_file['apodization/apod_type'][0]	
		return res

	def write_file(self,filename,prefix=None,overwrite=False):
		data_to_write = {'apodization/apodizer' : self.apodizer, 'apodization/apod_type' : self.apod_type}
		pymusutil.generic_hdf5_write(filename,prefix,overwrite,data_to_write)
	
	def calc_apodizer(self):
		logging.info(" Computing apodization ... ")
		for row_x in range(self.apodizer.shape[0]):
			transverse_distances = self.scan.x[row_x]*np.ones(self.probe.num_channels) - self.probe.geometry[0,:]
			aperture = self.scan.z[row_x]
			focal = 1.75
			apod_raw = self.apod_window.apodize(transverse_distances,aperture/focal)
			apod_norm = np.linalg.norm(apod_raw,ord=1)
			if apod_norm < 1.:
				logging.error(" 0 APOD -> %s %s " % ( row_x, aperture) )	
			self.apodizer[row_x,:] = apod_raw/np.linalg.norm(apod_raw,ord=1)
		return

