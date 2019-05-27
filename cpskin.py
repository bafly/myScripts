# v0.1a - copy skin data, skin node creates on targets
#       - new: copy(), mk_skin_cluster(), copy_infs(), get_node(),
#              cp_values()(merged)

import pymel.core as pm

def copy(src, trgs=None):
    """Copies main skinCluster data from source geo to target
    # Usage:
        Select src and target(s)
        If target dosen't have one, user will be prompted 
            to create new
    # Return:
        list(), cretaed skinClster nodes
    """
    ls_src_scl = pm.PyNode(src).listHistory(type="skinCluster")
    if not ls_src_scl:
        print " skinCluster not found on source"
        return
    src_scl = ls_src_scl[0]
    src_infs = pm.skinCluster(src_scl, q=1, inf=1)
    trgs = pm.ls(trgs)
    
    items = []
    for sel in trgs:
        scl = None
        ls_trg_scl = sel.listHistory(type="skinCluster")
        if not ls_trg_scl:
            print " on target: {}".format(sel)
            user_inp = pm.confirmDialog(
                m="skinCluster not found\nCreate?", 
                t=sel.nodeName(),
                b=["Create", "Skip", "Cancel"],
                cb="Cancel")
            if user_inp == "Cancel":
                return
            if user_inp == "Skip":
                continue
            scl = mk_skin_cluster(sel, src_infs)
        else:
            scl = ls_trg_scl[0]

        # recreate influence order
        cp_infs(src_scl, scl)

        # copy
        cp_values(src_scl, scl)

        # copy bind prematrix
        cp_bind_pm(src_scl, scl)
        
        if scl:
            items.append(scl)
    return items

def move_weights(src=None, trg=None, skcls=None):
    """Move weights from one influence to antoher"""
    ls_skcls = pm.ls(skcls)
    if not (src and trg and skcls):
        lssl = pm.selected()
        if not (src and trg):
            jnts = pm.ls(lssl, type="joint")
            if not jnts:
                print ">_<  No joints selected"
                return
            if not src:
                src = jnts[0]
                if not trg:
                    if len(jnts) < 2:
                        print ">_<  Not enough joints are selected"
                        return
                    trg = jnts[1]
            else:
                trg = jnts[0]
        if not skcls:
            other = list(set(lssl) - set(jnts))
            if not other:
                # print ">_<  You need to add binded geometry(ies) to current selection"
                print ("o_O No gometries are found, "
                     +"i will try get all common skin nodes from given influences")
            else:
                skcls = pm.ls(pm.listHistory(other), type="skinCluster")
                if not skcls:
                    print ">_<  Try to select \"BINDED\" or skinned geometry(ies), gl xD"
                    return
    print "src/trg: {0} >> {1}".format(src, trg)
    
    if not skcls:
        ls_src_skcl_plgs = set(src.wm.outputs(p=1, type="skinCluster"))
        src_skcls = set(x.node() for x in ls_src_skcl_plgs)
        ls_trg_skcl_plgs = set(trg.wm.outputs(p=1, type="skinCluster"))
        trg_skcls = set(x.node() for x in ls_trg_skcl_plgs)
        skcls = list(src_skcls.intersection(trg_skcls))
        if not skcls:
            print ">_< Given influences have no sharing skinCluster nodes"
            return
    for skcl in skcls:
        # check if influences are not binded to skin cluster node
        if skcl not in src.wm.outputs(type="skinCluster"):
            print ">_< {} is not linked to {}".format(src, skcl)
            return
        if skcl not in trg.wm.outputs(type="skinCluster"):
            print ("O_o {} is not linked to {}, but wait... "
                  +"i will bind it for you ^_^").format(trg, skcl)
            pm.skinCluster(skcl, e=1, ai=trg, wt=0)
        do_move_weights(src, trg, skcl)

