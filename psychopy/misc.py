"""Tools, nothing to do with psychophysics or experiments
- just handy things like conversion functions etc...
""" 
# Part of the PsychoPy library
# Copyright (C) 2011 Jonathan Peirce
# Distributed under the terms of the GNU General Public License (GPL).

import numpy, random #this is imported by psychopy.core
from psychopy import log
import monitors

import os, shutil
import Image, cPickle
#from random import shuffle #this is core python dist

def toFile(filename, data):
    """save data (of any sort) as a pickle file
    
    simple wrapper of the cPickle module in core python
    """
    f = open(filename, 'w')
    cPickle.dump(data,f)
    f.close()

def fromFile(filename):
    """load data (of any sort) from a pickle file
    
    simple wrapper of the cPickle module in core python
    """
    f = open(filename)
    contents = cPickle.load(f)
    f.close()
    return contents

def mergeFolder(src, dst, pattern=None):
    """Merge a folder into another. 
    
    Existing files in dst with the same name will be overwritten. Non-existent
    files/folders will be created.
    
    """
    # dstdir must exist first
    srcnames = os.listdir(src)
    for name in srcnames:
        srcfname = os.path.join(src, name)
        dstfname = os.path.join(dst, name)
        if os.path.isdir(srcfname):
            if not os.path.isdir(dstfname): os.makedirs(dstfname)
            mergeFolder(srcfname, dstfname)
        else:
            try:
                shutil.copyfile(srcfname, dstfname)#copy without metadata
            except IOError, why:
                print why

def radians(degrees):
    """Convert degrees to radians
    
    >>> radians(180)
    3.1415926535897931
    >>> degrees(45)
    0.78539816339744828
    
    """
    return degrees*numpy.pi/180.0

def shuffleArray(inArray, shuffleAxis=-1, seed=None):
    """Takes a  (flat) num array, list or string and returns a shuffled
    version as a num array with the same shape. Optional argument ShuffleAxis
    determines the axis to shuffle along (default=-1 meaning shuffle across
    entire matrix?)
    
    THIS DOESN'T WORK WITH MATRICES YET - ONLY FLAT ARRAYS - APPEARS TO BE BUG
    IN EITHER NUMPY.ARGSORT() OR NUMPY.TAKE()
    """
    #arrAsList = shuffle(list(inArray))
    #return numpy.array(arrAsList)
    if seed is not None:
        numpy.random.seed(seed)
        
    inArray = numpy.array(inArray, 'O')#convert to array if necess
    rndArray = numpy.random.random(inArray.shape)#create a random array of the same shape
    newIndices =  numpy.argsort(rndArray, shuffleAxis)# and get the arguments that would sort it
    return numpy.take(inArray,newIndices)#return the array with the sorted random indices

def extendArr(inArray,newSize):
    """Takes a numpy array and returns it padded with zeros to the necessary size
    
    >>> misc.extendArr([1,2,3],5)
    array([1, 2, 3, 0, 0])
    
    """ 
    if type(inArray) in [tuple,list]:
        inArray=numpy.asarray(inArray)
        
    newArr = numpy.zeros(newSize,inArray.dtype)
    #create a string to eval (see comment below)
    indString=''
    for thisDim in inArray.shape:
        indString += '0:'+str(thisDim)+','
    indString = indString[0:-1]#remove the final comma
    
    #e.g.
    #newArr[0:4,0:3]=inArray
    
    exec("newArr["+indString+"]=inArray")
    return newArr
    


def ratioRange(start, nSteps=None, stop=None, 
               stepRatio=None, stepdB=None, stepLogUnits=None):
    """Creates a  array where each step is a constant ratio
    rather than a constant addition.
    
    Specify *start* and any 2 of, *nSteps*, *stop*, *stepRatio*, *stepdB*, *stepLogUnits*
    
    >>> ratioRange(1,nSteps=4,stop=8)
    array([ 1.,  2.,  4.,  8.])    
    >>> ratioRange(1,nSteps=4,stepRatio=2)
    array([ 1.,  2.,  4.,  8.])    
    >>> ratioRange(1,stop=8,stepRatio=2)
    array([ 1.,  2.,  4.,  8.])    
            
    """

    if start<=0:
        raise RuntimeError, "Can't calculate ratio ranges on negatives or zero"
    if (stepdB != None): stepRatio= 10.0**(stepdB/20.0) #dB = 20*log10(ratio)
    if (stepLogUnits != None): stepRatio= 10.0**stepLogUnits #logUnit = log10(ratio)
    
    if (stepRatio!=None) and (nSteps!=None):
        factors = stepRatio**numpy.arange(nSteps,dtype='d')
        output = start*factors
        
    elif (nSteps!=None) and (stop!=None):
        if stop<=0:
            raise RuntimeError, "Can't calculate ratio ranges on negatives or zero"
        lgStart = numpy.log10(start) 
        lgStop = numpy.log10(stop)
        lgStep = (lgStop-lgStart)/(nSteps-1)
        lgArray = numpy.arange(lgStart, lgStop+lgStep, lgStep)
        #if the above is a badly rounded float it may have one extra entry
        if len(lgArray)>nSteps: lgArray=lgArray[:-1]
        output = 10**lgArray
        
    elif (stepRatio!=None) and (stop!=None):
        thisVal=float(start)
        outList = []
        while thisVal<stop:
            outList.append(thisVal)
            thisVal *= stepRatio
        output=numpy.asarray(outList)
        
    return output
    

