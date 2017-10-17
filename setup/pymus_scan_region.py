import tools.pymus_utils as pymusutil
import logging
import numpy as np
import h5py

logging.basicConfig(level=logging.INFO)

class UnexpectedFormat(Exception):
	pass

class ScanRegion:
	def __init__(self,x_input=None,z_input=None):
		''' LinearScan:
				x_axis   : (vector) x coordinates of each row of pixels
				z_axis   : (vector) z coordinate of each column of pixels 
				x_matrix : (matrix) x coordinate of each pixel in the matrix
				z_matrix : (matrix) z coordinate of each pixel in the matrix
				x        : (vector) x coordinate of each pixel in the matrix
				z        : (vector) z coordinate of each pixel in the matrix
				dx       : spatial step in the x-axis
				dz       : spatial step in the z-axis
				Nx       : number of samples in the x-axis
				Nz       : number of samples int the z-axis
				Npixels  : total number of pixels in the matrix '''
		self.x_axis   = np.array([])
		self.z_axis   = np.array([])
		self.x_matrix = np.array([])
		self.z_matrix = np.array([])
		self.x        = np.array([])
		self.z        = np.array([])
		self.dx       = 0.
		self.dz       = 0.
		self.Nx       = 0
		self.Nz       = 0
		self.Npixels  = 0
		if x_input is not None:
			self.set_x_axis(x_input)
		if z_input is not None:
			self.set_z_axis(z_input)

	def set_x_axis(self,x_input):
		if x_input is None:
			raise UnexpectedFormat(" No Input passed as x_axis ")
		if len(x_input) < 1 or len(x_input.shape) > 1:
			raise UnexpectedFormat("X-axis must a vector of size >= 1")
		self.x_axis = x_input
		self.dx = x_input[1] - x_input[0]
		self.Nx = len(x_input)
		self.x_matrix, self.z_matrix = np.meshgrid(self.x_axis,self.z_axis)
		self.x = self.x_matrix.flatten()
		self.z = self.z_matrix.flatten()
		self.Npixels = len(self.x)

	def set_z_axis(self,z_input):
		if z_input is None:
			raise UnexpectedFormat(" No Input passed as z_axis ")
		if len(z_input) < 1 or len(z_input.shape) > 1:
			raise UnexpectedFormat("Z-axis must a vector of size >= 1")
		self.z_axis = z_input
		self.dx = z_input[1] - z_input[0]
		self.Nx = len(z_input)
		self.x_matrix, self.z_matrix = np.meshgrid(self.x_axis,self.z_axis)
		self.x = self.x_matrix.flatten()
		self.z = self.z_matrix.flatten()
		self.Npixels = len(self.x)

	def write_file(self,filename,prefix=None,overwrite=False):
		data_to_write = {'x_axis' : self.x_axis, 'z_axis' : self.z_axis}
		pymusutil.generic_hdf5_write(filename,prefix,overwrite,data_to_write)

	def read_file(self,filename,prefix):
		data_from_file = {'x_axis' : None, 'z_axis' : None}
		res = pymusutil.generic_hdf5_read(filename,prefix,data_from_file)
		if data_from_file['x_axis'] is None:
			logging.error("x_axis data not found in %s:%s " % (filename,prefix))
		else:
			self.set_x_axis(data_from_file['x_axis'][:])
		if data_from_file['z_axis'] is None:
			logging.error("z_axis data not found in %s:%s " % (filename,prefix))
		else:
			self.set_z_axis(data_from_file['z_axis'][:])

	def __str__(self):
		if len(self.x_axis) < 1 or len(self.z_axis) < 1:
			return "Scanning Region - not defined "
		log_str  = ( "Scanning Region "
					 "X = [{x0} ... {xN}] ({nx} pts) / " 
					 "Z = [{z0} ... {zN}] ({nz} pts)   "
				   ).format(x0=self.x_axis[0],
							xN=self.x_axis[-1],
							nx=len(self.x_axis),
							z0=self.z_axis[0],
							zN=self.z_axis[-1],
							nz=len(self.z_axis))
		return log_str 

