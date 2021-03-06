''' Micrograph alignment for tilt, defocus, or dose fractionated series

This script (`ara-alignmovie`) translationally aligns and then averages a series of image frames to
reduce blur due to thermal drift.

Tips
====

 #. Parallel Processing - Several micrographs can be run in parallel (assuming you have the memory and cores available). 
    `-p 8` will run 8 micrographs in parallel. 
    
 #. A diagnostic power spectra can be written out for each average image using the `--diagnostic-file` option
 
 #. By default, translation coordinates are not written out. This can be enabled by setting the `--translation-file` option.

Examples
========

.. sourcecode :: sh
    
    # Align frames using l2 optimization over decimated data - output average is not decimated
    
    $ ara-alignmovie -i mic_0001.frames.mrc -o avg_mic_0001.dat --bin-factor 2 --gain-file norm_0.mrc
    
    # Align frames using l2 optimization
    
    $ ara-alignmovie -i mic_0001.frames.mrc -o avg_mic_0001.dat --apix 1.2 --resolution 10 --gain-file norm_0.mrc

Critical Options
================

.. program:: ara-alignmovie

.. option:: -i <FILENAME1,FILENAME2>, --input-files <FILENAME1,FILENAME2>, FILENAME1 FILENAME2, --movie-files <FILENAME1,FILENAME2>
    
    List of filenames for the input micrograph frame stacks.
    If you use the parameters `-i` or `--inputfiles` they must be comma separated 
    (no spaces). If you do not use a flag, then separate by spaces. For a 
    very large number of files (>5000) use `-i "filename*"`

.. option:: -o <FILENAME>, --output <FILENAME>, --micrograph-files <FILENAME>
    
    Output filename for the averaged micrograph image. The filename should 
    have the correct number of digits (e.g. sndc_0000.spi).

.. option:: -p <FILENAME>, --param-file <FILENAME> 
    
    Filename for SPIDER parameter file describing a Cryo-EM experiment

.. option:: --gain-file <FILENAME>
    
    Gain reference normalization image, optional but highly recommended

Useful Options
===============

.. option:: --selection-file <FILENAME>
    
    Micrograph selection file

.. option:: --frame-beg <INT>
    
    Index of the first frame to average, 0 means first frame, 1 second and so on

.. option:: --frame-end <INT>
    
    Index of last frame to average, if 0 use last in stack

.. option:: --resolution <FLOAT>
    
    Target resolution to lowpass filter frames

.. option:: --apix <FLOAT>
    
    Pixel size of the image
    
Tunable Options
===============

.. option:: --search-radius <FLOAT>
    
    Maximum search radius

.. option:: --upsampling <FLOAT>
    
    Upsampling factor

.. option:: --gap <INT>
    
    Gap between pairs for L1/L2 alignment

Diagnostic Options
==================

.. option:: --benchmark <BOOL>
    
    Run every alignment algorithm on the same set of micrographs for benchmarking

.. option:: --window-size <INT>
    
    Window size for the diagnostic power spectra periodogram calculation

.. option:: --pad <INT>
    
    Padding for the diagnostic power spectra periodogram calculation

.. option:: --translation-file <FILENAME>
    
    Output filename for the translation coordinates, optional.  The filename should have the correct number of digits (e.g. sndc_0000.spi).

.. option:: --diagnostic-file <FILENAME>
    
    Output filename for the power spectra images, optional.  The filename should have the correct number of digits (e.g. sndc_0000.spi).

.. option:: --waypoint-file <FILENAME>
    
   Output filename for the average with path in color drawn on the micrograph images, optional. The filename should have the correct number of digits (e.g. sndc_0000.spi).

Other Options
=============

This is not a complete list of options available to this script, for additional options see:

    #. :ref:`Options shared by all scripts ... <shared-options>`
    #. :ref:`Options shared by MPI-enabled scripts... <mpi-options>`
    #. :ref:`Options shared by file processor scripts... <file-proc-options>`
    #. :ref:`Options shared by SPIDER params scripts... <param-options>`

.. Created on Dec 19, 2013
.. codeauthor:: Robert Langlois <rl2528@columbia.edu>
.. codeauthor:: Ryan Hyde Smith <rhs2132@columbia.edu>
.. codeauthor:: Hstau Liao <hl2485@columbia.edu>
'''
from ..core.app import program
from ..core.image import ndimage_utility
from ..core.image import enhance as enhance_image
from ..core.image import ndimage_file
from ..core.image import ndimage_interpolate
from ..core.image import ndimage_filter
from ..core.image import affine_transform
from ..core.image import alignment
from ..core.metadata import format
from ..core.metadata import format_utility
from ..core.metadata import spider_params
from ..core.metadata import spider_utility
from ..core.metadata import selection_utility
from ..core.parallel import mpi_utility
from ..core.util import drawing
from ..core.util import plotting
import scipy.fftpack
import scipy.ndimage
import numpy
import logging
import os

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