def makeImageAuto(inarray):
    """Combines float_uint8 and image2array operations
    ie. scales a numeric array from -1:1 to 0:255 and
    converts to PIL image format"""
    return image2array(float_uint8(inarray))

def image2array(im):
    """Takes an image object (PIL) and returns an array
    
     fredrik lundh, october 1998
    
     fredrik@pythonware.com
     http://www.pythonware.com
    
    """
    if im.mode not in ("L", "F"):
            raise ValueError, "can only convert single-layer images"
    if im.mode == "L":
            a = numpy.fromstring(im.tostring(), numpy.uint8)
    else:
            a = numpy.fromstring(im.tostring(), numpy.float32)
    a.shape = im.size[1], im.size[0]
    return a

def array2image(a):
    """Takes an array and returns an image object (PIL)""" 
    # fredrik lundh, october 1998
    #
    # fredrik@pythonware.com
    # http://www.pythonware.com
    #
    if a.dtype.kind in ['u','I', 'B']:
            mode = "L"
    elif a.dtype.kind == numpy.float32:
            mode = "F"
    else:
            raise ValueError, "unsupported image mode"
    return Image.fromstring(mode, (a.shape[1], a.shape[0]), a.tostring())
########################################################################

    

def float_uint8(inarray):
    """Converts arrays, lists, tuples and floats ranging -1:1
    into an array of Uint8s ranging 0:255
    
    >>> float_uint8(-1)
    0
    >>> float_uint8(0)
    128
    
    """
    retVal = numpy.around(255*(0.5+0.5*numpy.asarray(inarray)))
    return retVal.astype(numpy.uint8)
def uint8_float(inarray):
    """Converts arrays, lists, tuples and UINTs ranging 0:255
    into an array of floats ranging -1:1
    """
    return numpy.asarray(inarray,'f')/127.5 - 1
def float_uint16(inarray):
    """Converts arrays, lists, tuples and floats ranging -1:1
    into an array of Uint16s ranging 0:2^16
    """
    i16max = 2**16 - 1
    retVal = numpy.around(i16max*(1.0+numpy.asarray(inarray))/2.0)
    return retVal.astype(numpy.UnsignedInt16)

def sph2cart(*args):
    #convert from spherical coordinates (elevation, azimuth, radius)
    #to cartesian (x,y,z)
    
    #usage:
        #array3xN[x,y,z] = sph2cart(array3xN[el,az,rad])
        #OR 
        #x,y,z = sph2cart(elev, azim, radius)
        
    if len(args)==1:    #received an Nx3 array
        elev = args[0][0,:]
        azim = args[0][1,:]
        radius = args[0][2,:]
        returnAsArray = True
    elif len(args)==3:
        elev = args[0]
        azim = args[1]
        radius = args[2]
        returnAsArray = False
        
    z = radius * numpy.sin(radians(elev))
    x = radius * numpy.cos(radians(elev))*numpy.cos(radians(azim))
    y = radius * numpy.cos(radians(elev))*numpy.sin(radians(azim))
    if returnAsArray:
        return numpy.asarray([x, y, z])
    else:
        return x, y, z
    
#---unit conversions
def pix2deg(pixels, monitor):
    """Convert size in pixels to size in degrees for a given Monitor object"""   
    #get monitor params and raise error if necess
    scrWidthCm = monitor.getWidth()
    scrSizePix = monitor.getSizePix()
    if scrSizePix==None:
        raise ValueError("Monitor %s has no known size in pixels (SEE MONITOR CENTER)" %monitor.name)
    if scrWidthCm==None:
        raise ValueError("Monitor %s has no known width in cm (SEE MONITOR CENTER)" %monitor.name)
    cmSize=pixels*float(scrWidthCm)/scrSizePix[0]
    return cm2deg(cmSize, monitor)
def deg2pix(degrees, monitor):
    """Convert size in degrees to size in pixels for a given Monitor object"""   
    #get monitor params and raise error if necess
    scrWidthCm = monitor.getWidth()
    scrSizePix = monitor.getSizePix()
    if scrSizePix==None:
        raise ValueError("Monitor %s has no known size in pixels (SEE MONITOR CENTER)" %monitor.name)
    if scrWidthCm==None:
        raise ValueError("Monitor %s has no known width in cm (SEE MONITOR CENTER)" %monitor.name)
    
    cmSize = deg2cm(degrees, monitor)
    return cmSize*scrSizePix[0]/float(scrWidthCm)
