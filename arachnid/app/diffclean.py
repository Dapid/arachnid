''' Clean particle selection with the view classifier or ViCer

This script (`ara-autoclean`) was designed to post clean an existing particle selection. It requires
that the projections be grouped by view as well as 2D alignment parameters. This can be obtained by
2D-reference free classification or 3D orientation determination.

Notes
=====

 #. Filenames: Must follow the SPIDER format with a number before the extension, e.g. mic_00001.spi. Output files just require the number of digits: `--output sndc_0000.spi`

 #. Parallel Processing - Several micrographs can be run in parallel (assuming you have the memory and cores available). `-p 8` will run 8 micrographs in parallel. 
 
 #. Supports both SPIDER and RELION alignment files - if the alignment comes from pySPIDER, you must specified --scale-spi or set True.

Examples
========

.. sourcecode :: sh
    
    # Run with a disk as a template on a raw film micrograph
    
    $ ara-autoclean -i image_file_0001.spi -a align_file.spi -o output/clean_000.spi -p params.spi -w 10

Critical Options
================

.. program:: ara-autoclean

.. option:: -i <FILENAME1,FILENAME2>, --input-files <FILENAME1,FILENAME2>, FILENAME1 FILENAME2
    
    List of input stack filenames or single input stack filename template
    If you use the parameters `-i` or `--inputfiles` the filenames may be comma or 
    space separated on the command line; they must be comma seperated in a configuration 
    file. Note, these flags are optional for input files; the filenames must be separated 
    by spaces. For a very large number of files (>5000) use `-i "filename*"`

.. option:: -o <FILENAME>, --output <FILENAME>
    
    Output filename for the output embeddings and selection files (prefixed with sel_$output)

.. option:: -p <FILENAME>, --param-file <FILENAME> 
    
    Filename for SPIDER parameter file describing a Cryo-EM experiment

.. option:: -a <FILENAME>, --alignment <FILENAME> 
    
    Input file containing alignment parameters

Useful Options
===============

These options 

.. program:: ara-autoclean

.. option:: --order <INT>
    
    Reorganize views based on their healpix order (overrides the resolution parameter)

.. option:: --prob-reject <FLOAT>
    
    Probablity that a rejected particle is bad

.. option:: --neig <INT>
    
    Number of eigen vectors to use

.. option:: --expected <FLOAT>
    
    Expected fraction of good data

.. option:: --resolution <FLOAT>
    
    Filter to given resolution - requires apix to be set

Customization Options
=====================

Generally, these options do not need to be changed, unless you are giving the program a non-standard input.

.. program:: ara-autoclean
    
.. option:: --disable-rtsq <BOOL>

    Do not use alignment parameters to rotate projections in 2D
    
.. option:: --scale-spi <BOOL>

    Scale the SPIDER translation (if refinement was done by pySPIDER)
    
Testing Options
===============

Generally, these options do not need to be considered unless you are developing or testing the code.

.. program:: ara-autoclean
    
.. option:: --single-view <INT>

    Test the algorithm on a specific view
    
.. option:: --random-view <INT>

    Set number of views to assign randomly, 0 means skip this
    
.. option:: --disable-bispec <BOOL>

    Disable bispectrum feature space
    
.. option:: --nsamples <INT>

    Number of rotational samples
    
.. option:: --angle-range <FLOAT>

    Angular search range

Other Options
=============

This is not a complete list of options available to this script, for additional options see:

    #. :ref:`Options shared by all scripts ... <shared-options>`
    #. :ref:`Options shared by MPI-enabled scripts... <mpi-options>`
    #. :ref:`Options shared by file processor scripts... <file-proc-options>`
    #. :ref:`Options shared by SPIDER params scripts... <param-options>`

.. Created on Sep 21, 2012
.. codeauthor:: Robert Langlois <rl2528@columbia.edu>
'''

from ..core.app import program
from ..core.image import ndimage_file, analysis, ndimage_utility, rotate, ndimage_processor, ndimage_interpolate, preprocess_utility, reproject, reconstruct, manifold
from ..core.image.ctf import correct as ctf_correct
from ..core.metadata import format, format_utility, spider_params, format_alignment
from ..core.parallel import mpi_utility, openmp
from ..core.orient import healpix, orient_utility
import logging, numpy
from sklearn.covariance import MinCovDet, EmpiricalCovariance
import scipy.stats, os

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