def process(filename, benchmark=False, **extra):
    '''Concatenate files and write to a single output file
        
    :Parameters:
        
        filename : str
                   Input filename
        extra : dict
                Unused key word arguments
                
    :Returns:
        
        filename : str
                   Current filename
        coords : str
                 Coordinates
    '''
    
    spider_utility.update_spider_files(extra, filename, *extra['outfile_deps'])
    if benchmark:
        coords = benchmark_in_memory(filename, **extra)
    else:
        coords = align_in_memory(filename, **extra)
        
    if len(coords) > 0:
        _logger.info("Writing average")
        write_average(filename, coords, **extra)
        _logger.info("Writing average - finished")
        write_coordinates(coords, **extra)
    return filename, coords

def fft_in_memory(filename, gain_file="", bin_factor=1.0, **extra):
    ''' Precalculate the FFT of each frame in the movie stack.
    
    :Parameters:
    
        filename : str
                   Filename for movie stack
        gain_file : str
                    Filename for gain normalization image
        bin_factor : float
                     Factor to downsample frame images
        extra : dict
                Unused keyword arguments
    
    :Returns:
    
        fourier_frames : list
                         List of Fourier transforms of each frame
    
    .. codeauthor:: Robert Langlois <rl2528@columbia.edu>
    .. codeauthor:: Ryan Hyde Smith <rhs2132@columbia.edu>
    '''
    
    gain = ndimage_file.read_image(gain_file) if gain_file != "" else None
    fourier_frames = []
    _logger.info("Caching FFT in memory")
    for frame in ndimage_file.iter_images(filename):
        frame = frame.astype(numpy.float)
        if gain is not None: numpy.multiply(frame, gain, frame)
        x, y, w, h = get_window(frame, **extra)
        frame = frame[y:y+h, x:x+w].copy()
        enhance_image.normalize_standard(frame, var_one=True, out=frame)
        frame = scipy.fftpack.fft2(frame)
        if bin_factor > 1.0: frame = ndimage_interpolate.resample_fft_fast(frame, bin_factor, True)
        fourier_frames.append(frame)
    return fourier_frames

def align_in_memory(filename, mode=0, **extra):
    ''' Align frames from a movie stack in memory
    
    This function supports the following alignment algorithms:
    
        #. Sequential
        #. L2
    
    :Parameters:
    
        filename : str
                   Filename for movie stack
        mode : int
               Alignment mode: 0) Sequential, 1) L2
        extra : dict
                Unused keyword arguments
    
    :Returns:
    
        trans : array
                Shifts for each movie frame
    
    
    .. codeauthor:: Robert Langlois <rl2528@columbia.edu>
    .. codeauthor:: Ryan Hyde Smith <rhs2132@columbia.edu>
    '''
    
    fourier_frames = fft_in_memory(filename, **extra)
    if mode == 0:
        _logger.info("Sequential alignment")
        trans = align_sequential(fourier_frames, **extra)
    else:
        _logger.info("L2 alignment")
        trans = align_l2(fourier_frames, **extra)
    _logger.info("Alignment finished")
    write_perdiogram(fourier_frames, 0, trans, **extra)
    trans *= extra['bin_factor']
    return trans

