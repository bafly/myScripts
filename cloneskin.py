import pymel.core as pm

def doIt(sclA=None, sclB=None):
        
    pts = None

    ls_nodes = pm.ls(sclA, sclB, type="skinCluster")
    if not ls_nodes:
        ls_nodes = pm.ls(sl=1, type="skinCluster")
        
    if len(ls_nodes) == 2:
        sclA, sclB = ls_nodes
        #sclA = pm.PyNode("REF:skinCluster239")
        #sclB = pm.PyNode("skinCluster296")

        sclA_infs = sclA.getInfluence()
        #sclB_infs = sclB.getInfluence()

        #i = 0
        pts = sclA.wl.getNumElements()
        for i in range(pts):
            #print "pt:", i
            inf_inds = sclA.wl[i].w.getArrayIndices()
            # ls_inf = [sclA_infs[x] for x in inf_inds]
            ls_w = [sclA.wl[i].w[x].get() for x in inf_inds]
            for ii in range(sclA_infs.__len__()):
                sclB.wl[i].w[ii].set(0)
            for wi, ii in enumerate(inf_inds):
                w = ls_w[wi]
                #print "i:", wi, "w:", w
                sclB.wl[i].w[ii].set(w)
    
    return pts

"""
sclA.wl.getNumElements()    # 512

sclA.wl.elements()
sclA.wl[442].w.elements()    # .w[1]...w[1]
sclA.wl[444].w.evaluateNumElements()    # 5 ..all elements
sclA.wl[372].w.getArrayIndices()    # [0,1,2,3,]
sclA.wl[433].w.getArrayIndices()    # [2] ##############

sclB_wl = sclB.getInfluence()
"""


"""
skinCluster@
@.weightList[x] - Contains indexArray(points), each of it element
                  corresponds to vertex indices
@.@.weights     - Contains doubleArray of influence indeices, the size of array equals to
                  binded infuences count, the order depends on connections in matrces array
@.@.@.weights[x]- Contains floats representing weight of that influence to that point

@.[vtxID(array), ...]
@.vtxID[x].[jointID(float), ...]
@.vtxID[x].jointID[y].get() >> influenceI wieghtJ
@.vtxID[x].jointID[y].get() >> influenceK wieghtL...

"""