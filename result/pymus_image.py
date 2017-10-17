import h5py
import tools.pymus_utils as pymusutil
import numpy as np
import matplotlib.pyplot as plt
import logging

logging.basicConfig(level=logging.DEBUG)

class ImageFormatError(Exception):
	pass

class EchoImage(object):
	''' Echogeneicity grayscale image
		'''
	def __init__(self,scan):
		self.scan = scan
		self.data_array = np.zeros((len(scan.z_axis),len(scan.x_axis)))
		self.scan_x_bounds = [self.scan.x_axis.min(), self.scan.x_axis.max()]
		self.scan_z_bounds = [self.scan.z_axis.min(), self.scan.z_axis.max()]
		self.title = ""
		
	def import_data(self,data):
		try:
			self.data_array = np.abs( np.reshape(data,self.data_array.shape) )
		except:
			raise ImageFormatError(" format error - cannot reshape %s to %s " % ( str(data.shape),str(self.data_array.shape) ))
		return
	 
	def set_title(self,title):
		self.title = title

	def show_image(self,dbScale=True,dynamic_range=60):
		z_m, z_M = self.scan_z_bounds
		x_m, x_M = self.scan_x_bounds
		z_span = z_M - z_m
		x_span = x_M - x_m
		x_ratio = x_span/z_span
		print("X -> %s %s Z -> %s %s / %s %s / %s " % (x_m,x_M,z_m,z_M,z_span,x_span,x_ratio))
		base_sz = 6.
		im_M = self.data_array.max()
		fig, ax = plt.subplots(figsize=(1.0 + x_ratio*base_sz,0.3 + base_sz))
		xtent = [x_m,x_M,z_m,z_M]
		if dbScale:
			plt_im = 20.*np.log10((1./im_M)*self.data_array)
		else:
			plt_im = self.data_array
		cax = ax.imshow(plt_im,interpolation='none',vmin=-1.*dynamic_range,vmax=0.,extent=xtent,cmap='gray')
		ax.set_xlabel(" x [mm] ")
		ax.set_ylabel(" z [mm] ")
		ax.set_title(self.title)
		range_ticks = [-1.*k for k in np.arange(int(dynamic_range + 1))[::-10]]
		fig.colorbar(cax, ticks = range_ticks)
		plt.show()

	def write_file(self,filename,prefix=None,overwrite=False):
		data_to_write = {'title' : self.title, 'data' : self.data_array}
		pymusutil.generic_hdf5_write(filename,prefix,overwrite,data_to_write)

	def read_file(self,filename,prefix):
		data_from_file = {'title' : None, 'data' : None}
		res = pymusutil.generic_hdf5_read(filename,prefix,data_from_file)
		print(data_from_file)
		if data_from_file['title'] is None:
			logging.error("title not found in %s:%s " % (filename,prefix))
		else:
			self.title = data_from_file['title'][0]
		if data_from_file['data'] is None:
			logging.error("image data not found in %s:%s " % (filename,prefix))
		else:
			self.data_array = data_from_file['data'][:]


