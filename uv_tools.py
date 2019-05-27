#v0.1a  -new-  combine()
#v0.1   -new-  split_shells()
#       -new-  get_uv_shells()
#       -upd-  unfold() fix kwarg behavior
#       -ren-  doIt() > unfold()
#v0.0

"""unfold() based on some approaches from TNTII_FlattenModel.mel by TNTII1981:
    >> `PolySelectConvert 4;polySelectBorderShell 1;SplitVertex`
        *split vertices by uv borders
    >> `polyEvaluate -bc2`
        *get first and third values of bbx of uv cmop

    split_shells() based on rebbs *finger crossed* answer in polycount
    get_uv_shells() modified version of findUvShells() by Owen Burgess
"""

import maya.OpenMaya as om
import pymel.core as pm
import maya.cmds as cm

def unfold_by_uvs(sel=None):
    lssl = pm.ls(sel)
    if not lssl:
        lssl = [x for x in pm.selected() if x.getShape().type() == "mesh"]
    
    for sel in lssl:
        # split first
        uvs = sel.map
        pm.select(uvs)
        bord_uvs = pm.polySelectConstraint(
            t=0x0010, uv=0, bo=1, m=2, returnSelection=1)
        pm.polySplitVertex(bord_uvs, ch=0)

        # unfold in space
        for vtx in sel.vtx:
            uvbb = pm.polyEvaluate(vtx, bc2=1)
            pm.move(vtx, uv_to_ws(uvbb[0][0], uvbb[1][1], flat="z"))

def uv_to_ws(u, v, flat=None):
    # axis to flatten, default 0"x"
    axis = {"x":0, "y":1, "z":2}    # 0, 1, 2
    ax = 0
    if flat and isinstance(flat, (str, unicode)):
        ax = axis[flat]
    pos = [0.0, 0.0, 0.0]   # "x", "y", "z"
    uv_to_coords = u, v # "u", "v"
    i = (ax+1)%3
    j = ax if axis["z"] == i else i%2
    pos[i] = uv_to_coords[j]
    k = (i+1)%3
    m = ax if axis["z"] == k else (j+1)%2
    pos[k] = uv_to_coords[m]
    return pos

def uv_borders(lssl=None, dosel=None):
    tim = cm.timerX(st=1)

    lssl = cm.ls(lssl)
    if not lssl:
        lssl = [x for x
                  in cm.ls(tr=1)
                  if cm.listRelatives(x, s=1, type="mesh")]
    
    for sel in lssl:
        # split first
        uvs = cm.ls(sel+".map[*]")
        cm.select(uvs)
        # bord_uvs = cm.polySelectConstraint(
        #     t=0x0010, uv=0, bo=1, m=2, returnSelection=1)
        bord_uvs = cm.polySelectConstraint(
            t=0x0010, uv=0, bo=1, m=2, returnSelection=1)
        # cm.select(bord_uvs)
        # ed = cm.ls(sl=1)[0]
        edgs = cm.filterExpand(cm.polyListComponentConversion(bord_uvs, te=1, internal=1), sm=32)
        uv2edg = []
        for ed in edgs:
            # cm.select(ed)
            uvs = cm.filterExpand(cm.polyListComponentConversion(ed, tuv=1), sm=35)
            if len(uvs) > 2:
                uv2edg.append(ed)
    print ("Finidshed in: ", cm.timerX(st=1) - tim)
    cm.polySelectConstraint(bo=0)
    if dosel:
        cm.select(uv2edg)
    else:
        cm.select(lssl)
    return uv2edg

# obsolete
def _split_shells_(lssl=None):
    lssl = cm.ls(lssl)
    if not lssl:
        lssl = [x for x
                  in cm.ls(tr=1)
                  if cm.listRelatives(x, s=1, type="mesh")]
    for sel in lssl:
        bord_uvs = uv_borders(sel)
        cm.polySplitEdge(bord_uvs, ch=0)