################################ utils ################################
def get_node(sel):

    ls_scl = pm.PyNode(sel).listHistory(type="skinCluster")
    if not ls_scl:
        print " ! skinCluster not found"
        return None
    return  ls_scl[0]

def mk_skin_cluster(sel, infs=None):

    res = pm.skinCluster(
        sel, infs, bm=1, mi=2, rui=0, sm=0, tsb=1)
    return res

def copy_infs(src, trg):
    """Reconnectes(removes/connects) influences from 
        src to trg in order
        # Returns counter of existing matrices
    """
    exec("import pymel.core as pm")
    ls_src_scl = pm.ls(src)
    ls_trg_scl = pm.ls(trg)
    # src_matrix_plgs = ls_src_scl[0].ma.iterDescendants()
    in_use_idxs = src.ma.getArrayIndices()
    for i in range(in_use_idxs[-1]+1):
        plg = src.ma.elementByLogicalIndex(i)
        trg_plg = ls_trg_scl[0].attr(plg.split(".")[-1])
        print "souroce plg: {}\ttarget plg: {}".format(plg, trg_plg)
        ls_inf = plg.inputs(type="joint", p=1)
        ls_trg_inf = trg_plg.inputs(type="joint", p=1)
        print "  Source inf: ", ls_inf
        print "  Target inf: ", ls_trg_inf
        if not ls_inf:
            # if source matrix has no connected influence - disconnect any
            if ls_trg_inf:
                print " Diconnecting"
                exec("pm.disconnectAttr(\"{}\", \"{}\")".format(
                    ls_trg_inf[0], trg_plg))
        else:
            # check if target already have exact connected joint
            if not ls_inf[0].isConnectedTo(trg_plg):
                print " Connecting"
                exec("pm.connectAttr(\"{}\", \"{}\", f=1)".format(
                    ls_inf[0], trg_plg))
    return i

