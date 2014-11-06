'''Add object sizes to LabelMe3D output, save in a new annotation file. This
uses the ElementTree library, as well as numpy.'''

import xml.etree.ElementTree as ET
from numpy import array
from numpy.linalg import norm
from operator import add

#Function(s) for processing annotation files

def processAnnotation(fname, target, procedure):
    '''Apply procedure to LabelMe3D annotation file and save result to 
    target.'''

    xmltree = getXML(fname)
    procedure(xmltree)
    xmltree.write(target)

#Function(s) for manipulating xml data.

def getXML(fname):
    """Load an annotation file."""

    return ET.parse(fname)

def getObjects(annotation):
    """Return a list of all 3D objects in annotation, which points to the root
    node of an ElementTree object parsed out from a LabelMe3d annotation file.

    The returned list is a list of ElementTree objects."""

    return filter(findObject3d, annotation.findall('./object'))

def getPolygon3d(obj):
    """Return a list of all 3D polygons in obj, which points to an ElementTree
    representation of an object field in a LabelMe3D annotation file.

    The returned list is a list of ElementTree objects."""

    return obj.find('./world3d/polygon3d')

def pointsFromPolygon3d(polygon):
    '''Given an ElementTree representation of a 3D polygon in LabelMe3D return
    the point cloud of the polygon as a list of numpy arrays.'''

    return array([dataFromCoordinateAnnotations(polygon.findall(coordannots))\
              for coordannots in ['./pt/x', './pt/y', './pt/z']]).transpose()

def dataFromCoordinateAnnotations(ptannots):
    '''Given a list of LabelMe3D pt coordinate annotations, return a list
    containing the data in each field.'''

    return array([float(ET.Element.findtext(ptannot, '.'))\
                  for ptannot in ptannots])

def findObject3d(obj):
    '''Return true if object has polygon3D.'''

    if obj.find('./world3d/polygon3d'):
        return True
    return False

#Function(s) for sizing polygons

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

if __name__ == '__main__':

    sample = getXML('sample.xml')
    objects = getObjects(sample)
    print objects
    writeBoundingBall3d(objects[0])
    print ET.tostring(objects[0])
    processAnnotation('sample.xml', 'sampleresult.xml', writeBoundingBall3ds)