def benchmark_in_memory(filename, **extra):
    ''' Benchmark the frame alignment algorithms
    
    This function benchmarks the following alignment algorithms:
    
        #. Trisequential
        #. Sequential
        #. L2
    
    :Parameters:
    
        filename : str
                   Filename for movie stack
        extra : dict
                Unused keyword arguments
    
    :Returns:
    
        trans : array
                Empty list
    
    .. codeauthor:: Robert Langlois <rl2528@columbia.edu>
    .. codeauthor:: Ryan Hyde Smith <rhs2132@columbia.edu>
    '''
    
    fourier_frames = fft_in_memory(filename, **extra)
    avg = average_fft(fourier_frames)
    write_perdiogram(avg, 0, **extra)
    _logger.info("Begin sequential")
    trans = align_sequential(fourier_frames, **extra)
    avg = average_fft(fourier_frames, trans)
    pow1 = write_perdiogram(avg, 1, **extra)
    _logger.info("Begin l2")
    trans = align_l2(fourier_frames, **extra)
    avg = average_fft(fourier_frames, trans)
    pow2=write_perdiogram(avg, 2, **extra)
    _logger.info("Begin mean displacement")
    trans = align_mean_displacement(fourier_frames, **extra)
    avg = average_fft(fourier_frames, trans)
    pow4=write_perdiogram(avg, 4, **extra)
    write_powerspectra_1D((pow1, pow2, pow4), ('Sequential', 'L2', 'Mean'), **extra)
    #trans *= extra['bin_factor']
    return []

def align_mean_displacement(fourier_frames, upsampling=2, search_radius=50, lowpass_sigma=None, **extra):
    '''
    '''
    
    filter_kernel=None
    if lowpass_sigma is not None:
        filter_kernel = scipy.fftpack.ifftshift(ndimage_filter.gaussian_lowpass_kernel(fourier_frames[0].shape, lowpass_sigma, numpy.float))
    else: filter_kernel=1.0
    
    index = numpy.triu_indices(len(fourier_frames), 1)
    cache = numpy.zeros((len(fourier_frames), len(fourier_frames), 3))
    
    for i, j in zip(*index):
        y, x, p = alignment.xcorr_dft_peak(fourier_frames[i]*filter_kernel, fourier_frames[j], upsampling, search_radius)
        cache[i, j] = (x,y,p)
        cache[j, i] = (-x,-y,p)
    
    trans = numpy.zeros((len(fourier_frames), 2))
    idx = numpy.arange(1, len(fourier_frames), dtype=numpy.int)
    for i in xrange(1, trans.shape[0]):
        cidx = idx[idx != i]
        weight = 1.0 #cache[0, cidx, 2]+cache[i, cidx, 2]
        #weight /= weight.sum()
        
        trans[i, :] = numpy.mean(weight*(cache[0, cidx, :2]-cache[i, cidx, :2]), axis=0)
        #print trans[i, :], trans[i]-trans[i-1]
    return trans

def align_sequential(fourier_frames, upsampling=2, search_radius=50, lowpass_sigma=None, **extra):
    '''
    
    @author: Robert Langlois
    '''
    
    filter_kernel=None
    trans = numpy.zeros((len(fourier_frames), 2))
    ref = fourier_frames[0].copy()
    if lowpass_sigma is not None:
        filter_kernel = scipy.fftpack.ifftshift(ndimage_filter.gaussian_lowpass_kernel(ref.shape, lowpass_sigma, numpy.float))
    for i, frame in enumerate(fourier_frames[1:]):
        if filter_kernel is not None: numpy.multiply(ref, filter_kernel, ref)
        y, x, p1 = alignment.xcorr_dft_peak(ref, frame, upsampling, search_radius)
        trans[i+1, :]=(x,y)
        #print i+1, trans[i+1, :], trans[i+1, :]-trans[i, :], p1
        ref += scipy.ndimage.fourier_shift(frame, (-trans[i+1, 1], -trans[i+1, 0]), -1, 0)
    return trans

