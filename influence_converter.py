#v0.1a -upd- clean super small values 3.0517578125e-05
#      -new- fromAtoB()

from pymel.core import datatypes as dt
import pymel.core as pm

"""
example:
    
    trgeo = pm.selected()[0]
    geo = trgeo.getShape()
    initPos = getVtxPos(geo)

    # move smth
    all_weights = getVtxWeight(geo, initPos, 2)
    #maxv = 0.9
    nweightsData = normalizeVtxWeights(all_weights)

    assignWeight(geo, nweightsData)

"""

def doIt(ind=None, val=None):

    """
    Select influences and last binded geometry.
    
    Each influences will be moved to compare
    offsets of corresponding compotents.
    Delta will be final weight of created joints.
    
    If no current skinCluster is found new will be
    created with interractive mode. Each new joints
    After adding to deformer will be locked to preserve
    weights.

    Args:
        - ind, axis index(0-x, 1-y, 2-z)
        - val, offset of influence
    """
    
    lssl = pm.selected()
    geo_tr = lssl[-1]
    infls = lssl[:-1]
    geo = geo_tr.getShape()
    initPos = getVtxPos(geo)
    if not ind:
        ind = 1
    mov = [0.0]*3
    if not val:
        val = 1.0
    mov[ind] = val
    movback = mov[:]
    movback[ind] *= -1

    for sel in infls:

        pos = pm.xform(sel, q=1, ws=1, rp=1)
        # move
        pm.move(sel, mov, r=1)
        all_wghts = getVtxWeight(geo, initPos, ind)
        nWghtsData = normalizeVtxWeights(all_wghts)
        assignWeight(geo, nWghtsData, pos=pos)
        # move back
        pm.move(sel, movback, r=1)

def getVtxPos(geo=None, vtxs=None, axis=None):
    
    comp = "vtx"
    if geo.type() == "nurbsCurve":
        comp = "cv"
    print "  comp type: ", comp
    axis = axis if axis else 1
    data = vtxs if not geo else geo.__getattr__(comp)
    pos = [x.getPosition("world")[axis] for x in data]
    return (pos)

def getVtxWeight(geo, oldPos, ind):
    
    comp = "vtx"
    if geo.type() == "nurbsCurve":
        comp = "cv"
    weight = [geo.__getattr__(comp)[x].getPosition("world")[ind] - y for x,y in enumerate(oldPos)]
    return weight

def pruneWeights(wlist):
    
    data = {}
    data = dict((i,x) for i, x in enumerate(wlist) if not x<=0)
    return data

def normalizeVtxWeights(wlist, maxv=None):
    
    if not maxv or not isinstance(maxv, float):
        maxv = 1.0
    
    eps = 0.0001
    curmax = 0.0    
    wdata = {}
    ind_info = 0
    for i, v in enumerate(wlist):
        if v > eps:
            wdata.update({i:v})
            if v > curmax:
                ind_info = i
                curmax = v

    clampv = 1.0
    newdata = wdata.copy()
    if maxv != 1.0:
        clampv = maxv / curmax
    
    newdata.update(dict((k, v*clampv) for k,v in newdata.items()))
    
    print "max value: [{0}]={1}".format(ind_info, newdata[ind_info])
    return newdata

def getSkinc(geo):

    comp = "i"
    if geo.getShape() and geo.getShape().type() == "nurbsCurve":
        comp = "cr"
    print "finding skin, comp: ", comp
    skinc = None
    geo = pm.ls(geo)[0]
    if geo.type() == "transform":
        geo = geo.getShape()
    ls_hi = geo.__getattr__(comp).listHistory(type="skinCluster")
    if ls_hi.__len__():
        chk_geo = pm.skinCluster(ls_hi[0], q=1, g=1)
        if chk_geo[0] == geo:
            skinc = ls_hi[0]

    return skinc

