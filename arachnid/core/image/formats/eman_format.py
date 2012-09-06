''' Use EMAN2/Sparx to read or write to a file


The following formats are supported for reading:

============= ==============
MRC           IMAGIC
SPIDER        HDF5
PIF           ICOS
VTK           PGM
Amira         Video-4-Linux
Gatan DM2     Gatan DM3
TIFF          Scans-a-lot
LST           PNG
============= ==============

The image writing interface selects the image format based on the file extension.  The following table
lists each supported extension with its corresponding file format.

+--------------+-------------------------------------+-+--------------+------------------------------+
|  Extension   |   Format                            | | Extension    |   Format                     |
+==============+=====================================+=+==============+==============================+
| rec,  mrc,   |                                     | | img, IMG     |                              |
| MRC,  ALI,   |   `MRC`_                            | | hed, HED     | `IMAGIC`_                    |
| tnf,  TNF,   |                                     | | imagic       |                              |
| ccp4, map    |                                     | | IMAGIC       |                              |
+--------------+-------------------------------------+-+--------------+------------------------------+
| spi, SPI,    |                                     | | spidersingle |                              |
| spider,      |  `Spider Stack`_                    | | SPIDERSINGLE |  `Spider Image`_             |
| SPIDER       |                                     | | singlespider |                              |
|              |                                     | | SINGLESPIDER |                              |
+--------------+-------------------------------------+-+--------------+------------------------------+
| jpg, JPG,    | `JPEG Image Format`_                | |  png,  PNG   | `Portable Network Graphics`_ |
| jpeg, JPEG   |                                     | |              |                              |
+--------------+-------------------------------------+-+--------------+------------------------------+
| vtk, VTK     | `Visualization Toolkit`_            | | xplor, XPLOR | `X-Plor File Format`_        |
+--------------+-------------------------------------+-+--------------+------------------------------+
| h5,   H5,    |`Hierarchical Data Format`_          | | map, MAP     | `ICOS Image Format`_         |
| hdf,  HDF    |                                     | | icos, ICOS   |                              |
+--------------+-------------------------------------+-+--------------+------------------------------+
| am, AM,      | `AMIRA Image Format`_               | | pif,  PIF    | `Portable Image Format`_     |
| amira, AMIRA |                                     | |              | For EM data                  |
+--------------+-------------------------------------+-+--------------+------------------------------+
| lst,  LST    | List of Image Files                 | | pgm,  PGM    | `Portable Gray Map`_         |
| lsx,  LSX    |                                     | |              |                              |
+--------------+-------------------------------------+-+--------------+------------------------------+

.. _`X-Plor File Format`: http://nmr.cit.nih.gov/xplor-nih/
.. _`MRC`: http://www2.mrc-lmb.cam.ac.uk/
.. _`IMAGIC`: http://imagescience.de/imagic/
.. _`Gatan Image Format`: http://www.gatan.com/
.. _`Spider Stack`: http://www.wadsworth.org/spider_doc/spider/docs/spider.html
.. _`Spider Image`: http://www.wadsworth.org/spider_doc/spider/docs/spider.html
.. _`Visualization Toolkit`: http://www.vtk.org/
.. _`Hierarchical Data Format`: http://www.hdfgroup.org/HDF5/
.. _`Portable Gray Map`: http://netpbm.sourceforge.net/doc/pgm.html
.. _`AMIRA Image Format`: http://www.amira.com/
.. _`JPEG Image Format`: http://www.jpeg.org/
.. _`Flexible Image Transport System`: http://heasarc.gsfc.nasa.gov/docs/heasarc/fits.html
.. _`Portable Image Format`: http://cryoem.ucsd.edu/programs.shtm
.. _`Portable Network Graphics`: http://www.libpng.org/pub/png/
.. _`Tagged Image File Format`: http://www.libtiff.org/
.. _`Video For Linux`: http://linuxtv.org/wiki/index.php/Main_Page
.. _`ICOS Image Format`: http://www.mosaic.ethz.ch/research/projects/closed
.. _`Frealign`: http://emlab.rose2.brandeis.edu/frealign

.. Created on Aug 11, 2012
.. codeauthor:: Robert Langlois <rl2528@columbia.edu>
'''
from .. import eman2_utility, ndimage
from spider import _update_header
import numpy, logging, struct

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