def deg2cm(degrees, monitor):
    """Convert size in degrees to size in pixels for a given Monitor object"""
    #check we have a monitor
    if not isinstance(monitor, monitors.Monitor):
        raise ValueError("deg2cm requires a monitors.Monitor object as the second argument but received %s" %str(type(monitor)))
    #get monitor dimensions
    dist = monitor.getDistance()
    #check they all exist
    if dist==None:
        raise ValueError("Monitor %s has no known distance (SEE MONITOR CENTER)" %monitor.name)
    return degrees*dist*0.017455
def cm2deg(cm, monitor):
    """Convert size in cm to size in degrees for a given Monitor object"""
    #check we have a monitor
    if not isinstance(monitor, monitors.Monitor):
        raise ValueError("cm2deg requires a monitors.Monitor object as the second argument but received %s" %str(type(monitor)))
    #get monitor dimensions
    dist = monitor.getDistance()    
    #check they all exist
    if dist==None:
        raise ValueError("Monitor %s has no known distance (SEE MONITOR CENTER)" %monitor.name)
    return cm/(dist*0.017455)
def pix2cm(pixels, monitor):
    """Convert size in pixels to size in cm for a given Monitor object"""
    #check we have a monitor
    if not isinstance(monitor, monitors.Monitor):
        raise ValueError("cm2pix requires a monitors.Monitor object as the second argument but received %s" %str(type(monitor)))
    #get monitor params and raise error if necess
    scrWidthCm = monitor.getWidth()
    scrSizePix = monitor.getSizePix()
    if scrSizePix==None:
        raise ValueError("Monitor %s has no known size in pixels (SEE MONITOR CENTER)" %monitor.name)
    if scrWidthCm==None:
        raise ValueError("Monitor %s has no known width in cm (SEE MONITOR CENTER)" %monitor.name)
    return pixels*float(scrWidthCm)/scrSizePix[0]
def cm2pix(cm, monitor):
    """Convert size in degrees to size in pixels for a given Monitor object"""
    #check we have a monitor
    if not isinstance(monitor, monitors.Monitor):
        raise ValueError("cm2pix requires a monitors.Monitor object as the second argument but received %s" %str(type(monitor)))
    #get monitor params and raise error if necess
    scrWidthCm = monitor.getWidth()
    scrSizePix = monitor.getSizePix()
    if scrSizePix==None:
        raise ValueError("Monitor %s has no known size in pixels (SEE MONITOR CENTER)" %monitor.name)
    if scrWidthCm==None:
        raise ValueError("Monitor %s has no known width in cm (SEE MONITOR CENTER)" %monitor.name)
    
    return cm*scrSizePix[0]/float(scrWidthCm)

#---color conversions---#000000#FFFFFF------------------------------------------ 
def dkl2rgb(dkl_Nx3, conversionMatrix=None):
    #Convert from DKL color space (cone-opponent space from Derrington,
    #Krauskopf & Lennie) to RGB. 

    #Requires a conversion matrix, which will be generated from generic
    #Sony Trinitron phosphors if not supplied (note that this will not be
    #an accurate representation of the color space unless you supply a 
    #conversion matrix
    #
    #usage:
        #rgb(Nx3) = dkl2rgb(dkl_Nx3(el,az,radius), conversionMatrix)
    
    dkl_3xN = numpy.transpose(dkl_Nx3)#its easier to use in the other orientation!
    if numpy.size(dkl_3xN)==3:
        RG, BY, LUM = sph2cart(dkl_3xN[0],dkl_3xN[1],dkl_3xN[2])
    else:
        RG, BY, LUM = sph2cart(dkl_3xN[0,:],dkl_3xN[1,:],dkl_3xN[2,:])
    dkl_cartesian = numpy.asarray([LUM, RG, BY])
    
    if conversionMatrix==None:
        conversionMatrix = numpy.asarray([ \
            #LUMIN    %L-M    %L+M-S  (note that dkl has to be in cartesian coords first!)
            [1.0000, 1.0000, -0.1462],#R
            [1.0000, -0.3900, 0.2094],#G
            [1.0000, 0.0180, -1.0000]])#B
        log.warning('This monitor has not been color-calibrated. Using default DKL conversion matrix.')
        
    rgb = numpy.dot(conversionMatrix, dkl_cartesian)
    
    return numpy.transpose(rgb)#return in the shape we received it
    
