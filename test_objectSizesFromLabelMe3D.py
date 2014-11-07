'''Contains tests of objectSizesFromLabelMe3D. In this document modified
LabelMe3D annotations, objects etc. are understood to be modified by
objectSizesFromLabelMe3D.py.'''

from numpy import array
import objectSizesFromLabelMe3D as sizes

def getBoundingBalls(fname):
    '''Return a list of all bounding balls in modified LabelMe3D annotation
    file with file name fname.'''

    return [getBoundingBall(obj) for obj in \
            sizes.getObjects(sizes.getXML(fname))]

def getBoundingBall(obj):
    '''Given a modified LabelMe3D object, return its bounding ball.'''
    return array([centerFromBoundingBall3d(obj), radiusFromBoundingBall3d(obj)])

def centerFromBoundingBall3d(obj):
    '''Given a modified LM3D object, return the center point of its bounding
    ball.'''

    return array([float(obj.find('./boundingball3d/center'+coordinate).text) \
                   for coordinate in ['/x', '/y', '/z']])

def radiusFromBoundingBall3d(obj):
    '''Given a modified LM3D object, return the radius of its bounding ball.'''
    
    return array([float(obj.find('./boundingball3d/radius').text)])

if __name__=='__main__':

    import numpy as np
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt

    def drawSphere(xCenter, yCenter, zCenter, r):
        #draw sphere
        u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
        x=np.cos(u)*np.sin(v)
        y=np.sin(u)*np.sin(v)
        z=np.cos(v)
        # shift and scale sphere
        x = r*x + xCenter
        y = r*y + yCenter
        z = r*z + zCenter
        return (x,y,z)

    bbs = getBoundingBalls('sampleresult.xml')
    params = [bb[0].tolist()+bb[1].tolist() for bb in bbs]
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    # draw a sphere for each data point
    for x in params[:]:
        (xs,ys,zs) = drawSphere(x[0],x[1],x[2],x[3])
        ax.plot_wireframe(zs, xs, ys, color="r")

    plt.show()
