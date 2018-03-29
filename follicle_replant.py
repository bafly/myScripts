#v0.0 not tested yet

"""Select follicles/or any transforms
    then last select geometry
"""

import pymel.core as pm

def get_uv_data(items, trg):
    
    lssl = pm.ls(items)
    trg = pm.PyNode(trg)
    
    cp = pm.createNode("closestPointOnMesh", ss=1)
    trg.o >> cp.im
    trg.getShape().wm >> cp.ix
    
    uv_data = {"items" : [str(x) for x in lssl],
               "data" : {},
               "target" : str(trg)}
    for sel in lssl:
        data = {}
        sel.t >> cp.ip
        data["u"] = cp.u.get()
        data["v"] = cp.v.get()
        uv_data["data"].update({str(sel) : data})
    pm.delete(cp)
    return uv_data

def set_uv_data(data, trg, create=None):
    
    if not create:
        create = False
    trg = pm.PyNode(trg)
    new = []
    fol = None
    folShp = None
    for sel, val in data.items():
        if (not pm.objExists 
                or pm.PyNode(sel).getShape().type() != "follicle"):
            print "Node does not exist: ", sel
            if not create:
                continue
            else:
                folShp = pm.createNode("follicle")
                fol = folShp.getParent()
                folShp.ot >> fol.t
                folShp.outRotate >> fol.r
                new.append(fol)
        else:
            fol = pm.PyNode(sel)
            folShp = fol.getShape()
        print "Found ", fol
        
        trg.o >> folShp.inm
        trg.getShape().wm >> folShp.iwm
        
        folShp.pu.set(val["u"])
        folShp.pv.set(val["v"])
    
    if new:
        setn = "_set_new_follicles"
        newset = None
        if not pm.objExists(setn):
            newset = pm.sets(n=setn, em=1)
        newset.addMebmers(new)
    return new

def doIt():
    
    lssl = pm.selected()
    trg = lssl.pop(-1)
    uv_data = get_uv_data(lssl, trg)

    # store childs data and unparent them
    for sel in lssl:
        childs = sel.getChildren(type="transform")
        uv_data["data"][str(sel)].update(
            {"childs" : [str(x) for x in childs]}
            )
        pm.parent(childs, w=1)

    set_uv_data(uv_data["data"], uv_data["target"])

    # parent back
    for sel in lssl:
        childs = uv_data["data"][str(sel)]["childs"]
        pm.parent(childs, sel)
        pm.move(0, 0, 0, childs, os=1)

if __name__ == '__main__':
    doIt()