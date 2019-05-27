#######################################################################
#                              mute_bind                              #
#     (!) best thing is to get bindPose right from skinCluster        #

pi = 3.141592653589793
def mute_bind(scl=None):
    """Temporarly mutes all influences of selected skinCluster
    Creates two sets:
        _bp_joints_workfSet# - for temporary joints as hold,
        _mute_infs_workSet# - for mute nodes
    
    Usage:
        Select skinCluster to start
    Return:
        dict, with infuences and their data(
            "hold", "mute", 
            "bp"(world space bind matrix), "mtx"(current world matrix)
        )
    """
    print "A"
    if not scl:
        ls_scl = pm.ls(type="skinCluster", sl=1)
        if not ls_scl:
            return
        scl = ls_scl[0]
    print "B"
    # infs, inf_data = get_pb_data(scl)
    # infs = get_infs(scl)
    print "C"
    inf_data = get_inf_data(scl)
    # inf_data2 = create_bp_joints(inf_data=inf_data)
    print "D"
    holds, mutes = set_bind(scl=scl)
    pm.select(mutes)
    pm.sets(holds, n="_bp_joints_workfSet#")
    pm.sets(mutes, n="_mute_infs_workSet#")
    print "END"
    return holds, mutes
#mute_items = pm.selected()
#revert_mute(scl=scl)
def unmute(mute_items=None, scl=None, inf_data=None):
    """Select mute nodes, or use arg scl for skinCluster """
    state = False
    mute_items = pm.ls(mute_items) or pm.ls(sl=1, type="mute")
    ls_scl = pm.ls(scl) or pm.ls(sl=1, type="skinCluster")
    if not mute_items:
        if ls_scl:
            scl = ls_scl[0]
        if scl:
            infs, data = get_inf_data(scl)
            for x in infs:
                ls_mute = x.inputs(type="mute")
                if ls_mute:
                    mute_items.extend(ls_mute)
        else:
            if inf_data:
                mute_items = [v["mute"]
                              for k, v
                              in inf_data.items()
                              if v.has_key("mute")]
            else:
                return state
    hold_items = []
    if mute_items:
        hold_items = [x.h.inputs()[0]
                      for x in mute_items
                      if x.h.inputs()]
    for x in mute_items:
        x.m.set(0)
    try:
        pm.delete(mute_items)
        state = True
    except Exception as err:
        state = False
        print err
    try:
        pm.delete(hold_items)
    except Exception as err:
        state = False
        print err
    return state

def get_inf_data(scl):
    """Returns(list,dict):
        - influecnes
        - their data : bp - bind world matrix, mtx - current matrix,
            parent - their space
    """
    # scl = pm.PyNode("skinCluster1")
    scl = pm.PyNode(scl)
    inf_data = {}
    ls_dpnode = scl.bp.inputs(type="dagPose")
    if not ls_dpnode:
        return None, None
    infs = []
    for plg in ls_dpnode[0].m.iterDescendants():
        bad_msg = ["Damaged dagPose:"]
        bad_news = False
        ls_inf = plg.inputs()
        if not ls_inf:
            bad_news = True
            bad_msg.append(str(plg))
            continue
        infs.append(ls_inf[0])
        bp_m = ls_dpnode[0].wm[plg.index()].get()
        inf_data[ls_inf[0]] = {"bindmat":bp_m, "mat":ls_inf[0].getMatrix(ws=1)}
    return infs, inf_data

def create_bp_joints(scl=None, inf_data=None):
    """Creates temporary joints for bind poses and
    adds them to objectSet _bp_joint_workSet1
    
    Returns(dict) - Updated influences data:
        - per influence dict adding new key - hold for new items
    """
    tmp_jnts = []
    if not inf_data:
        if not scl:
            return
        inf_data = get_pb_data(scl)
    for jnt, data in inf_data.items():
        print jnt, data
        tmpjnt = None
        par = data["parent"]
        if par:
            tmpjnt = pm.joint(par, n="tmp_pb_join#")
        else:
            pm.select(d=1)
            tmpjnt = pm.joint(n="tmp_pb_join#")
        
        pm.xform(tmpjnt, ws=1, m=data["bp"])
        tmp_jnts.append(tmpjnt)
        inf_data[jnt]["hold"] = tmpjnt

    if tmp_jnts:
        pm.sets(tmp_jnts, n="_bp_joints_workfSet#")
    return inf_data

# gobind tools #
def get_infs(scl):
    scl = pm.PyNode(scl)
    infs = scl.ma.inputs()
    return infs

def set_bind(infs=None, scl=None, inf_data=None):
    """Using dagPose or per influence.bindPose
    to temporarly mute channels as in bind moment
    """
    infs = pm.ls(infs)
    hold_items = []
    mute_items = []
    if scl:
        print " <i>  Using skinCluster's dagPose matraces xD"
        infs, inf_data = get_inf_data(scl)
    if inf_data:
        bind_mats = [v["bindmat"] for k, v in inf_data.items()]
    else:
        infs = get_infs(scl)
        print " <i>  Using Influence's own bindPose matrix"
        bind_mats = [x.bps.get() for x in infs]
    for inf, bindmat in zip(infs, bind_mats):
        hold, mutes = do_set_bind(inf, bindmat)
        mute_items.append(mutes)
        hold_items.append(hold)
        # data["mutes"] = mutes
        # data["hold"] = hold
    return hold_items, mute_items

def do_set_bind(inf, bindmat=None):
    if not bindmat:
        bindmat = inf.bps.get()
    par = inf.getParent()
    
    mutes = []
    plugs = (inf.t.getChildren()
           + inf.r.getChildren()
           + inf.s.getChildren())

    hold = pm.joint(par, n="tmp_pb_"+inf)
    pm.xform(hold, ws=1, m=bindmat)
    for plg in plugs:
        at = plg.attrName(longName=1)
        ls_inp = plg.inputs(p=1)
        plgI = None
        plgH = hold.attr(at)
        plgM = plg
        if ls_inp:
            plgI = ls_inp[0]
        else:
            plgI = plg.get()
            if plg.type() == "doubleAngle":
                plgI *= pi / 180
                print "{} >> {}".format(plg.get(), plgI)
        mutes.append(mute_plug(plgI, plgH, plgM, 1))
    return hold, mutes
                
def mute_plug(plgI, plgH, plgM, mute=None):
    """Args:
        - plgI, plgH - (float/str/pm.Attribute)inputs
    Returns (object) - mute node
    """
    if mute is None:
        mute = 0
    mut = pm.createNode("mute", ss=1, n="tmpmute_"+plgM.replace(".", "_"))
    if isinstance(plgI, float):
        mut.i.set(plgI)
    else:
        pm.PyNode(plgI) >> mut.i
    if isinstance(plgH, float):
        mut.h.set(plgH)
    else:
        pm.PyNode(plgH) >> mut.h
    mut.o >> pm.PyNode(plgM)
    mut.m.set(mute)
    return mut
def mute_inf(inf):
    inf = pm.PyNode(inf)
    bp_m = inf.bps.get()
    return bp_m