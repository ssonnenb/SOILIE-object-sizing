'''Add object sizes to LabelMe3D output, save in a new annotation file. This
uses the ElementTree library, as well as numpy.'''

import xml.etree.ElementTree as ET
from numpy import array, dot, diagonal
from numpy.linalg import solve
from numpy.linalg import norm
from operator import add

from LM3dFuncs import *

#Function(s) for sizing polygons

#Constraint: bounding balls must be represented as (center, radius)

#The BoundingBall functions only find bounding balls based on centroid and
#farthest point. I have realized that this is not ideal, as they will not find
#the _smallest_ bounding ball. Further functions below do so. They use the
#algorithm described by Emo Welzl (1991) in 'smallest enclosing disks (balls)
#and ellipsoids'

#The following functions are for using bounding balls centered on a point
#cloud centroid, with radius being the max distance between centroid and any
#one of the points.

def writeBoundingBall3ds(root):
    '''Write bounding ball information to the object field of an ElementTree
    representation of each LabelMe3D object in an annotation file represented
    by ElementTree object root. See writeBoundingBall for details.'''

    map(writeBoundingBall3d, getObjects(root))

def writeBoundingBall3d(obj):
    '''Write bounding ball information to the object field of an ElementTree
    representation of an object annotation in LabelMe3D.

    The result will look like this:
    <object>
    .
    .
    .
        <boundingball3d>
            <center>
                <pt>
                    <x>x-coordinate<\\x>
                    <y>y-coordinate<\\y>
                    <z>z-coordinate<\\z>
                <\\pt>
            <\\center>
            <radius>radius<\\radius>
        <\\boundingball3d>
    .
    .
    .
    <\\object>'''

    bb = findBoundingBall(getPolygon3d(obj))
    #populate <boundingball3d>
    ET.SubElement(obj, 'boundingball3d')
    #populate <center> 
    ET.SubElement(obj.find('./boundingball3d'), 'center')
    for i in range(3):
        ET.SubElement(obj.find('./boundingball3d/center'), \
                      ['x', 'y', 'z'][i])
        obj.find('./boundingball3d/center/'+['x', 'y', 'z'][i]).text = \
                                                  str(bb[0][i])
    #populate <radius>
    ET.SubElement(obj.find('boundingball3d'), 'radius')
    obj.find('./boundingball3d/radius').text = str(bb[1])

def findBoundingBall(polygon3d):
    '''Return the center and radius of the ball bounding polygon. Polygon3d is
    an ElementTree representation of a 3D polygon in LabelMe3d.'''

    points = pointsFromPolygon3d(polygon3d)
    centroid = findCentroid(points)
    return centroid, findRadius(centroid, points)

def findCentroid(points):
    '''Find euclidian centroid of a set of points (list of numpy arrays).
    Euclidian centroid for k points x_1,...,x_k is sum_i^k x_i/k.'''

    return reduce(add, points)/len(points)

def findRadius(center, points):
    '''Return the distance of the farthest point (in list of numpy arrays
    points) from center (numpy array). Distance is in the Euclidian metric.'''

    return max([norm(center - point) for point in points])

#The following functions are for using the smallest bounding balls for a point
#cluster, algorithm is bazed on Welzl paper cited above.

from random import choice

def minidisk(P):
    """Return the smallest ball bounding set of points P."""
    
    return _bMinidisk(P, [])

def _bMinidisk(P, R):
    if P == [] or len(R)==3:
        B = ballFromBoundaryPoints(R)
    else:
        p, B = choice(P), bMinidisk(P[:].remove(p), R)
        if not pointInBall(p, B):
            B = bMinidisk(P[:].remove(p), R.append(p))
    return B
        
def ballFromBoundaryPoints(B):
    """Return ball with boundary points B."""

    center = centerFromBoundaryPoints(B)
    return center, findRadius(center, B[:1])

from numpy import mean

def centerFromBoundaryPoints(B):
    #find segment boundaries
    vertices = array([B[2], B[0]])
    midpoints = array([findCentroid(B[:2]),findCentroid(B[1:2])])
    coeffs = vertices - midpoints
    constants = diagonal(dot(coeffs, vertices.T))
    return solve(coeffs, constants)

def pointInBall(p, B):
    """True if p is in ball B."""
    
    return norm(p - B[0]) < B[1]

if __name__ == '__main__':

    sample = getXML('sample.xml')
    objects = getObjects(sample)
    print objects
    writeBoundingBall3d(objects[0])
    print ET.tostring(objects[0])
    processAnnotation('sample.xml', 'sampleresult.xml', writeBoundingBall3ds)
