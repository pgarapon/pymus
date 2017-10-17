import logging
import urllib2
import os
import glob
import h5py
import numpy as np

logging.basicConfig(level=logging.INFO)

def generic_hdf5_write(filename,prefix=None,overwrite=False,fields={}):
	f = h5py.File(filename,"w")
	g_prf = f
	if prefix is not None:
		try:
			g_prf = f[str(prefix)]
		except KeyError:
			g_prf = f.create_group(str(prefix)) 
	for key_name,key_val_array in fields.items():
		if not isinstance(key_val_array,np.ndarray):
			key_val_array = np.array([key_val_array])
		if key_name in g_prf.keys():
			if overwrite:
				del g_prf[key_name]
				g_prf.create_dataset(key_name,data=key_val_array)
		else:
			g_prf.create_dataset(key_name,data=key_val_array)
	f.close()	

def generic_hdf5_read(filename,prefix,data_kv):
	try:
		f = h5py.File(filename,"r")
	except:
		logging.error(" File %s not found " % filename )
		return 0
	g_prf = f
	if prefix is not None:
		try:
			g_prf = f[str(prefix)]
		except KeyError:
			logging.error(" cannot read data for %s at %s " % (filename,prefix))
			return 0
	for key_name in data_kv.keys():
		key_split = key_name.split("/")
		i, g = 1, g_prf
		for key in key_split:
			if key in g.keys():
				g = g[key]
			else:
				logging.error(" No data %s in %s:%s " % ("/".join(key_split[:i]),filename,prefix) )
				continue
			i += 1
		data_kv[key_name] = g[:]
	f.close()
	return 1	

	

	

	