def cp_values(src=None, trg=None):

    """
    # NB: RESEARCH RESULTS
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
    pts = None

    ls_nodes = pm.ls(src, trg, type="skinCluster")
    if not ls_nodes:
        ls_nodes = pm.ls(sl=1, type="skinCluster")
        
    if len(ls_nodes) == 2:
        src, trg = ls_nodes
        #src = pm.PyNode("REF:skinCluster239")
        #trg = pm.PyNode("skinCluster296")

        src_infs = src.getInfluence()
        #trg_infs = trg.getInfluence()

        #i = 0
        pts = src.wl.getNumElements()
        for i in range(pts):
            #print "pt:", i
            inf_inds = src.wl[i].w.getArrayIndices()
            # ls_inf = [src_infs[x] for x in inf_inds]
            ls_w = [src.wl[i].w[x].get() for x in inf_inds]
            for ii in range(src_infs.__len__()):
                trg.wl[i].w[ii].set(0)
            for wi, ii in enumerate(inf_inds):
                w = ls_w[wi]
                #print "i:", wi, "w:", w
                trg.wl[i].w[ii].set(w)
    
    return pts

def do_move_weights(src, trg, skcl):
    
    wt_data = skcl.getPointsAffectedByInfluence(src)
    # save infs lock state
    src_liw = src.liw.get()
    trg_liw = trg.liw.get()
    
    # move it!
    src.liw.set(0)
    trg.liw.set(0)
    pm.skinPercent(skcl, wt_data[0], tmw=(src, trg))
    
    # return lock state
    src.liw.set(src_liw)
    trg.liw.set(trg_liw)

def in_mesh(c, d):

    lssl = pm.ls(c,d)
    if len(lssl) != 2:
        print " <!> At least two valid objects are required"
        return
    c, d = lssl

    c_init = c.getShape(ni=1)
    d_init = d.getShape(ni=1)
    ls_c_init = [x for x in c.getShapes() 
                   if x.isIntermediate() and x.w.outputs()]
    ls_d_init = [x for x in d.getShapes() 
                   if x.isIntermediate() and x.w.outputs()]
    if ls_c_init:
        c_init = ls_c_init[0]
    if ls_d_init:
        d_init = ls_d_init[0]
    print "{0} >> {1}".format(c_init, d_init)
    if not c_init.w.isConnectedTo(d_init.i):
        # pm.evalDeferred("import pymel.core as pm")
        pm.evalDeferred(
            "pm.connectAttr(\"{0}\", \"{1}\")".format(
                c_init.w, d_init.i),
            en=1
            )
    # if c_init.w.isConnectedTo(d_init.i):
    # c_init.w // d_init.i
    pm.evalDeferred(
        "pm.disconnectAttr(\"{0}\", \"{1}\")".format(
            c_init.w, d_init.i))

def cp_infs(a, b):
    
    last = a.ma.getArrayIndices()[-1]
    print "range: ", last
    for i in range(last+1):
        a_plg = a.ma.elementByLogicalIndex(i)
        b_plg = b.ma.elementByLogicalIndex(i)
        ls_jnt_plg = a_plg.inputs(type="joint", p=1)
        print "a: " + a_plg
        print "b: " + b_plg
        print "inf: ", ls_jnt_plg
        if not ls_jnt_plg:
            ls_con = b_plg.inputs()
            if ls_con:
                print "Disconnecting"
                b_plg.disconnect(inputs=1)
        else:
            if not ls_jnt_plg[0].isConnectedTo(b_plg):
                ls_jnt_plg[0] >> b_plg

def copy_skin_ids(a, b):
    a, b = pm.ls(a,b)
    # get a skin group id #
    a_skin_grpid = None
    ls_skinid = a.ip[0].gi.inputs(p=1, type="groupId")
    if ls_skinid:
        a_skin_grpid = ls_skinid[0]
    id = a_skin_grpid.get()
    # b skin data: id attr, groupParts, groupId, objectSet, mesh id #
    skin_data = get_skin_id_plugs(b)
    # skin_data["gid"].disconnect()
    skin_data["gpt"].disconnect()
    skin_data["gpt"].set(id)
    
    # skin_data["gid"].set(id)
    # skin_data["sid"].get()

def get_skin_id_plugs(a):
    
    # get b skin id #
    skin_id = a.ip[0].gi

    skin_grpid = None
    skin_grpp = None
    skin_set = None
    mesh_id = None

    # get skin tweak
    #ls_skin_tweak = a.ip[0].ig.inputs()
    #if ls_skin_tweak:
    #    skin_tweak_id = ls_skin_tweak[0].ip[0].gi

    # get b skin group id #
    ls_skin_grpid = skin_id.inputs(p=1, type="groupId")
    if not ls_skin_grpid:
        ls_skin_grpp = a.ip[0].ig.inputs(type="groupParts")
        if ls_skin_grpp:
            skin_grpp = ls_skin_grpp[0]
            ls_skin_grpid = skin_grpp.gi.inputs(p=1, type="groupId")

    if ls_skin_grpid:
        skin_grpid = ls_skin_grpid[0]

        # get mesh #
        ls_mesh = skin_grpid.outputs(p=1, type="mesh")
        if ls_mesh:
            mesh_id = ls_mesh[0]

            # get b skin set #
            ls_skin_set = mesh_id.parent().outputs(type="objectSet")
            if ls_skin_set:
                skin_set = ls_skin_set[0].msg

        # get skin group parts id #
        ls_skin_grpp = skin_grpid.outputs(type="groupParts")
        if ls_skin_grpp:
            skin_grpp = ls_skin_grpp[0]

    skin_data = {
        "sid" : skin_id,
        "gid" : skin_grpid,
        "gpt" : skin_grpp.gi,
        "set" : skin_set,
        "msh" : mesh_id
    }
    return skin_data

def cp_bind_pm(a, b):

    for i in range(a.pm.numElements()-1):
        M = a.pm[i].get()
        if not b.pm[i].isConnected():
            b.pm[i].set(M)