def process(input_vals, output, cache_file, scale, scale_range, **extra):#, neig=1, nstd=1.5
    '''Concatenate files and write to a single output file
        
    :Parameters:
    
    input_vals : list 
                 Tuple(view id, image labels and alignment parameters)
    output : str
             Filename for output file
    cache_file : str
                 Location to cache distance matrix
    extra : dict
            Unused key word arguments
                
    :Returns:
    
    filename : str
               Current filename
    '''
    
    _logger.info("Processing view %d"%int(input_vals[0]))
    
    label, align = input_vals[1:]
    filename = label[0] if isinstance(label, tuple) else label[0][0]
    mask = create_mask(filename, **extra)
    
    openmp.set_thread_count(1) # todo: move to process queue
    data = ndimage_processor.read_matrix_from_cache(cache_file)
    if data is None:
        data = ndimage_processor.create_matrix_from_file(label, image_transform, align=align, mask=mask, dtype=numpy.float32, **extra)
        ndimage_processor.write_matrix_to_cache(cache_file, data)
    
    #data -= data.min()
    #data /= data.max()
    openmp.set_thread_count(extra['thread_count'])
    assert(data.shape[0] == align.shape[0])
    if scale < 0.0:
        sigma = numpy.linspace(float(scale_range[0]), float(scale_range[1]), int(scale_range[2]))
        kernel_cum = numpy.zeros((2, sigma.shape[0]))
        tmp = data.copy()
        _logger.info("Start:%f"%(numpy.sum(data)))
        totmax = 2
        totmin = 2
        while (totmax+totmin) > 2:
            kernel_cum[0, :]=-10**sigma
            for i in xrange(kernel_cum.shape[1]):
                tmp[:] = data[:]*kernel_cum[0,i]
                #numpy.multiply(data, scale, tmp)
                numpy.exp(tmp, tmp)
                kernel_cum[1, i] = numpy.sum(tmp)
            for i in xrange(len(sigma)):
                _logger.info("%f,%f  (%f)"%(sigma[i], kernel_cum[1, i], kernel_cum[0, i]))
            totmax = (kernel_cum[1, :].max()==kernel_cum[1, :]).sum()
            totmin = (kernel_cum[1, :].min()==kernel_cum[1, :]).sum()
            if kernel_cum[1, 0] == kernel_cum[1, :].max():
                _logger.info("New range1: %d - %d"%(int(totmax-1), int(kernel_cum.shape[1]-totmin)))
                minval = sigma[totmax-1]
                maxval = sigma[kernel_cum.shape[1]-totmin]
            else:
                _logger.info("New range2: %d - %d"%(int(totmin-1), int(kernel_cum.shape[1]-totmax)))
                minval = sigma[totmax-1]
                maxval = sigma[kernel_cum.shape[1]-totmax]
            _logger.info("New range: %f - %f"%(float(minval), float(maxval)))
            sigma = numpy.linspace(float(minval), float(maxval), int(scale_range[2]))
    if scale != 0.0:
        assert(numpy.alltrue(numpy.isfinite(data)))
        if scale > 0.0: scale = -scale
        data = numpy.multiply(data, scale, data)
        assert(numpy.alltrue(numpy.isfinite(data)))
        data = numpy.exp(data, data)
        assert(numpy.alltrue(numpy.isfinite(data)))
        #data /= data.sum(axis=1)[:, numpy.newaxis]
    else:
        numpy.sqrt(data, data)
    tst = data-data.mean(0)

    feat = embed_sample(tst, **extra)
        
    rsel=None
    if feat is not None:
        sel, rsel, dist = one_class_classification(feat, **extra)
        if isinstance(label, tuple):
            filename, label = label #psi,theta,phi,inplane,tx,ty,defocus
            dist[:] = tst[:, 0]
            mindist = numpy.min(tst, 1)
            format.write_dataset(output, numpy.hstack((sel[:, numpy.newaxis], dist[:, numpy.newaxis], mindist[:, numpy.newaxis], align[:, 0][:, numpy.newaxis], label[:, 1][:, numpy.newaxis], align[:, (3,4,5,1)], feat)), input_vals[0], label, header='select,dist,mindist,rot,group,psi,tx,ty,mirror')
        else:
            dist[:] = tst[:, 0]
            mindist = numpy.min(tst, 1)
            format.write_dataset(output, numpy.hstack((sel[:, numpy.newaxis], dist[:, numpy.newaxis], mindist[:, numpy.newaxis], align[:, 0][:, numpy.newaxis], align[:, (3,4,5,1)], feat)), input_vals[0], label, header='select,dist,mindist,rot,psi,tx,ty,mirror', default_format=format.csv)
        _logger.info("Finished embedding view: %d"%(int(input_vals[0])))
    else:
        _logger.info("Skipping view (too few projections): %d"%int(input_vals[0]))
    
    return input_vals, rsel