def assignWeight(geo, wdata, skinc=None, jnt=None, pos=None):
    
    comp = "vtx"
    if geo.type() == "nurbsCurve":
        comp = "cv"
    mesh = None
    if pm.PyNode(geo).type() != "transform":
        mesh = geo
        geo = geo.getParent()
        
    #TODO: find center of wlist
    if not pos:
        pos = [0,0,0]
    
    if not jnt:
        print " Z"
        pm.select(cl=1)
        jnt = pm.joint(p=pos)
        jnt_grp = pm.group(jnt, em=1, n=str(jnt) + "_grp")
        jnt_grp.setTranslation(pos)
        jnt.setParent(jnt_grp)
    if not skinc:
        print " Y"

        skinc = getSkinc(geo)
    if not skinc:
        print " X"

        # insert base jnt
        pm.select(cl=1)
        basejnt = pm.joint(n=(str(geo) + "_baseJnt"))
        # check cons TODO: reconnect all constraint types
        ls_constrs = pm.parentConstraint(geo, q=1, n=1)
        if ls_constrs:
            transfer_constraint(geo, basejnt)
        skinc = pm.skinCluster(geo, basejnt)
        print "  New skincluster: {0}".format(skinc)
    
    print "_:", geo, skinc
    # add infl
    pm.skinCluster(skinc, e=1, ai=jnt, lw=1, wt=0)
    print "_:", jnt
    #########
    """
    for v, w in vtxs_data1.items():
        print "__:", v, w
        pm.skinPercent(snc, v, tv=[str(jnt), w])
    """
    for i, w in wdata.items():
        #print "__:", i, w
        print i, w
        pm.skinPercent(skinc, geo.__getattr__(comp)[i], tv=[str(jnt), w])

    return jnt

def doJnt( jname=None, pos=None ):
    
    jnt = grp = None
    lssl = pm.selected()
    if not jname:
        jname = ""
        if lssl.__len__():
            jname = "jnt_" + lssl[0].nodeName()
    if pos == None:
        pos = [0,0,0]
        if lssl.__len__():
            pos = pm.xform(lssl[0], q=1, ws=1, rp=1)
    jnt = pm.joint(n=jname, p=pos)
    gname = "grp"+jnt.nodeName()[0].upper()+jnt.nodeName()[1:]
    grp = pm.group(n=gname, em=1)
    pos = pm.xform(jnt, q=1, ws=1, rp=1)
    rot = pm.xform(jnt, q=1, ws=1, ro=1)
    scl = pm.xform(jnt, q=1, r=1, s=1)
    # align grp
    grp.setTranslation(pos, ws=1)
    grp.setRotation(rot, ws=1)
    grp.setScale(scl, ws=1)
    
    jpar = jnt.getParent()
    if jpar:
        grp.setParent(jpar)
    jnt.setParent(grp)
    
    return (jnt, grp)

def getInfoFromSelection(geo=None, pos=None):

    if not geo:
        lssl = pm.selected()
        geo = lssl[0]
    else:
        if pm.objExists(geo):
            geo = pm.PyNode(geo)
    if geo.type() == "mesh":
        #mesh = geo
        geo = mesh.getParent()
        
    if not pos:
        pos = [0,0,0]
        if lssl.__len__() > 1:
            inf = lssl[1]
            
    #print geo, pos
    return geo, inf

def convertThis(geo=None, vtxs=None, pos=None, axis=None):
    

    inf = None
    geo, inf = getInfoFromSelection()
    if not axis:
        axis = 2
    move_dir = [0,0,0]
    move_dir[axis] = 1

    if vtxs:
        print "A"
        vlist = pm.ls(vtxs, fl=1)
        initPos = getVtxPos(vtxs=vlist, axis=axis)
        pm.move(inf, move_dir, ws=1, r=1)
        normW = normalizeVtxWeights(initPos)
    else:
        print "B"
        initPos = getVtxPos(geo, axis=axis)
        pm.move(inf, move_dir, ws=1, r=1)
        wlist = getVtxWeight(geo, initPos, axis)
        normW = normalizeVtxWeights(wlist)

    if not pos:
        pos = [0, 0, 0]
        if not inf:
            return
        pos = pm.xform(inf, q=1, ws=1, rp=1)
    
    move_dir[axis] = -1
    pm.move(inf, move_dir, ws=1, r=1)

    # print "vtxslist: ", initPos.__len__()
    infPos = pm.xform(inf, q=1, t=1)
    offset = infPos[:]
    offset[axis] = offset[axis]+1
    pm.xform(inf, t=offset)
    #print geo, pos
    pm.xform(inf, ws=1, t=infPos)
    # print "pos:", pos
    jnt = assignWeight(geo, normW, pos=pos)

    return jnt

def fromAtoB(lssl=None):
    """Select two geometries one with offset
        and second desitnation
    """
    lssl = pm.ls(lssl)
    if not lssl:
        lssl = pm.selected()
        if not lssl:
            return
    if len(lssl) != 2:
        print "  ! Select source and target geometries"
        return
    geo_src, gro_trg = [x.getShape() for x in lssl]
    if not ind:
        ind = 1
    if not val:
        val = 1.0
    pos = [0.0]*3

    initPos = getVtxPos(geo_trg)
    all_wghts = getVtxWeight(geo_src, initPos, ind)
    nWghtsData = normalizeVtxWeights(all_wghts)
    assignWeight(geo_trg, nWghtsData, pos=pos)