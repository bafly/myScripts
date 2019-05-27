import pymel.core as pm
from pymel.core import datatypes as dt


def doIt(shpsA=None, shpsB=None, flp=None, brk=False):

    """
    using transform groups
    flp = default(0, 0, 0) - xBase, yBase, zBase - if zero no flipping
    brk = clr rig after mirror
    """
    tg = None
    tgs = []
    mat = [
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 0.0, 1.0,
    ]
    M = dt.Array(mat, shape=(4,4))
    # miirror matrix
    if not flp:
        flp = (0, 0, 0)

    for i,j in enumerate(flp):
        M[i, i] = M[i][i] + (-1*(j*2))
    print M.formated()

    # check shps
    lssl = pm.ls(shpsA, shpsB)
    if not lssl:
        lssl = pm.ls(sl=1)
    else:
        lssl = [x.getShapes(ni=1) 
                if "transform" in x.type(i=1)
                else [x]
                for x in lssl]

    if lssl.__len__() != 2:
        print "  <!> Select two transforms"
        return
    shpsA, shpsB = lssl

    if not (shpsA and shpsB):
        return
    print "shapes A:", shpsA
    init_lssl = pm.selected()
    for i, shp in enumerate(shpsA):
        typ = shp.type()
        if i < shpsB.__len__():
            print "shp type: " + typ
            trg_shp = shpsB[i]
            iplg = "cr"
            oplg = "ws"
            if typ == "mesh":
                iplg = "i"
                oplg = "o"
            print trg_shp
            ls_tg = trg_shp.attr(iplg).inputs(type="transformGeometry")
            if ls_tg:
                tg = ls_tg[0]
            else:
                tg = pm.createNode("transformGeometry", n=("tg_"+trg_shp))

            tg.txf.set(M.ravel(), type="matrix")
            print M.ravel()
            if not shp.attr(oplg).isConnectedTo(tg.ig):
                print " // connecting to transformGeometry"
                shp.attr(oplg) >> tg.ig
            if not tg.og.isConnectedTo(trg_shp.attr(iplg)):
                print " // connecting to target"
                tg.og >> trg_shp.attr(iplg)

            if brk:
                print " // breaking"
                pm.evalDeferred("pm.disconnectAttr(\"{:}\", \"{:}\")".format(shp.ws, tg.ig))
                pm.evalDeferred("pm.disconnectAttr(\"{:}\", \"{:}\")".format(tg.og, trg_shp.attr(iplg)))
                pm.evalDeferred("pm.delete(\"{:}\")".format(tg))
            else:
                tgs.append(tg)
            tg.fn.set(1)
    pm.select(init_lssl)
    return tgs

def getTransformType(tr):

    tr = pm.PyNode(tr)
    ntype = tr.nodeType()
    shp = tr.getShape()
    if shp:
        ntype = shp.nodeType()

    return ntype

# TODO:
def copyComps(src, trg, comp):

    data = pm.ls(src, trg)
    if len(data) != 2:
        return
    src, trg = data