def embed_sample(samp, neig, expected, **extra):
    ''' Embed the sample images into a lower dimensional factor space
    
    :Parameters:
    
    samp : array
           2D array where each row is an unraveled image and each column a pixel
    neig : int
           Number of Eigen vectors
    expected : float
               Probability an image does not contain an outlier
    extra : dict
            Unused keyword arguments
    
    :Returns:
    
    feat : array
           2D array where each row is a compressed image and each column a factor
    '''
    
    if expected == 0.0:
        eigv, feat = analysis.pca_fast(samp, samp, neig)[1:]
    else:
        eigv, feat=analysis.dhr_pca(samp, samp, neig, expected, True)
    _logger.info("Eigen: %s"%(",".join([str(v) for v in eigv[:10]])))
    tc=eigv.cumsum()
    _logger.info("Eigen-cum: %s"%(",".join([str(v) for v in tc[:10]])))
    return feat

def one_class_classification(feat, neig, prob_reject, **extra):
    '''Reject outliers using one-class classification based on the mahalanobis distance
    estimate from a robust covariance as calculated by minimum covariance determinant.
    
    :Parameters:
    
    feat : array
           2D array where each row is a compressed image and each column a factor
    neig : int
           Number of Eigen vectors
    prob_reject : float
                  Probability threshold for rejecting outliers
    extra : dict
            Unused keyword arguments
    
    :Returns:
    
    sel : array
          Boolean array for each image
    rsel : array
           Boolean array for each group of rotated images
    dist : array
           Mahalanobis distance from the median for each image
    '''

    feat=feat[:, :neig]
    try:
        robust_cov = MinCovDet().fit(feat)
    except:
        robust_cov = EmpiricalCovariance().fit(feat)
    dist = robust_cov.mahalanobis(feat - numpy.median(feat, 0))
    cut = scipy.stats.chi2.ppf(prob_reject, feat.shape[1])
    sel =  dist < cut
    _logger.debug("Cutoff: %d -- for df: %d | sel: %d"%(cut, feat.shape[1], numpy.sum(sel)))
    rsel = sel
    return sel, rsel, dist

def create_mask(filename, pixel_diameter, apix, **extra):
    ''' Create a disk mask from the input file size, diameter in pixels and target
    pixel size.
    
    :Parameters:
    
    filename : str
               Input image file
    pixel_diameter : int
                     Diameter of mask in pixels
    apix : float
           Pixel spacing
    extra : dict
            Unused keyword arguments
    
    :Returns:
    
    mask : array
           2D array of disk mask
    '''
    
    img = ndimage_file.read_image(filename)
    bin_factor = decimation_level(apix, pixel_diameter=pixel_diameter, **extra)
    shape = numpy.asarray(img.shape, dtype=numpy.float)/bin_factor
    mask = ndimage_utility.model_disk(int(pixel_diameter/2.0/bin_factor), tuple(shape.astype(numpy.int)))
    return mask

def resolution_from_order(apix, pixel_diameter, order, resolution, **extra):
    ''' Estimate a target resolution based on the angular increment. Returns
    new estimate only if less-resolved than the current.
    
    :Parameters:
    
    apix : float
           Pixel spacing
    pixel_diameter : int
                     Diameter of mask in pixels
    order : int
            Healpix order
    resolution : float
                 Current resolution
    extra : dict
            Unused keyword arguments
    
    :Returns:
    
    resolution : float
                 Estimated resolution
    '''
    
    if order == 0 or 1 == 1: return resolution
    res = numpy.tan(healpix.nside2pixarea(order))*pixel_diameter*apix
    if res > resolution: resolution=res
    return resolution

def order_from_resolution(apix, pixel_diameter, resolution, **extra):
    ''' Estimate healpix order from resolution
    
    :Parameters:
    
    apix : float
           Pixel spacing
    pixel_diameter : int
                     Diameter of mask in pixels
    resolution : float
                 Current resolution
    extra : dict
            Unused keyword arguments
    
    :Returns:
    
    order : int
            Healpix order
    '''
    
    theta_delta = numpy.rad2deg( numpy.arctan( resolution / (pixel_diameter*apix) ) )
    _logger.info("Target sampling %f for resolution %f -> %d"%(theta_delta, resolution, healpix.theta2nside(numpy.deg2rad(theta_delta))))
    return healpix.theta2nside(numpy.deg2rad(theta_delta))

