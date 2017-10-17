import logging
import tools.pymus_utils as pymusutil
import numpy as np

logging.basicConfig(level=logging.DEBUG)

class UnexpectedSequenceFormat(Exception):
	pass

class UsPWSequence(object):
	def __init__(self,num_channels=128,pitch=0.,geometry=None,sampling_freq=None):
		''' Plane Waves illumination Sequence:
			init_time  : initial delay
			mod_freq   : modulation_frequency
			prf        : pulse repetition frequency
			angles     : (array) illumination angle			'''
		self.initial_time=0.
		self.modulation_frequency=0.
		self.prf=100.
		self.angles=np.array([])

	def __str__(self):
		res_string = ( " Us PW Sequence - N_angles = {nang} "
					   " init_time = {t0} - prf = {prf} "
					   " mod_freq = {mf} "
					 ).format(nang=len(self.angles),
							  t0=self.initial_time,
							  prf=self.prf,
							  mf=self.modulation_frequency)
		return res_string

	def write_file(self,filename,prefix=None,overwrite=False):
		data_to_write = {'initial_time'         : self.initial_time,
						 'modulation_frequency' : self.modulation_frequency,
						 'prf'                  : self.prf,
						 'angles'               : self.angles}
		pymusutil.generic_hdf5_write(filename,prefix,overwrite,data_to_write)

	def read_file(self,filename,prefix,caps_prf=False):
		key_prf = "PRF" if caps_prf else "prf"
		data_from_file = {'initial_time' : None, 
						  'modulation_frequency' : None,
						  key_prf : None,
						  'angles' : None}
		res = pymusutil.generic_hdf5_read(filename,prefix,data_from_file)
		if data_from_file['initial_time'] is None:
			logging.error("initial_time data not found in %s:%s " % (filename,prefix))
		else:
			self.initial_time = data_from_file['initial_time'][0]
		if data_from_file['modulation_frequency'] is None:
			logging.error("modulation_frequency data not found in %s:%s " % (filename,prefix))
		else:
			self.sampling_freq = data_from_file['modulation_frequency'][0]
		if data_from_file['angles'] is None:
			logging.error("angles data not found in %s:%s " % (filename,prefix))
		else:
			self.angles = data_from_file['angles'][:]
		if data_from_file[key_prf] is None:
			logging.error("prf data not found in %s:%s " % (filename,prefix))
		else:
			self.sampling_freq = data_from_file[key_prf][0]
