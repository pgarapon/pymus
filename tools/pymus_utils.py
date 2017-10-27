import logging
import urllib
import os
import glob
import h5py
import numpy as np

logging.basicConfig(level=logging.INFO)

S_URL_CREATIS_PREFIX = "https://www.creatis.insa-lyon.fr/EvaluationPlatform/picmus/dataset"

pt_exp = os.path.abspath(os.path.dirname(__file__))
TO_PYMUS="/".join(pt_exp.split("/")[:-1]) + "/"
TO_DATA = TO_PYMUS + "data/"
TO_DATA_TEST = TO_DATA + "test/"
TO_DATA_TMP = TO_DATA + "tmp/"

S_PW_CHOICES = [1 + 2*i for i in range(37) ]
S_PHT_CHOICES = ["numerical","in_vitro_type1","in_vitro_type2"]
S_DATA_TYPES = ["scan","sequence","probe","dataset"]

class DataNotSupported(Exception):
	pass 

def download_data(remote_filename,url,local_path,force_download=None):
	if not os.path.exists(local_path):
		try:
			os.makedirs(local_path)
		except Exception as e:
			logging.error(" DIR creation failed %s " % e )
			return 1
	if force_download is None and remote_filename in [ n.split("/")[-1] for n in glob.glob(local_path + "/*") ]:
		logging.info(" File found %s -> %s " % (local_path,remote_filename) )
		return 0
	else:
		f_write = open(local_path  + remote_filename,"wb")
		try:
			f_read = urllib.request.urlopen(url + "/" + remote_filename)
			logging.info(" Downloading %s/%s ... " % (url,remote_filename))
			f_write.write(f_read.read())

		except urllib.error.HTTPError as e:
			logging.error(" HTTP Error - url = %s/%s - ERR = %s " % (url,remote_filename,e) )
			return 1
		except urllib.error.URLError as e:
			logging.error(" URL Error - url = %s/%s - ERR = %s " % (url,remote_filename,e) )
			return 1

	return 0

def download_dataset(filename,path_to):
	dwnld_data = download_data(filename,S_URL_CREATIS_PREFIX,path_to)
	if dwnld_data > 0:
		logging.error(" Error downloading data ")

def creatis_dataset_filename(phantom_selection, nbPW):
	if phantom_selection not in S_PHT_CHOICES or nbPW not in S_PW_CHOICES:
		raise DataNotSupported(" Data request %s %s not supported " % ( phantom_selection,nbPW) )

	return "dataset_rf_%s_transmission_1_nbPW_%s.hdf5" % (phantom_selection,nbPW)

def has_data(prefix,fname):
	spl_str = "%s/" % prefix
	return fname.split("/")[-1] in [ g.split(spl_str)[-1] for g in glob.glob(TO_DATA + "%s*" % spl_str)	]

def generic_hdf5_write(filename,prefix=None,overwrite=False,fields={}):
	f = h5py.File(filename,"w")
	g_prf = f
	if prefix is not None:
		try:
			g_prf = f[str(prefix)]
		except KeyError:
			g_prf = f.create_group(str(prefix)) 
	for key_name,key_val_array in fields.items():
		if isinstance(key_val_array,str):
			key_val_array = np.array(key_val_array).astype(np.string_)
		elif not isinstance(key_val_array,np.ndarray):
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
		try:
			data_kv[key_name] = g[:]
		except:
			data_kv[key_name] = g[()]
	f.close()
	return 1	

	

	

	