def decimation_level(apix, window, **extra):
    '''
    :Parameters:
    
    apix : float
           Pixel spacing
    window : int
             Size of the window in pixels
    extra : dict
            Unused keyword arguments
    
    :Returns:
    
    out : float
          Target downsampling factor
    '''
    
    resolution = resolution_from_order(apix, **extra)
    dec = resolution / (apix*3)
    d = float(window)/dec + 10
    d = window/float(d)
    return min(max(d, 1), 8)

def image_transform(img, i, mask, apix, var_one=True, align=None, disable_rtsq=False, scale_spi=False, ref_vol=None, angs=None, references=None, neighbors=None, ref_projections=None, **extra):
    ''' Transform the image
    
    :Parameters:
    
    img : array
          2D image matrix
    i : int
        Offset into alignment parameters 
    mask : array
           2D array of disk mask
    apix : float
           Pixel spacing 
    var_one : bool
              Normalize image to variance 1 
    align : array
            2D array of alignment parameters
    disable_rtsq : bool
                   Disable rotate/translate image
    scale_spi : bool
                Scale translations before rotate/translate
    ref_vol : array
              3D reference volume reconstructed from the data
    angs : array
           Sampling angles
    extra : dict
            Unused keyword arguments
    
    :Returns:
    
    out : array
          1D representation of the image
    '''
    
    if not disable_rtsq: #psi,theta,phi,inplane,tx,ty,defocus
        if scale_spi:
            img = ndimage_utility.fourier_shift(img, align[i, 4]/apix, align[i, 5]/apix).copy()
        else:
            img = ndimage_utility.fourier_shift(img, align[i, 4], align[i, 5]).copy()
    elif align[i, 0] != 0: img = rotate.rotate_image(img, -align[i, 0])
    if align[i, 1] > 179.999: img = ndimage_utility.mirror(img)
    ndimage_utility.vst(img, img)
    bin_factor = decimation_level(apix, **extra)
    if bin_factor > 1: img = ndimage_interpolate.downsample(img, bin_factor)
    if mask.shape[0] != img.shape[0]:
        _logger.error("mask-image: %d != %d"%(mask.shape[0],img.shape[0]))
    assert(mask.shape[0]==img.shape[0])
    ndimage_utility.normalize_standard_norm(img, mask, var_one, out=img)
    
    #ctfimg = ctf_correct.ctf_model_spi_2d(align[i, -1], img.shape[0], apix=apix, **extra)
    ctfimg = ctf_correct.transfer_function(img.shape, align[i, -1], apix=apix, **extra)
    frame = align[i, :3].copy()
    if ref_vol is not None:
        return distance_from_reference(img, frame, ctfimg, mask, ref_vol, angs)
    elif ref_projections is not None:
        return distance_from_projection(img, frame, ctfimg, mask, ref_projections, angs)
    else:
        return distance_from_neighbor(img, frame, ctfimg, mask, references, align, neighbors[i], bin_factor)

def distance_from_projection(img, frame, ctfimg, mask, ref_projections, angs):
    '''
    '''
    
    dist = numpy.zeros(len(angs), dtype=img.dtype)
    for j in xrange(len(angs)):
        ang1 = angs[j].copy()
        avg = ref_projections[j].copy()
        euler = rotate.rotate_euler(frame, ang1)
        avg = rotate.rotate_image(avg, -(euler[0]+euler[2]))
        ndimage_utility.normalize_standard(avg, mask, False, out=avg)
        avg *= (img*avg).sum()/(avg**2).sum()
        if 1 == 0:
            avg -= img
            numpy.square(avg, avg)
            dist[j] = numpy.sqrt(avg.sum())
        else:
            dist[j] = numpy.sqrt(ctf_correct_distance(img, avg, ctfimg))
    return dist

def distance_from_reference(img, frame, ctfimg, mask, ref_vol, angs):
    '''
    '''
    
    frame2=frame.copy()
    frame[0]=0
    frame = -frame[::-1]
    dist = numpy.zeros(len(angs), dtype=img.dtype)
    for j in xrange(len(angs)):
        ang1 = angs[j].copy()
        ang1[0]=0
        euler = rotate.rotate_euler(frame, ang1)
        avg = reproject.reproject_3q_single(ref_vol, img.shape[0]/2, euler.reshape((1, 3)))[0]
        euler = rotate.rotate_euler(frame2, euler)
        avg = rotate.rotate_image(avg, -(euler[0]+euler[2]))
        ndimage_utility.normalize_standard(avg, mask, False, out=avg)
        avg *= (img*avg).sum()/(avg**2).sum()
        if 1 == 0:
            avg -= img
            numpy.square(avg, avg)
            dist[j] = numpy.sqrt(avg.sum())
        else:
            dist[j] = numpy.sqrt(ctf_correct_distance(img, avg, ctfimg))
    return dist