def align_l2(fourier_frames, upsampling=2, search_radius=50, lowpass_sigma=None, gap=5, **extra):
    '''
    .. codeauthor:: Robert Langlois <rl2528@columbia.edu>
    .. codeauthor:: Ryan Hyde Smith <rhs2132@columbia.edu>
    '''
    
    filter_kernel=None
    if lowpass_sigma is not None:
        filter_kernel = scipy.fftpack.ifftshift(ndimage_filter.gaussian_lowpass_kernel(fourier_frames[0].shape, lowpass_sigma, numpy.float))
    else: filter_kernel=1.0
    
    pairs = []
    for i in xrange(len(fourier_frames)-1):
        for j in xrange(i+gap, len(fourier_frames)):
            assert(numpy.abs(i-j)>=gap)
            pairs.append((i,j))
    A = numpy.zeros((len(pairs), len(fourier_frames)-1))
    for i, p in enumerate(pairs):
        A[i, p[0]:p[1]] = 1
    b = numpy.zeros((len(pairs), 2))
    for i, p in enumerate(pairs):
        b[i, 1], b[i, 0] = alignment.xcorr_dft_peak(fourier_frames[p[0]]*filter_kernel, fourier_frames[p[1]], upsampling, search_radius)[:2]
    x0 = numpy.linalg.lstsq(A, b)[0]
    trans = numpy.zeros((len(fourier_frames), 2))
    trans[1:] = x0.cumsum(axis=0)
    '''
    for i in xrange(trans.shape[0]):
        if i > 0:
            print trans[i], trans[i]-trans[i-1]
        else:
            print trans[i]
    '''
    return trans

def average_fft(fourier_frames, trans=None, do_ifft=True):
    '''
    '''
    
    avg = numpy.zeros_like(fourier_frames[0])
    for i, frame in enumerate(fourier_frames):
        if trans is None:
            avg += frame
        else:
            avg += scipy.ndimage.fourier_shift(frame, (-trans[i, 1], -trans[i, 0]), -1, 0)
    return scipy.fftpack.ifft2(avg).real if do_ifft else avg

def write_average_with_path(avg, trans, waypoint_file="", **extra):
    '''
    '''
    
    if waypoint_file == "": return
    radius = numpy.asarray((avg.shape[1]/2, avg.shape[0]/2))
    trans = trans.copy()
    trans -= trans.min(axis=0)
    trans /= trans.max(axis=0)
    trans *= radius
    trans += radius
    drawing.draw_path(avg, trans, width=10, out=waypoint_file)

def powerspectra(fourier_frames, trans=None, window_size=256, pad=1, overlap=0.5, **extra):
    '''
    '''
    
    avg = numpy.zeros_like(fourier_frames[0])
    for i, frame in enumerate(fourier_frames):
        if trans is not None:
            avg += scipy.ndimage.fourier_shift(frame, (-trans[i, 1], -trans[i, 0]), -1, 0)
        else:
            avg += frame
    avg = scipy.fftpack.ifft2(avg).real
    avg = scipy.fftpack.fft2(avg)
    avg = scipy.fftpack.fftshift(avg).real
    return ndimage_interpolate.downsample(numpy.ascontiguousarray(avg), (window_size, window_size))

def perdiogram(avg, window_size=256, pad=1, overlap=0.5, **extra):
    '''
    '''
    
    return ndimage_utility.perdiogram(avg, window_size, pad, overlap)


