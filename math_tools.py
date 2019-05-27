#v0.1a

# math tools

import math

import pymel.core as pm

def get_line_circle_intersections(A, B, C, r):
    """Finds line and circle intersectinos
    # Code source:
            http://csharphelper.com/blog/2014/09/determine-where-a-line-intersects-a-circle-in-c/
    # Args:
        - A -point, start of line
        - B -point, end of line
        - C -point, circle's center
        - r -float, circle's radius
    
    # Returns, always two points:
        - if not interseection(s) - points at origin
        - if tangential - first point is result second at origin
    
    # Usage:
    A = pm.getAttr("A.t")
    B = pm.getAttr("B.t")
    C = pm.getAttr("C.t")
    r = 10.0
    P1, P2 = get_line_circle_intersections(A, B, C, r)
    pm.move("P1", P1[0], P1[1], P1[2])
    pm.move("P2", P2[0], P2[1], P2[2])
    
    """
    Lx = B[0] - A[0]
    Ly = B[1] - A[1]
    Lz = B[2] - A[2]

    # stranger things
    D = Lx**2 + Ly**2
    E = 2 * ( Lx * (A[0] - C[0]) + Ly * (A[1] - C[1]) )
    F = (
            (A[0] - C[0])**2
          + (A[1] - C[1])**2
          - r**2
        )
    det = E**2 - 4 * D * F
    
    # declare null vectors
    P1 = [0, 0, 0]
    P2 = [0, 0, 0]
    t1 = t2 = None
    eps = .00001
    if ( not (D <= eps) or (det < 0) ):
        if det == 0:
            print "tangential intersection found",
            t1 = t2 = -E / (2*D)
        else:
            print "pass-through intersection found",
            t1 = ( (-E + math.sqrt(det)) / (2 * D) )
            t2 = ( (-E - math.sqrt(det)) / (2 * D) )
        P1[0] = A[0] + t1 * Lx
        P1[1] = A[1] + t1 * Ly
        P1[2] = A[2] + t1 * Lz
        P2[0] = A[0] + t2 * Lx
        P2[1] = A[1] + t2 * Ly
        P2[2] = A[2] + t2 * Lz
    else:
        print "no intersections are available",

    return P1, P2