def distance_from_neighbor(img, frame, ctfimg, mask, references, align, neighbors, bin_factor):
    '''
    '''
    
    dist = numpy.zeros(len(neighbors[1:]), dtype=img.dtype)
    for j, neigh in enumerate(neighbors[1:]):
        euler = rotate.rotate_euler(frame, align[neigh, :3].copy())
        avg = rotate.rotate_image(references[neigh], -(euler[0]+euler[2]))
        ndimage_utility.normalize_standard(avg, mask, False, out=avg)
        if bin_factor > 1: avg = ndimage_interpolate.downsample(avg, bin_factor)
        avg *= (img*avg).sum()/(avg**2).sum()
        dist[j] = numpy.sqrt(ctf_correct_distance(img, avg, ctfimg))
    return dist

def ctf_correct_distance(img, ref, ctfimg):
    '''
    '''
    
    zimg = ctfimg.copy()
    zimg[:] = 1+1j
    img = ctf_correct.correct(img.copy(), zimg, True)
    ref = ctf_correct.correct(ref, ctfimg, True)
    #img = ctf_correct.correct_model(img, None, True)
    #ref = ctf_correct.correct_model(ref, ctfimg, True)
    tmp=numpy.subtract(img, ref, ref)
    numpy.abs(tmp, tmp)
    numpy.square(tmp,tmp)
    d = numpy.sum(tmp).real
    return d

def group_by_reference(label, align, ref):
    ''' Group alignment entries by view number
    
    :Parameters:
    
    label : array
            2D integer array where rows are images and columns are file ID, slice ID
    align : array
            2D float array for alignment parameters where rows are images and columns alignment parameters
    ref : array
            1D integer array containing the group number for each image
    
    :Returns:
    
    group : list
            List of tuples (view, selected label, selected align)
    '''
    
    group=[]
    refs = numpy.unique(ref)
    if isinstance(label, tuple):
        filename, label = label
        _logger.info("Processing %d projections from %d stacks grouped into %d views"%(len(label), len(numpy.unique(label[:, 0])), len(refs)))
        for r in refs:
            sel = r == ref
            group.append((r, (filename, label[sel]), align[sel]))
    else:
        stack_count = {}
        for i in xrange(len(label)):
            if label[i][0] not in stack_count: 
                stack_count[label[i][0]]=1 
        stack_count = len(stack_count)
        _logger.info("Processing %d projections from %d stacks grouped into %d views - no spi"%(len(label), stack_count, len(refs)))
        for r in refs:
            sel = r == ref
            group.append((r, [label[i] for i in numpy.argwhere(sel).squeeze()], align[sel]))
    return group

def read_alignment(files, alignment="", order=0, random_view=0, disable_mirror=False, **extra):
    ''' Read alignment parameters
    
    :Parameters:
    
    files : list
            List of input files containing particle stacks
    alignment : str
                Input filename containing alignment parameters
    order : int
            Healpix resolution
    random_view : int
                  Assign projections to given number of random views (0 disables)
    disable_mirror : bool
                     Flag to disable mirroring
    extra : dict
            Unused keyword arguments
    
    :Returns:
    
    files : list
            List of filename, index tuples
    align : array
            2D array of alignment parameters
    ref : array
          1D array of view groups
    '''

    files, align = format_alignment.read_alignment(alignment, files[0], use_3d=True, align_cols=8)
    align[:, 7]=align[:, 6]
    if order > 0: orient_utility.coarse_angles(order, align, half=not disable_mirror, out=align)
    if random_view == 1:
        ref = numpy.zeros(len(align), dtype=numpy.int)
    elif random_view>0:
        ref = numpy.random.randint(0, random_view, len(align))
    else:
        ref = align[:, 6].astype(numpy.int)
    return files, align, ref

