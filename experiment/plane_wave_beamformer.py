import processing.pymus_beamforming as pymus_beamforming
import setup.pymus_us_dataset as pymus_us_dataset
import setup.pymus_scan_region as pymus_scan_region
import setup.pymus_us_probe as pymus_us_probe
import setup.pymus_us_sequence as pymus_sequence
import result.pymus_image as pymus_image
import tools.pymus_utils as pymus_utils

import numpy as np

import logging
import click
import os
import glob
import numpy as np

class BeamFormingConfig(object):

	def __init__(self,apod_type=None):
		self.scan = pymus_scan_region.ScanRegion()
		self.probe = pymus_us_probe.UsProbe()
		self.sequence = pymus_sequence.UsPWSequence()
		self.data = None
		self.apod = "none"
		if apod_type is not None:
			self.apod = apod_type

		self.load_apod = None
		self.save_apod = None
		self.img_path = None

	def load_settings(self,standard_specs=None,filenames=None):
		if filenames is None and standard_specs is None:
			logging.error(" Provide an input to load settings ")
			return
		if filenames is None:
			nbPW = standard_specs["nbPW"]
			pht = standard_specs["pht_type"]
			scan_source = pymus_utils.TO_DATA + "scan_region/linear_scan_region.hdf5"
			probe_source = pymus_utils.TO_DATA + "probe/linear_probe.hdf5"
			sequence_source = pymus_utils.TO_DATA + "sequence/sequence_nb_pw_%s.hdf5" % standard_specs["nbPW"]
			data_source = pymus_utils.TO_DATA + "echo/%s_nb_pw_%s.hdf5" % (pht,nbPW)
		else:
			if "scan" in filenames.keys():
				scan_source = filenames["scan"]
			if "probe" in filenames.keys():
				probe_source = filenames["probe"]
			if "sequence" in filename.keys():
				sequence_source = filename["sequence"]
			if "data" in filenames.keys():
				data_source = filename["data"]

		if not pymus_utils.has_data("scan",scan_source):
			if filenames is not None and "scan" in filenames.keys():
				logging.error(" unable to load settings from file")
				return
			pymus_scan_region.ImportFromCreatis()

		if not pymus_utils.has_data("probe",probe_source):
			if filenames is not None and "probe" in filenames.keys():
				logging.error(" unable to load settings from file")
				return
			pymus_us_probe.ImportFromCreatis()

		if not pymus_utils.has_data("sequence",sequence_source):
			if filenames is not None and "sequence" in filenames.keys():
				logging.error(" unable to load settings from file")
				return
			pymus_sequence.ImportFromCreatis(nbPW=standard_specs["nbPW"])

		if not pymus_utils.has_data("echo",data_source):
			if filenames is not None and "data" in filenames.keys():
				logging.error(" unable to load settings from file")
				return
			pymus_us_dataset.ImportFromCreatis(nbPW=standard_specs["nbPW"],pht=standard_specs["pht_type"])

		self.scan.read_file(scan_source,"scan_region")
		self.probe.read_file(probe_source,"probe")
		self.sequence.read_file(sequence_source,"sequence")

		self.data = pymus_us_dataset.UsDataSet("dataset_plane_waves",self.probe,self.sequence)
		self.data.read_file(data_source,standard_specs["pht_type"])

		self.im_path = pymus_utils.TO_PYMUS + "experiment/output/image_%s_bf_%s_PW.hdf5" % (standard_specs["pht_type"],standard_specs["nbPW"])
		self.png_path = self.im_path.split(".")[0] + ".png"
				

def plane_wave_beamforming(config):
	beamformer = pymus_beamforming.BeamFormer(config.scan,config.probe,config.apod)
	if config.load_apod is not None:
		beamformer.load_apodizer(pymus_utils.TO_DATA_TEST + "process/%s.hdf5" % config.load_apod)
	if config.save_apod is not None:
		beamformer.save_apodizer(pymus_utils.TO_DATA_TEST + "process/%s.hdf5" % config.save_apod)
	beamformer.beamform(config.sequence,config.data.data)

	logging.info("save contrast image")
	beamformer.write_image(config.im_path)

	logging.info("load and show image")
	img = pymus_image.EchoImage(config.scan)
	img.read_file(config.im_path,None)
	img.show_image(dbScale=True,dynamic_range=60,to_file=config.png_path)  

@click.command()
@click.option('--phantom', default="in_vitro_type1", help='Type of medium to use.')
@click.option('--nbpw', default=3, help='Number of plane waves in illumination.')
def main(phantom,nbpw):
	cfg = BeamFormingConfig()
	cfg.load_settings(standard_specs={"pht_type" : phantom, "nbPW" : nbpw})
	plane_wave_beamforming(cfg)

if __name__ == "__main__":
	main()