def dklCart2rgb(LUM, LM, S, conversionMatrix=None):
    """Like dkl2rgb2D except that it uses cartesian coords (LM,S,LUM) rather than
    spherical coords for DKL (elev, azim, contr)
    NB: Due to the matrix multiplication, this may return rgb values >1 or <-1
    """
    NxNx3=list(LUM.shape)
    NxNx3.append(3)
    dkl_cartesian = np.asarray([LUM.reshape([-1]), LM.reshape([-1]), S.reshape([-1])])

    if conversionMatrix==None:
        conversionMatrix = np.asarray([ \
            #LUMIN    %L-M    %L+M-S  (note that dkl has to be in cartesian coords first!)
            [1.0000, 1.0000, -0.1462],#R
            [1.0000, -0.3900, 0.2094],#G
            [1.0000, 0.0180, -1.0000]])#B
    rgb = np.dot(conversionMatrix, dkl_cartesian)
    return np.reshape(np.transpose(rgb), NxNx3)
    
def rgb2dklCart(picture, conversionMatrix=None):
    """convert an RGB image into Cartesian DKL space"""
    #Turn the picture into an array so we can do maths
    picture=scipy.array(picture)
    #Find the original dimensions of the picture
    origShape = picture.shape

    #this is the inversion of the dkl2rgb conversion matrix
    if conversionMatrix==None:
        conversionMatrix = np.asarray([\
            #LUMIN->%L-M->L+M-S
            [ 0.25145542,  0.64933633,  0.09920825],
            [ 0.78737943, -0.55586618, -0.23151325],
            [ 0.26562825,  0.63933074, -0.90495899]])
        log.warning('This monitor has not been color-calibrated. Using default DKL conversion matrix.')
    else:
        conversionMatrix = np.linalg.inv(conversionMatrix)

    #Reshape the picture so that it can multiplied by the conversion matrix
    red = picture[:,:,0]
    green = picture[:,:,1]
    blue = picture[:,:,2]

    dkl = np.asarray([red.reshape([-1]), green.reshape([-1]), blue.reshape([-1])])
    
    #Multiply the picture by the conversion matrix
    dkl=np.dot(conversionMatrix, dkl)

    #Reshape the picture so that it's back to it's original shape
    dklPicture = np.reshape(np.transpose(dkl), origShape)
    return dklPicture

def lms2rgb(lms_Nx3, conversionMatrix=None):
    #Convert from cone space (Long, Medium, Short) to RGB. 
    
    #Requires a conversion matrix, which will be generated from generic
    #Sony Trinitron phosphors if not supplied (note that you will not get
    #an accurate representation of the color space unless you supply a 
    #conversion matrix)
    #
    #usage:
        #rgb(Nx3) = lms2rgb(dkl_Nx3(el,az,radius), conversionMatrix)
    
    lms_3xN = numpy.transpose(lms_Nx3)#its easier to use in the other orientation!
        
    if conversionMatrix==None:
        cones_to_rgb = numpy.asarray([ \
            #L        M        S
            [ 4.97068857, -4.14354132, 0.17285275],#R
            [-0.90913894, 2.15671326, -0.24757432],#G
            [-0.03976551, -0.14253782, 1.18230333]#B
            ])
        log.warning('This monitor has not been color-calibrated. Using default LMS conversion matrix.')
    else: cones_to_rgb=conversionMatrix
    
    rgb_to_cones = numpy.linalg.pinv(cones_to_rgb)#get inverse
    rgb = numpy.dot(cones_to_rgb, lms_3xN)
    return numpy.transpose(rgb)#return in the shape we received it

def pol2cart(theta, radius, units='deg'):
    """Convert from polar to cartesian coordinates
    
    **usage**:
        x,y = pol2cart(theta, radius, units='deg')
    """
    if units in ['deg', 'degs']:
        theta = theta*numpy.pi/180.0
    xx = radius*numpy.cos(theta)
    yy = radius*numpy.sin(theta)
    
    return xx,yy
#----------------------------------------------------------------------
def  cart2pol(x,y, units='deg'):
    """Convert from cartesian to polar coordinates
    
    **usage**:
        theta, radius = pol2cart(x, y, units='deg')
        
    units refers to the units (rad or deg) for theta that should be returned"""
    radius= numpy.hypot(x,y)
    theta= numpy.arctan2(y,x)
    if units in ['deg', 'degs']:
        theta=theta*180/numpy.pi
    return theta, radius
    
def plotFrameIntervals(intervals):
    """Plot a histogram of the frame intervals.
    
    Arguments:
        - intervals: Either a filename to a log file, saved by Window.saveFrameIntervals
            or simply a list (or array of frame intervals)
    """
    from pylab import hist, show, plot
    
    if type(intervals)==str:
        f = open(intervals, 'r')
        exec("intervals = [%s]" %(f.readline()))
#    hist(intervals, int(len(intervals)/10))
    plot(intervals)
    show()