def init_root(files, param):
    # Initialize global parameters for the script
    
    spider_params.read(param['param_file'], param)
    if param['order'] < 0:
        param['order'] = order_from_resolution(**param)
    
    _logger.info("Pixel size: %f"%param['apix'])
    _logger.info("Window size: %f"%param['window'])
    if param['scale_spi']: _logger.info("Scaling translations by pixel size (pySPIDER input)")
    if param['resolution'] > 0.0: _logger.info("Filter and decimate to resolution %f by a factor of %f"%(resolution_from_order(**param), decimation_level(**param)))
    if not param['disable_rtsq']: _logger.info("Rotate and translate data stack")
    _logger.info("Rejection precision: %f"%param['prob_reject'])
    _logger.info("Number of Eigenvalues: %f"%param['neig'])
    if param['order'] > 0: _logger.info("Angular order %f sampling %f degrees "%(param['order'], healpix.nside2pixarea(param['order'], True)))
    #_logger.info("nsamples: %f"%param['nsamples'])
        
    param['sel_by_mic']={}
    _logger.info("Reading alignment file and grouping projections")
    label, align, ref = read_alignment(files, **param)
    group = group_by_reference(label, align, ref)
    _logger.info("Created %d groups"%len(group))
    if param['single_view'] > 0:
        _logger.info("Using single view: %d"%param['single_view'])
        tmp=group
        group = [tmp[param['single_view']-1]]
    else:
        count = numpy.zeros((len(group)))
        for i in xrange(count.shape[0]):
            if isinstance(group[i][1], tuple):
                count[i] = len(group[i][1][1])
            else:
                count[i] = len(group[i][1])
        index = numpy.argsort(count)
        newgroup=[]
        for i in index[::-1]:
            if count[i] > 20:
                newgroup.append(group[i])
        group=newgroup
    
    # 1. Calculate nn
    # 2. Calculate local average - sample variance
    if param['local_neighbors'] > 0:
        param['references'], param['neighbors'] = generate_local_neighbor_references(label, align, **param)
        openmp.set_thread_count(param['thread_count'])
    elif param['all_views']:
        param['ref_projections'], param['angs'] = generate_reference_projections(label, align, **param)
    else:
        _logger.info("Reconstructing volume")
        param['ref_vol'] = reconstruct_volume(label, align, **param)
        _logger.info("Reconstructing volume - finished")
        param['angs'] = healpix.angles(param['ang_order'], True, out=numpy.zeros((param['ang_limit'],3)))
        
    _logger.info("Processing %d groups - after removing views with less than 20 particles"%len(group))
    return group

def get_batch(batch):
    '''
    '''
    try: import psutil
    except: 
        _logger.exception("Failed to import psutil")
        return min(batch, 10000)
    
    def batch_size(dtype):
        _logger.info("Batch: %f (free) -> %d"%(psutil.virtual_memory().free, int(psutil.virtual_memory().free/dtype.itemsize)))
        return int(numpy.sqrt(float(psutil.virtual_memory().free/dtype.itemsize)))
    return batch_size
    
def generate_local_neighbor_references(label, align, local_neighbors, output, cache_file, batch=0, local_sample=0, **extra):
    '''
    '''
    
    extra['thread_count'] = max(extra.get('worker_count', 0), extra.get('thread_count', 0))
    extra['worker_count'] = extra['thread_count']
    ang = align[:, :3].copy()
    ang[:, 0]=0
    quat=orient_utility.spider_to_quaternion(ang, True)
    _logger.info("Finding nearest neighbors")
    openmp.set_thread_count(extra['thread_count'])
    batch = get_batch(batch)
    neigh = manifold.knn_geodesic_cache(quat, local_neighbors, cache_file=format_utility.add_prefix(cache_file, 'nn_'), batch=batch)
    _logger.info("Finding nearest neighbors - finished")
    openmp.set_thread_count(1)
    _logger.info("Read data")
    samp = ndimage_processor.image_array_from_file(label, preprocess_utility.phaseflip, param=align, dtype=numpy.float32, **extra)
    _logger.info("Read data - finished")
    _logger.info("Average nearest neighbors")
    neigh = neigh.col.reshape((samp.shape[0], local_neighbors+1))
    
    if local_sample > 0:
        samp_file = format_utility.add_prefix(cache_file, 'samp_')
        if os.path.exists(samp_file):
            _logger.info("Searching for cache file: %d == %d"%(ndimage_file.count_images(samp_file), len(samp)))
        if os.path.exists(samp_file) and ndimage_file.count_images(samp_file) == len(samp):
            samp = ndimage_file.read_stack(samp_file)
        else: 
            samp = local_neighbor_subsample(samp, neigh, align, local_sample) # Wrong, needs to rotate!
            ndimage_file.write_stack(samp_file, samp)#[numpy.random.randint(0, len(samp), 10)]
    else:
        avg_file = format_utility.add_prefix(cache_file, 'avg_')
        _logger.info("Searching for cache file: %s"%avg_file)
        _logger.info("Searching for cache file: %d"%os.path.exists(avg_file))
        if os.path.exists(avg_file):
            _logger.info("Searching for cache file: %d == %d"%(ndimage_file.count_images(avg_file), len(samp)))
        if os.path.exists(avg_file) and ndimage_file.count_images(avg_file) == len(samp):
            samp = ndimage_file.read_stack(avg_file)
        else: 
            samp = local_neighbor_average(samp, neigh, align) # Wrong, needs to rotate!
            ndimage_file.write_stack(avg_file, samp)#[numpy.random.randint(0, len(samp), 10)]
    _logger.info("Average nearest neighbors - finished")
    return samp, neigh