def write_powerspectra_1D(pows, labels, diagnostic_file="", dpi=300, **extra):
    '''
    '''
    
    if plotting.is_plotting_disabled(): return
    
    spectra1d = []
    for pow in pows:
        raw = ndimage_utility.mean_azimuthal(pow)[:pow.shape[0]/2]
        spectra1d.append(raw[5:])
    plotting.plot_lines(diagnostic_file, spectra1d, labels, 'CTF', dpi)
    
def write_pow(pow, index=0, diagnostic_file="", apix=None, **extra):
    '''
    '''
    
    
    if diagnostic_file == "": return
    if apix is not None and apix > 0.0 and 1 == 0:
        rmin=30.0
        rmax=apix*3.0
        
        min_freq = apix/rmin
        max_freq = apix/rmax
        
        rang = ((max_freq*pow.shape[0])-(min_freq*pow.shape[0]))/2.0
        freq2 = float(pow.shape[0])/(rang/1)
        freq1 = float(pow.shape[0])/(rang/15)
        pow = ndimage_filter.filter_annular_bp(pow, freq1, freq2)
    
    ndimage_file.write_image(diagnostic_file, pow, index)

def write_perdiogram(avg, index=0, trans=None, diagnostic_file="", **extra):
    '''
    '''
    
    if diagnostic_file == "": return
    if isinstance(avg, list) and trans is not None:
        avg = average_fft(avg, trans)
    pow = perdiogram(avg, **extra)
    write_pow(pow, index, diagnostic_file, **extra)
    return pow

def write_coordinates(coords, translation_file="", **extra):
    ''' Write the coordinates to a text file
    '''
    
    if translation_file == "": return
    coords = numpy.hstack((numpy.arange(len(coords))[:, numpy.newaxis], coords))
    format.write(translation_file, coords, header='id,x,y'.split(','))

def write_average(filename, coords, output, frame_beg=0, frame_end=0, gain_file="", diagnostic_file="", crop=[], line_width=10, **extra):
    ''' Average the frames in the stack using the given 
    translation coordinates.
    '''
    
    gain = ndimage_file.read_image(gain_file) if gain_file != "" else None
    #frame_beg=0, frame_end=0
    if gain is not None:
        avg = gain.copy()
        avg[:]=0
    else: avg = None
    for i, frame in enumerate(ndimage_file.iter_images(filename)):
        frame = frame.astype(numpy.float)
        if gain is not None: frame *= gain
        frame = affine_transform.fourier_shift(frame, -coords[i, 0], -coords[i, 1])
        if avg is None: avg = frame
        else: avg += frame
    avg /= len(coords)
    ndimage_file.write_image(output, avg, header=dict(apix=extra['apix']))
    
    if diagnostic_file != "" and len(crop) > 0 and crop[0] > 0 \
        or (len(crop) > 1 and crop[1] > 0) \
        or (len(crop) > 2 and crop[2] > 0) \
        or (len(crop) > 3 and crop[3] > 0):
        output = format_utility.add_prefix(output, 'diagnostic_win_')
        
        x, y, w, h = get_window(avg, crop)
        mask = numpy.zeros(avg.shape, dtype=numpy.bool)
        mask[:, x:x+line_width]=0
        mask[y:y+line_width, :]=0
        mask[:, x+w:x+line_width+w]=0
        mask[y+h:y+line_width+h, :]=0
        
        ndimage_file.write_image(output, avg)

def get_window(avg, crop=[], **extra):
    '''
    '''
    
    x, y, w, h = 0, 0, -1, -1
    if len(crop) > 0: x = crop[0]
    if len(crop) > 1: y = crop[1]
    if len(crop) > 2: w = crop[2]
    if len(crop) > 3: h = crop[3]
    if w == -1: w = avg.shape[1]
    if h == -1: h = avg.shape[0]
    return x, y, w, h
    