def unfold(sel=None):
    tim = cm.timerX(st=1)

    lssl = cm.ls(sel, l=1)
    if not lssl:
        lssl = [x for x
                  in cm.ls(tr=1, l=1, sl=1)
                  if cm.listRelatives(x, s=1, type="mesh")]
        if not lssl:
            return
    
    for sel in lssl:
        # split first
        split_shells(sel)
        vtxs = cm.filterExpand(cm.ls(sel+".vtx[*]"), sm=31)
        # unfold in space
        for vtx in vtxs:
            uvbb = cm.polyEvaluate(vtx, bc2=1)
            # pos = uv_to_ws(uvbb[0][0], uvbb[1][1], flat="z")
            # cm.move(pos[0], pos[1], pos[2], vtx)
            cm.move(0, uvbb[1][1], uvbb[0][0], vtx)
    print ("Finidshed in: ", cm.timerX(st=1) - tim)

def split_shells(sel=None, uvset=None, hist=None):
    """Splitting edges by uv shell borders
    # Partially based on rebb's code:
        https://polycount.com/discussion/52722/maya-mel-script-help-needed-uv-border-edges/p1
    
    # TODO: 
        - optimipztion:
            get_uv_shells() is revoking each time
            edges are modified(splitting)
    
    # Using:
        - get_uv_shells()
    
    # Usage:
        select objects:
        >> split_shells(hist=True)

    # Args:
        - sel, str, if None current selections will be used
        - uvset, str, if None current uvSet will be used for
           each selection
        - hist, bool, construction history preservation, 
           default is True
    
    # Returns:
        >> 0  # on success
    """
    
    # solve selection
    lssl = cm.ls(sel, l=1)
    if not sel:
        lssl = cm.ls(sl=1, l=1)
        if not lssl:
            return

    # uv component name
    attr = "map"
    
    # resolve kwargs for all selection
    hist = True if hist is None else hist
    
    for sel_l in lssl:
        # resolve kwargs for each selection
        if not uvset:
            # if not given use current
            uvset = cm.getAttr(sel_l + ".cuvs")
        else:
            # if given, check if exists
            alluvs = cm.polyUVSet(sel_l, q=1, auv=1)
            if sel not in alluvs:
                msg = "  ! Not found in: '{}':'{}'"
                print msg.format(uvset, sel_l),
                continue
        
        shells = get_uv_shells(sel_l, uvSet=uvset)
        # shell = shells[0]
        print ">", sel_l
        for i in range(len(shells)):
            comps = []
            for j in shells[i]:
                comp = "{}.{}[{}]".format(sel_l, attr, j)
                comps.append(comp)
            #cm.select(comps)
            # chippoff shells except first(0)
            if i:
                # convert to containing face and flatten list
                #   (faster than `ls -fl ..`)
                shell2face = cm.filterExpand(
                        cm.polyListComponentConversion(comps, tf=1, internal=1),
                        sm=34)
                #cm.select(shell2face)
                chipoff = cm.polyChipOff(shell2face, dup=0, ch=hist)
                comps = cm.polyListComponentConversion(shell2face, tuv=1)
            # select only borders of one shell
            cm.select(comps)     # do not comment this line
            # (!) selection based operation
            # On selection mask type to "uv borders"
            bord_uvs = cm.polySelectConstraint(
                        t=0x0010, uv=0, bo=1, m=2, returnSelection=1)
            # Off "uv borders" mask
            cm.polySelectConstraint(bo=0)
            #cm.select(bord_uvs)
            # convert to edge and flatten list
            edgs = cm.filterExpand(
                cm.polyListComponentConversion(bord_uvs, te=1, internal=1),
                sm=32)
            #cm.select(edgs)
            # filter edges by uv
            uv2edg = []
            for ed in edgs:
                # cm.select(ed)
                uvs = cm.filterExpand(
                    cm.polyListComponentConversion(ed, tuv=1),
                    sm=35)
                if len(uvs) > 2:
                    uv2edg.append(ed)
            #cm.select(uv2edg)
            if uv2edg:
                cm.polySplitEdge(uv2edg, ch=hist)
                # update shells
            # update uv shells' uv points
            shells = get_uv_shells(sel_l, uvSet=uvset)
    return 0