def local_neighbor_average(samp, neigh, align):
    '''
    '''
    
    avgsamp = numpy.empty_like(samp)
    avgsamp[:]=samp[:]
    for i in xrange(samp.shape[0]):
        frame = align[neigh[i, 0], :3].copy()
        for j in neigh[i, 1:]:
            euler = rotate.rotate_euler(frame, align[j, :3].copy())
            img = rotate.rotate_image(samp[j], -(euler[0]+euler[2]))
            avgsamp[i]+=img
    return avgsamp

def local_neighbor_subsample(samp, neigh, align, sample_size):
    '''
    '''
    
    avgsamp = numpy.empty_like(samp)
    avgsamp[:]=samp[:]
    for i in xrange(samp.shape[0]):
        frame = align[neigh[i, 0], :3].copy()
        nn = neigh[i, 1:].copy()
        numpy.random.shuffle(nn)
        for j in nn[:sample_size]:
            euler = rotate.rotate_euler(frame, align[j, :3].copy())
            img = rotate.rotate_image(samp[j], -(euler[0]+euler[2]))
            avgsamp[i]+=img
    return avgsamp

def generate_reference_projections(label, align, ang_order, **extra):
    '''
    '''
    
    vol = reconstruct_volume(label, align, **extra)
    angs = healpix.angles(ang_order, True)
    thread_count = max(extra.get('worker_count', 0), extra.get('thread_count', 0))
    return reproject.reproject_3q_mp(vol, vol.shape[0]/2, angs, thread_count=thread_count), angs

def reconstruct_volume(label, align, worker_count, output, **extra):
    ''' Reconstruct a volume from the label and alignment parameters
    
    :Parameters:
    
    label : array
            2D integer array where rows are images and columns are file ID, slice ID
    align : array
            2D float array for alignment parameters where rows are images and columns alignment parameters
    worker_count : int
                   Number of workers to use to reconstruct the volume
    extra : dict
            Unused keyword arguments
    
    :Returns:
    
    vol : array
          3D volume reconstructed from the data
    '''
    
    output_vol = format_utility.add_prefix(output, 'vol_')
    filename = label[0] if isinstance(label, tuple) else ndimage_file.read_image(label[0][0])
    image_size = ndimage_file.read_image(filename).shape[0]
    iter_single_images = ndimage_file.iter_images(label)
    extra['bin_factor'] = decimation_level(**extra)
    image_size = int(float(image_size)/extra['bin_factor'])
    if os.path.exists(output_vol):
        vol = ndimage_file.read_image(output_vol)
        if vol.shape[0] == image_size: return vol
    extra['thread_count'] = max(worker_count, extra.get('thread_count', 0))
    vol = reconstruct.reconstruct_bp3f_mp(iter_single_images, image_size, align, process_image=preprocess_utility.phaseflip_align2d_decimate, **extra).T.copy()
    ndimage_file.write_image(output_vol, vol)
    return vol

def update_selection_dict(sel_by_mic, label, sel):
    ''' Maps selections from view to stack in a dictionary
    
    :Parameters:
    
    sel_by_mic : dict
                 Dictionary to update
    label : tuple or list 
            If tuple (filename, label), otherwise list of tuples [(filename, index)]
    sel : array
          Boolean array defining selections
    '''
    
    if isinstance(label, tuple):
        label = label[1]
        for i in numpy.argwhere(sel):
            sel_by_mic.setdefault(int(label[i, 0]), []).append(int(label[i, 1]+1))
    else:
        for i in numpy.argwhere(sel):
            sel_by_mic.setdefault(label[i][0], []).append(int(label[i][1])+1)

def initialize(files, param):
    # Initialize global parameters for the script
    
    if not mpi_utility.is_root(**param): 
        spider_params.read(param['param_file'], param)

def reduce_all(val, sel_by_mic, id_len=0, **extra):
    # Process each input file in the main thread (for multi-threaded code)
    
    _logger.info("Reducing to root selections")
    input, sel = val
    label = input[1]
    update_selection_dict(sel_by_mic, label, sel) 
    tot=numpy.sum(sel)
    total = len(label[1]) if isinstance(label, tuple) else len(label)
    return "%d - Selected: %d -- Removed %d"%(input[0], tot, total-tot)