def initialize(files, param):
    # Initialize global parameters for the script
    
    if mpi_utility.is_root(**param):
        n = len(files)
        for filename in param['finished']:
            if not ndimage_file.valid_image(filename): 
                files.append(filename)
        if len(files) > n:
            _logger.warn("Found %d corrupt files - reprocessing them"%(len(files)-n))
    files = mpi_utility.broadcast(files, **param)
    
    if len(files) == 0: return
    count = ndimage_file.count_images(files[0])
    _logger.info("Aligning %d stacks with %d frames in each"%(len(files), count))
    if param['param_file'] != "":
        spider_params.read(param['param_file'], param)
    if param['benchmark']:
        _logger.warn("Running Alignment in Benchmark mode!")
    else:
        _logger.info("Running l2-Alignment")
    if param['diagnostic_file'] != "":
        _logger.info("Writing diagnostic power spectra to %s"%param['diagnostic_file'])
    if param['gain_file']=="":
        _logger.warn("No gain reference!")
    else:
        _logger.info("Gain reference: %s"%param['gain_file'])
    if param['translation_file']=="":
        _logger.warn("No translation coordinate file given!")
    else:
        _logger.info("Output translation coordinate file: %s"%param['translation_file'])
    _logger.info("Decimation factor %f"%param['bin_factor'])
    if param['bin_factor'] > 1.0 and param['param_file'] == "" and param['apix'] > 0:
        apix = param['apix']
        param['apix'] *= float(param['bin_factor'])
        _logger.info("Using scaled pixel size: %f (originally %f)"%(param['apix'], apix))
    else:
        _logger.info("Pixel size: %f"%param['apix'])
    if param['resolution'] > 0.0:
        _logger.info("Filter frames to %f (%f)"%(param['resolution'], param['apix']/param['resolution']))
        param['lowpass_sigma']=param['apix']/param['resolution']
    if not drawing.is_available():
        if param['waypoint_file'] != "":
            _logger.info("Cannot write out illustrative waypoint average - no PIL installed")
            param['waypoint_file']=""
    else:
        if param['waypoint_file'] != "":
            _logger.info("Writing out illustrative waypoint image: %s"%param['waypoint_file'])
    
    if param['output']!="":
        try:os.makedirs(os.path.dirname(param['output']))
        except: pass
    if param['translation_file']!="":
        try:os.makedirs(os.path.dirname(param['translation_file']))
        except: pass
    if param['diagnostic_file']!="":
        try:os.makedirs(os.path.dirname(param['diagnostic_file']))
        except: pass
    if param['waypoint_file']!="":
        try:os.makedirs(os.path.dirname(param['waypoint_file']))
        except: pass
    
    if 'selection_file' in param and param['selection_file'] != "":
        if os.path.exists(param['selection_file']):
            select = format.read(param['selection_file'], numeric=True)
            oldcnt = len(files)
            files = selection_utility.select_file_subset(files, select, param.get('id_len', 0), len(param['finished']) > 0)
            _logger.info("Selecting %d files from %d"%(len(files), oldcnt))
    return files
    
def reduce_all(val, **extra):
    # Process each input file in the main thread (for multi-threaded code)
    
    filename, coords = val
    coords;
    return filename

def finalize(files, **extra):
    # Finalize global parameters for the script
    
    _logger.info("Completed")

def supports(files, **extra):
    ''' Test if this module is required in the project workflow
    
    :Parameters:
    
    files : list
            List of filenames to test
    extra : dict
            Unused keyword arguments
    
    :Returns:
    
    flag : bool
           True if this module should be added to the workflow
    '''
    
    if len(files) > 0 and ndimage_file.count_images(files[0]) > 1:
        return True
    return False

def change_option_defaults(parser):
    ''' Change the values to options specific to the script
    '''
    
    parser.change_default(bin_factor=2)

