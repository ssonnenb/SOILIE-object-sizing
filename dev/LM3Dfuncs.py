'''
Date: 07.01.2014
Author: Can Mekik

This module provides some functions for working with LabelMe3D annotations. 
'''

#USEFUL INFO
#ElementTree is for crawling XML files. Docs are online.

import xml.etree.ElementTree as ET
from numpy import array

#Function(s) for processing annotation files

def process_annotation(fname, target, procedure):
    '''Apply procedure to LabelMe3D annotation file and save result to 
    target.'''

    xmltree = getXML(fname)
    procedure(xmltree)
    xmltree.write(target)

def process_annotations(fnames, targets, procedure):
    '''Apply procedure to LabelMe3D annotation files and save results to 
    targets.'''

    map(processAnnotation, fnames, targets, [procedure]*len(fnames))

#Function(s) for manipulating xml data.

def get_XML(fname):
    """Load an annotation file."""

    return ET.parse(fname)

def get_object3Ds(annotation):
    """Return a list of all 3D objects in annotation, which points to the root
    node of an ElementTree object parsed out from a LabelMe3d annotation file.

    The returned list is a list of ElementTree objects."""

    return filter(findObject3d, annotation.findall('./object'))

def get_polygon3D(obj):
    """Return a list of all 3D polygons in obj, which points to an ElementTree
    representation of an object field in a LabelMe3D annotation file.

    The returned list is a list of ElementTree objects."""

    return obj.find('./world3d/polygon3d')

def points_from_polygon3D(polygon):
    '''Given an ElementTree representation of a 3D polygon in LabelMe3D return
    the point cloud of the polygon as a list of numpy arrays.'''

    return array([data_from_coordinate_annotations(polygon.findall(coordannots))\
              for coordannots in ['./pt/x', './pt/y', './pt/z']]).transpose()

#Miscellaneous functions

def data_from_coordinate_annotations(ptannots):
    '''Given a list of LabelMe3D pt coordinate annotations, return a list
    containing the data in each field.'''

    return array([float(ET.Element.findtext(ptannot, '.'))\
                  for ptannot in ptannots])

def find_object3D(obj):
    '''Return true if object has polygon3D.'''

    if obj.find('./world3d/polygon3d'):
        return True
    return False
