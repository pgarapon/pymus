import setup.pymus_us_dataset as pymus_us_dataset
import setup.pymus_scan_region as pymus_scan_region
import setup.pymus_us_probe as pymus_us_probe
import setup.pymus_us_sequence as pymus_sequence
import result.pymus_image as pymus_image
import processing.pymus_beamforming as pymus_beamforming

import os
pt_exp = os.path.abspath(os.path.dirname(__file__))
TO_PYMUS="/".join(pt_exp.split("/")[:-1]) + "/"
TO_DATA = TO_PYMUS + "data/"

def test_beamformer(pht,nbPW):
	# Loading Scan Region
	scan = pymus_scan_region.ScanRegion()
	scan.read_file(TO_DATA + "scan_region/linear_scan_region.hdf5","scan_region")
	# Loading probe parameters
	probe = pymus_us_probe.UsProbe()
	probe.read_file(TO_DATA + "probe/linear_probe.hdf5","probe")
	# Loading Sequence parameters
	seq = pymus_sequence.UsPWSequence()
	seq.read_file(TO_DATA + "sequence/sequence_nb_pw_%s.hdf5" % nbPW,"sequence")
	# Loading Echo Data
	data = pymus_us_dataset.UsDataSet("dataset_%s_pw" % nbPW,probe,seq)
	data.read_file(TO_DATA + "echo/%s_nb_pw_%s.hdf5" % (pht,nbPW),pht)
	# Load Beamformer
	echo_data = data.data
	print(probe)
	print(seq)
	print(scan)
	print(data)
	beamformer = pymus_beamforming.BeamFormer(scan,probe,"none")
	beamformer.load_apodizer(TO_DATA + "process/apodization_linear_boxcar.hdf5")
	#beamformer.save_apodizer(TO_DATA + "process/apodization_linear_boxcar.hdf5")
	beamformer.beamform(seq,echo_data)
	im_path = TO_PYMUS + "experiment/output/image_%s_bf_%s_PW.hdf5" % (pht,nbPW) 
	beamformer.write_image(im_path)
	#beamformer.show_image()
	img = pymus_image.EchoImage(scan)
	img.read_file(im_path,None)
	img.show_image(dbScale=True,dynamic_range=60)  

if __name__ == "__main__":
	test_beamformer("in_vitro_type1",3)

