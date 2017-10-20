import setup.pymus_us_dataset as pymus_us_dataset
import setup.pymus_scan_region as pymus_scan_region
import setup.pymus_us_probe as pymus_us_probe
import setup.pymus_us_sequence as pymus_sequence
import result.pymus_image as pymus_image
import processing.pymus_beamforming as pymus_beamforming

import os
import logging

pt_exp = os.path.abspath(os.path.dirname(__file__))
TO_PYMUS="/".join(pt_exp.split("/")[:-1]) + "/"
TO_DATA = TO_PYMUS + "data/"
TO_DATA_TEST = TO_DATA + "test/"

def test_beamformer(pht,nbPW):
	logging.info("Loading Scan Region")
	scan = pymus_scan_region.ScanRegion()
	scf_name = TO_DATA_TEST + "scan_region/linear_scan_region.hdf5"
	scan.read_file(scf_name,"scan_region")
	logging.info(scan)

	logging.info("Loading probe parameters")
	probe = pymus_us_probe.UsProbe()
	prb_name = TO_DATA_TEST + "probe/linear_probe.hdf5"
	probe.read_file(prb_name,"probe")
	logging.info(probe)

	logging.info("Loading Sequence parameters")
	seq = pymus_sequence.UsPWSequence()
	sqc_name = TO_DATA_TEST + "sequence/sequence_nb_pw_%s.hdf5" % nbPW
	seq.read_file(sqc_name,"sequence")
	logging.info(seq)

	logging.info("Loading Echo Data")
	data = pymus_us_dataset.UsDataSet("dataset_%s_pw" % nbPW,probe,seq)
	dst_name = TO_DATA_TEST + "echo/%s_nb_pw_%s.hdf5" % (pht,nbPW) 
	data.read_file(dst_name,pht)
	logging.info(data)

	logging.info("Load Beamformer")
	beamformer = pymus_beamforming.BeamFormer(scan,probe,"none")
	''' load from file or save to file apodiation data

	beamformer.load_apodizer(TO_DATA + "process/apodization_linear_boxcar.hdf5")
	beamformer.save_apodizer(TO_DATA + "process/apodization_linear_boxcar.hdf5")
	'''
	beamformer.beamform(seq,data.data)

	logging.info("save contrast image")
	im_path = TO_PYMUS + "experiment/output/image_%s_bf_%s_PW.hdf5" % (pht,nbPW) 
	beamformer.write_image(im_path)

	logging.info("load and show image")
	img = pymus_image.EchoImage(scan)
	img.read_file(im_path,None)
	img.show_image(dbScale=True,dynamic_range=60)  

if __name__ == "__main__":
	test_beamformer("in_vitro_type1",3)