eman2ara={'': ''}
ara2eman=dict([(val, key) for key,val in eman2ara.iteritems()])

def is_readable(filename):
    ''' Test if the input filename of the image is in a recognized
    format.
    
    :Parameters:
    
    filename : str
               Input filename to test
    
    :Returns:
    
    read : bool
           True if the format is recognized
    '''
    
    _logger.debug("Test if read: %s"%filename)
    try: return eman2_utility.EMAN2.EMUtil.get_image_type(filename) != eman2_utility.EMAN2.EMUtil.ImageType.IMAGE_UNKNOWN
    except: return False
    
def read_header(filename, index=None):
    ''' Read the SPIDER header
    
    :Parameters:
    
    filename : str or file object
               Filename or open stream for a file
    index : int, optional
            Index of image to get the header, if None, the stack header (Default: None)
    
    :Returns:
        
    out : array
          Array with header information in the file
    '''
    
    try: "+"+filename
    except: raise ValueError, "EMAN2/Sparx formats do not support file streams"
    if not is_readable(filename): raise IOError, "Format not supported by EMAN2/Sparx"
    _logger.debug("Create emdata object")
    emdata = eman2_utility.EMAN2.EMData()
    _logger.debug("Read image from index: %s"%str(index))
    if index is None: emdata.read_image_c(filename)
    else: emdata.read_image_c(filename, index)
    
    _logger.debug("Get pixel size")
    header = numpy.zeros(1, dtype=ndimage._header)
    header[0].apix = emdata.get_attr('apix_x')
    _logger.debug("Finished read_header")
    return header

def read_image(filename, index=None, header=None, cache=None):
    '''Read an image from an EMAN2/Sparx supported format
    
    :Parameters:
    
    filename : str
               Input filename to read
    index : int, optional
            Index of image to get, if None, first image (Default: None)
    header : dict, optional
             Output dictionary to place header values
    cache : EMData
             Cached image data object
    
    :Returns:
        
    out : array
          Array with header information in the file
    '''
    
    try: "+"+filename
    except: raise ValueError, "EMAN2/Sparx formats do not support file streams"
    if not is_readable(filename): raise IOError, "Format not supported by EMAN2/Sparx"
    emdata = eman2_utility.EMAN2.EMData() if cache is None else cache
    if index is None: emdata.read_image_c(filename)
    else: emdata.read_image_c(filename, index)
    if header is not None: _update_header(emdata.todict(), header, eman2ara)
    type = eman2_utility.EMAN2.EMUtil.get_image_type(filename)
    if type == eman2_utility.EMAN2.EMUtil.ImageType.IMAGE_MRC:
        try: mrc_label = emdata.get_attr('MRC.label0')
        except: mrc_label = ""
        if (mrc_label.find('IMAGIC') != -1 and mrc_label.find('SPIDER') != -1):
            _logger.debug("Flipping MRC")
            emdata.process_inplace("xform.flip",{"axis":"y"})
    data = eman2_utility.em2numpy(emdata)
    if cache is None: data = data.copy()
    return data

