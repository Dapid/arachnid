''' Based on CTFFIND3

.. Created on Nov 25, 2013
.. codeauthor:: Robert Langlois <rl2528@columbia.edu>
'''

from arachnid.core.app import tracing
#from .. import ndimage_interpolate
import numpy
import scipy.optimize


import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

try: 
    from ..util import _ctf
    _ctf;
except:
    _ctf=None
    tracing.log_import_error('Failed to load _ctf.so module', _logger)

######################################################################
# CTF FIND3
######################################################################

def search_model_2d(powspec, dfmin, dfmax, fstep, rmin, rmax, ampcont, cs, voltage, pad=1.0, apix=None, xmag=None, res=None, **extra):
    '''
    '''
    
    if rmin < rmax: rmin, rmax = rmax, rmin
    if dfmax < dfmin: dfmin, dfmax = dfmax, dfmin
    if apix is None: apix = res*(10.0**4.0)/xmag
    if rmin > 50: rmin = 50.0
    if rmax > rmin: raise ValueError, "Increase rmax, rmin cannot be greater than 50"
    apix *= pad
    rmin = apix/rmin
    rmax = apix/rmax
    rmin2, rmax2 = rmin**2,rmax**2
    hw = -1.0/rmax2
    print 'Searching CTF Parameters...'
    print '      DFMID1      DFMID2      ANGAST          CC'
    best=(-1e20, None, None, None)
    i1 = int(dfmin/fstep)
    i2 = int(dfmax/fstep)
    cs *= 10**7.0
    kv = voltage*1000.0
    wl = 12.26/numpy.sqrt( kv+0.9785*kv**2/10.0**6.0 )
    
    powspec = powspec.astype(numpy.float32)
    pow_sm = powspec
    thetatr = wl/(apix*min(pow_sm.shape))
    pow_sm = pow_sm.copy()
    pow_sm = pow_sm[:pow_sm.shape[0]/2, :].copy()
    pow_sm = pow_sm.T.copy()
    smooth_2d(pow_sm, rmin)
    
    p=0
    for k in xrange(0, 18):
        for i in xrange(i1, i2+1):
            for j in xrange(i1, i2+1):
                df1, df2, ang = fstep*i, fstep*j, numpy.deg2rad(5.0*k)
                val = eval_model_2d(df1, df2, ang, pow_sm, cs, wl, ampcont, thetatr, rmin2, rmax2, hw)
                #model[:, :]=0
                #val = eval_model_2d_test(df1, df2, ang, powspec, model, cs, wl, ampcont, thetatr, rmin2, rmax2, hw)
                if val > best[0]:  
                    print "%f\t%f\t%f\t%f"%(df1, df2, numpy.rad2deg(ang), val)
                    best=(val, df1, df2, ang)
                p+=1
                
    powspec = pow_sm
    
    def error_func(p0):
        return -eval_model_2d(p0[0], p0[1], p0[2], powspec, cs, wl, ampcont, thetatr, rmin2, rmax2, hw)
    
    vals = scipy.optimize.fmin(error_func, (best[1], best[2], best[3]), disp=1)
    return vals[0], vals[1], vals[2]
    
def smooth_2d(powspec, rmin):
    '''
    '''
    
    n = max(powspec.shape)
    buf = numpy.zeros((n,n), dtype=numpy.float32)
    nw = int(powspec.shape[0]*rmin*numpy.sqrt(2.0))
    size = numpy.asarray(powspec.shape, dtype=numpy.int32)
    _ctf.msmooth(powspec.T, size, int(nw), buf.T)


def eval_model_2d(dfmid1, dfmid2, angast, pow, cs, wl, wgh, thetatr, rmin2, rmax2, hw):
    '''
    '''
    
    n = max(pow.shape)
    return _ctf.evalctf(float(cs), float(wl), float(numpy.sqrt(1.0-wgh*wgh)), float(wgh), float(dfmid1), float(dfmid2), float(angast), float(thetatr), float(hw), pow.T, numpy.asarray((n, n, 0), dtype=numpy.int32), float(rmin2), float(rmax2), 0.0)