def get_uv_shells(sel, uvSet=None):
    """Modified version of findUvShells() by Owen Burgess 2011
       https://mayastation.typepad.com/maya-station/2011/03/how-many-shells-in-a-uv-set-.html
    
    # Args/kwargs:
        - sel, str(dagPath), long name of dagNode/xform ("|pCube1")
        - uvSet, str, if None default name "map1" will be used
    
    # Returns 2d array[s][uv] of indices separated by uv shells:
        >> [[0, 1, 2...], [15, 16, 17..]]
    Each item [s] represents shell with its uv(.map[x]) points [uv]
    """
    uvSet = uvSet or "map1"
    selList = om.MSelectionList()
    om.MGlobal.getActiveSelectionList(selList)
    selListIter = om.MItSelectionList(selList, om.MFn.kMesh)
    
    selList.add(sel)
    omdagp = om.MDagPath()
    selList.getDagPath(0, omdagp)
    
    uvShellArray = om.MIntArray() 
    meshNode = sel
    
    # continue only if the given UV set exists on the shape
    uvSets = cm.polyUVSet(meshNode, query=True, allUVSets =True)
    
    uvshells = []
    if (uvSet in uvSets):
        shapeFn = om.MFnMesh(omdagp)
    
        shells = om.MScriptUtil()
        shells.createFromInt(0)
        shellsPtr = shells.asUintPtr()
    
        shapeFn.getUvShellsIds(uvShellArray, shellsPtr, uvSet)
    
        # optional : print the shell index of each UV
        for i in range(shells.getUint(shellsPtr)):
            # print "shell [{}]:".format(i),
            shell = []
            for j, k in enumerate(uvShellArray):
                if i == k:
                    # print j,
                    shell.append(j)
            uvshells.append(shell)
            
    return uvshells

def shell_border(comps, select=None):
    cm.select(comps)
    bord_uvs = cm.polySelectConstraint(
                t=0x0010, uv=0, bo=1, m=2, returnSelection=1)
    cm.polySelectConstraint(bo=0)
    # convert to edge and flatten list
    edgs = cm.filterExpand(
        cm.polyListComponentConversion(bord_uvs, te=1, internal=1),
        sm=32)
    # filter edges by uv
    uv2edg = []
    for ed in edgs:
        # cm.select(ed)
        uvs = cm.filterExpand(
            cm.polyListComponentConversion(ed, tuv=1),
            sm=35)
        if len(uvs) > 2:
            uv2edg.append(ed)
    if select:
        cm.select(uv2edg)
    return uv2edg

def smooth_shells(lssl=None, hist=None):
    """Usage(optional, select objects):
    >> smooth_shell(hist=False)
    Args:
     - hist, bool, (default True) construction history
    """
    lssl = cm.ls(lssl)
    if not lssl:
        lssl = [x for x 
                  in cm.ls(sl=1)
                  if cm.listRelatives(x, s=1, type="mesh")]
    hist = True if hist is None else hist
    for sel in lssl:
        cm.polySoftEdge(sel, a=180, ch=hist)
        borders = shell_border(sel + ".map[*]")
        # cm.select(borders)
        cm.polySoftEdge(borders, a=0, ch=hist)

def combine(comps=None, move=None, hist=None):
    """Sews all internal edges of given shell [Select uv shell]"""
    
    hist = True if hist is None else hist
    lssl = cm.ls(comps, type="float3")
    if not lssl:
        lssl = cm.ls(sl=1, type="float3")

    inner_e = cm.polyListComponentConversion(lssl, internal=1, te=1)
    if move:
        cm.polyMapSewMove(inner_e, nf=10, lps=0, ch=hist)
    else:
        cm.polyMapSew(inner_e, ch=hist)
