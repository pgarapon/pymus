# PYMUS

A python package for medical ultrasound imaging 

Load experimental setup (probe details, sequence, scanning region) and compute imaging in Plane Wave Compounding mode.

### You will need:

You will need a distribution of Python and several classic python packages, that most likely come with the distribution of Python, or can be easily installed with Pip Install Packages `pip` see [here](https://pip.pypa.io/en/stable/installing/). 

* [Python](https://www.python.org/download/releases/2.7/) - A python distribution ([Conda](https://conda.io/docs/user-guide/install/index.html) is recommended)
* [numpy](http://www.numpy.org/) The classic array library. 
* [scipy](https://www.scipy.org/) Not less classic scientific computation library. 
* [matplotlib](https://matplotlib.org/) A Python plotting/charting library. 

For file I/O we use the hdf5 format, so that python package is required aswell: 

* [h5py](http://www.h5py.org/)

Depending on your system, the install should be as easy as:
```
pip install numpy
```

### Installing

Download the repo to a location of your choice `/Users/YourSelf/projects/pymus`. 

In order for python to have access to different modules at startup, one convenient solution is to create a `pymus.pth` file that would be located at a location of the style:
```
/Users/YourSelf/miniconda2/lib/python2.7/site-packages/pymus.pth
```
To find out about your specific prefix (`/Users/YourSelf/miniconda2/`), run `python` and then `import sys` and then `sys.prefix`. 

The `pymus.pth` file should have just one line that is the absolute path to your `pymus` directory. 


## Building an image

The following test should run a Plane-Wave simplified beamforming and display an echogeinicity of a phantom image. 
``` 
python experiment/test_pymus.py
```

## Documentation 

## Authors

* **Pierre Garapon** - *Initial work* - [pgarapon](https://github.com/pgarapon)

This project is based on porting to python the matlab project [Picmus](https://www.creatis.insa-lyon.fr/Challenge/IEEE_IUS_2016/home). The Plane Wave Imaging Challenge in Medical UltraSound. See the following paper:

*Liebgott, H., Rodriguez-Molares, A., Jensen, J.A., Bernard, O., "Plane-Wave Imaging Challenge in Medical Ultrasound", in IEEE International Ultrasonics Symposium, Tours, France., 2016, p. accepted

See also the list of [contributors](https://github.com/pymus/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* The Medical ultrasound community and the folks at INSA Lyon for exposing some datasets. [Creatis](https://www.creatis.insa-lyon.fr/site7/fr)
* The Python community for an ever growing suite of efficient tools. 