def iter_images(filename, index=None, header=None):
    ''' Read a set of SPIDER images
    
    :Parameters:
    
    filename : str
               Input filename to read
    index : int, optional
            Index of image to start, if None, start with the first image (Default: None)
    header : dict, optional
             Output dictionary to place header values
    
    :Returns:
        
    out : array
          Array with header information in the file
    '''
    
    try: "+"+filename
    except: raise ValueError, "EMAN2/Sparx formats do not support file streams"
    if not is_readable(filename): raise IOError, "Format not supported by EMAN2/Sparx"
    if index is None: index = 0
    emdata = eman2_utility.EMAN2.EMData()
    count = count_images(filename)
    if index >= count: raise IOError, "Index exceeds number of images in stack: %d < %d"%(index, count)
    
    update_header=True
    for i in xrange(index, count):
        img = read_image(filename, i, header, emdata)
        if update_header:
            update_header=False
        yield img
    
def count_images(filename):
    ''' Count the number of images in the file
    
    :Parameters:
    
    filename : str
               Input filename to read
    
    :Returns:
        
    out : int
          Number of images in the file
    '''
    
    try: "+"+filename
    except: raise ValueError, "EMAN2/Sparx formats do not support file streams"
    if not is_readable(filename): raise IOError, "Format not supported by EMAN2/Sparx"
    return eman2_utility.EMAN2.EMUtil.get_image_count(filename)

def is_writable(filename):
    ''' Test if the image extension of the given filename is understood
    as a writable format.
    
    :Parameters:
    
    filename : str
               Output filename to test
    
    :Returns:
    
    write : bool
            True if the format is recognized
    '''
    
    ext = eman2_utility.EMAN2.Util.get_filename_ext(filename)
    try:
        type = eman2_utility.EMAN2.EMUtil.get_image_ext_type(ext)
        return type != eman2_utility.EMAN2.EMUtil.ImageType.IMAGE_UNKNOWN
    except: return False

def write_image(filename, img, index=None, header=None, type=None):
    ''' Write the given image to the given filename using a format
    based on the file extension, or given type.
    
    :Parameters:
    
    filename : str
               Output filename for the image
    img : array
          Image data to write out
    index : int, optional
            Index image should be written to in the stack
    header : dict, optional
             Dictionary of header values
    type : eman2_utility.EMAN2.EMUtil.ImageType, optional
           Format in which to write image
    '''
    
    try: "+"+filename
    except: raise ValueError, "EMAN2/Sparx formats do not support file streams"
    if not eman2_utility.is_em(img): 
        _logger.debug("Converting numpy array to EMData")
        img = eman2_utility.numpy2em(img)
    h={}
    _logger.debug("Updating the header")
    header=_update_header(h, header, ara2eman)
    for key, val in header.iteritems(): img.set_attr(key, val)
    if type is None:
        _logger.debug("Determine type of file from extension")
        type = eman2_utility.EMAN2.EMUtil.get_image_ext_type(eman2_utility.EMAN2.Util.get_filename_ext(filename))
    _logger.debug("Using type: %d"%type)
    if type == eman2_utility.EMAN2.EMUtil.ImageType.IMAGE_MRC: 
        _logger.debug("MRC - must flip")
        img.process_inplace("xform.flip",{"axis":"y"})
    if type == eman2_utility.EMAN2.EMUtil.ImageType.IMAGE_UNKNOWN: 
        _logger.debug("Type unknow - assume spider stack")
        type = eman2_utility.EMAN2.EMUtil.ImageType.IMAGE_SPIDER
    if index is None:
        if type == eman2_utility.EMAN2.EMUtil.ImageType.IMAGE_SPIDER:
            _logger.debug("Type SPIDER stack - switch to SINGLE spider")
            type = eman2_utility.EMAN2.EMUtil.ImageType.IMAGE_SINGLE_SPIDER
        index = 0
    _logger.debug("Write image")
    img.write_image_c(filename, index, type)
    # Workaround for buggy Montage from doc viewer
    if type == eman2_utility.EMAN2.EMUtil.ImageType.IMAGE_SINGLE_SPIDER:
        _logger.debug("Hacking spider file")
        f = open(filename, 'r+b')
        f.seek(26*4)
        f.write(struct.pack('f', 0.0))
        f.close()
    _logger.debug("Finished write")