def finalize(files, output, sel_by_mic, finished, thread_count, neig, input_files, **extra):
    # Finalize global parameters for the script
    
            
    for filename in finished:
        label = filename[1]
        data, header = format.read(output, ndarray=True, spiderid=int(filename[0]))
        feat = data[:, 6:]
        sel, rsel = one_class_classification(feat, neig=neig, **extra)[:2]
        _logger.info("Read %d samples and selected %d from finished view: %d"%(feat.shape[0], numpy.sum(rsel), int(filename[0])))
        sindex = header.index('select')
        for j in xrange(len(feat)):
            data[j, sindex] = sel[j]
        format.write(output, data, spiderid=int(filename[0]), header=header)
        update_selection_dict(sel_by_mic, label, rsel)
    tot=0
    for id, sel in sel_by_mic.iteritems():
        n=len(sel)
        tot+=n
        _logger.info("Writing %d to selection file %d"%(n, id))
        sel = numpy.asarray(sel)
        format.write(output, numpy.vstack((sel, numpy.ones(sel.shape[0]))).T, prefix="sel_", spiderid=id, header=['id', 'select'], default_format=format.spidersel)
    _logger.info("Selected %d projections"%(tot))
    _logger.info("Completed")

def setup_options(parser, pgroup=None, main_option=False):
    # Collection of options necessary to use functions in this script
    
    from ..core.app.settings import OptionGroup
    group = OptionGroup(parser, "ViCer", "Particle verification with View Classifier or ViCer",  id=__name__)
    group.add_option("", resolution=40.0,           help="Filter to given resolution - requires apix to be set")
    group.add_option("", disable_rtsq=False,        help="Do not use alignment parameters to rotate projections in 2D")
    group.add_option("", neig=2,                    help="Number of eigen vectors to use", dependent=False)
    group.add_option("", expected=0.8,              help="Expected fraction of good data", dependent=False)
    group.add_option("", scale_spi=False,           help="Scale the SPIDER translation (if refinement was done by pySPIDER")
    group.add_option("", single_view=0,             help="Test the algorithm on a specific view")
    group.add_option("", random_view=0,             help="Assign each projection to a random view group (if 1, assign to single group)")
    group.add_option("", order=0,                   help="Reorganize views based on their healpix order (overrides the resolution parameter)")
    group.add_option("", prob_reject=0.97,          help="Probablity that a rejected particle is bad", dependent=False)
    group.add_option("", ang_order=8,               help="Angular increment healpix order")
    group.add_option("", ang_limit=100,             help="Number of projections")
    group.add_option("", disable_mirror=False,      help="Disable mirroring and consider the full sphere in SO2")
    group.add_option("", cache_file="",             help="Cache the raw distances to a file for reuse")
    group.add_option("", scale=0.0,                 help="Scale the distance matrix using the RBF kernel")
    group.add_option("", scale_range=[-8.0,8.0,100],help="Range to search for scale")
    group.add_option("", local_neighbors=0,         help="Generate references from local neighborhood averaging")
    group.add_option("", local_sample=0,            help="Subsample the local neighbors")
    group.add_option("", batch=0,                   help="Size of image batch to process in parallel")
    group.add_option("", all_views=False,           help="Generate all reference views")
    
    
    pgroup.add_option_group(group)
    if main_option:
        pgroup.add_option("-i", input_files=[], help="List of filenames for the input micrographs", required_file=True, gui=dict(filetype="file-list"))
        pgroup.add_option("-o", output="",      help="Output filename for the coordinate file with with no digits at the end (e.g. this is bad -> sndc_0000.spi)", gui=dict(filetype="save"), required_file=True)
        pgroup.add_option("-a", alignment="",   help="Input file containing alignment parameters", required_file=True, gui=dict(filetype="open"))
        spider_params.setup_options(parser, pgroup, True)

def main():
    #Main entry point for this script
    program.run_hybrid_program(__name__,
        description = '''Clean a particle selection of any remaning bad windows
                        
                        Example:
                         
                        $ %prog input-stack.spi -o view_001.dat -p params.spi -a alignment.spi -w 4
                        
                        nohup %prog -c $PWD/$0 > `basename $0 cfg`log &
                        exit 0
                        
                      ''',
        use_version = True,
        supports_OMP=True,
    )

def dependents(): return []
if __name__ == "__main__": main()