def check_options(options, main_option=False):
    #Check if the option values are valid
    
    from ..core.app.settings import OptionValueError
    if options.resolution > 0.0 and options.apix == 0.0: 
        raise OptionValueError, "Pixel size required when using resolution to filter (use --param-file or --apix)"

def setup_options(parser, pgroup=None, main_option=False):
    # Collection of options necessary to use functions in this script
    
    from ..core.app.settings import OptionGroup
    group = OptionGroup(parser, "Align Frames", "Options to control frame alignment",  id=__name__)
    group.add_option("", frame_beg=0,       help="Index of the first frame to average, 0 means first frame, 1 second and so on", gui=dict(maximum=10000, minimum=0, singleStep=1))
    group.add_option("", frame_end=0,       help="Index of last frame to average, if 0 use last in stack", gui=dict(maximum=10000, minimum=0, singleStep=1))
    group.add_option("", gain_file="",      help="Gain reference normalization image", gui=dict(filetype="open"))
    group.add_option("", resolution=20.0,   help="Target resolution to lowpass filter frames")
    group.add_option("", apix=0.0,          help="Pixel size of the image")
    group.add_option("", search_radius=50,  help="Maximum search radius")
    group.add_option("", upsampling=2,      help="Upsampling factor")
    group.add_option("", gap=5,             help="Gap between pairs for L1/L2 alignment")
    group.add_option("", mode=("Sequential", "L2"), help="Alignment mode", default=1)
    group.add_option("", crop=[0, 0, -1, -1], help="Window size for the alignment")
    
    dgroup = OptionGroup(parser, "Diagnostic", "Options to control diagnostic output",  id=__name__)
    dgroup.add_option("", benchmark=False,   help="Run every alignment algorithm on the same set of micrographs for benchmarking")
    dgroup.add_option("", window_size=256,   help="Window size for the diagnostic power spectra")
    dgroup.add_option("", pad=2,             help="Padding for the diagnostic power spectra")
    group.add_option_group(dgroup)
    
    pgroup.add_option_group(group)
    if main_option:
        pgroup.add_option("-i", "--movie-files",          input_files=[],           help="List of filenames for the input micrographs, e.g. mic_*.mrc", required_file=True, gui=dict(filetype="open"), regexp=spider_utility.spider_searchpath)
        pgroup.add_option("-o", "--micrograph-files",     output="",                help="Output filename for the averaged micrograph image. The filename should have the correct number of digits (e.g. sndc_0000.spi).", gui=dict(filetype="save"), required_file=True)
        pgroup.add_option("",                             translation_file="",      help="Output filename for the translation coordinates, optional.  The filename should have the correct number of digits (e.g. sndc_0000.spi).", gui=dict(filetype="save"), required_file=False)
        pgroup.add_option("",                             diagnostic_file="",       help="Output filename for the power spectra images, optional.  The filename should have the correct number of digits (e.g. sndc_0000.spi).", gui=dict(filetype="save"), required_file=False)
        pgroup.add_option("",                             waypoint_file="",         help="Output filename for the average with path in color drawn on the micrograph images, optional. The filename should have the correct number of digits (e.g. sndc_0000.spi).", gui=dict(filetype="save"), required_file=False)
        pgroup.add_option("",                             selection_file="",        help="Micrograph selection file", gui=dict(filetype="open"), required_file=False)
        spider_params.setup_options(parser, pgroup, False)

def flags():
    ''' Get flags the define the supported features
    
    :Returns:
    
    flags : dict
            Supported features
    '''
    
    return dict(description = '''Automated movie frame alignment
                        
                        Example: Unprocessed film micrograph
                         
                        $ ara-align-frames movie_stack.spi -o average_image.spi
                      ''',
                supports_MPI=False, 
                supports_OMP=True,
                use_version=True)

def main():
    #Main entry point for this script
    program.run_hybrid_program(__name__)

if __name__ == "__main__": main()

