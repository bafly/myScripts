#v0.1a

import pymel.core as pm
def doIt(lssl=None):
    
    if not lssl:
        lssl = pm.selected()
    shps = [x for y in lssl 
              for x in y.getShapes(ni=1)
              if y.getShapes()]
    for shp in shps:
        shp_typ = shp.type()
        comp = None
        if shp_typ == "nurbsCurve":
            comp = "cp"
        else:
            if shp_typ == "mesh":
                comp = "pnts"
            else:
                print " ? add component for type: {0}".format(shp_typ)
                continue
        for c in range(shp.attr(comp).numElements()):
            shp.attr(comp)[c].set(0, 0, 0)