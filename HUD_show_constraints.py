#v0.1a  # fixed unloading actions
        # upd   selection button now unite all found constraints and allows
        #       to select them

import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel

"""How it works:
    1. HUD_menu_constraint_info():
        (runs from userSetup.mel) Creates [menu item] in display hud submenu
    2. [menu item] on activeate creates simple hud element that triggers
        [next script] on every selection change
    3. HUD_constraint_info_creator()
"""
def HUD_init():
    
    hudname = "HUDConstraintInfo"
    hud_menu_name = hudname + "Menu"
    hud_menu_lbl = "AVFX: Constraint Info"
    opvar = "AVFX_" + hud_menu_name
    visible = cmds.optionVar(q=opvar)
    annot = "Helps to find constraints for current selected child"
    
    # sec = 7 # center
    # nextblk = cmds.headsUpDisplay(nextFreeBlock=9)
    
    # delete if exist
    if pm.menuItem(hud_menu_name, q=1, ex=1):
        pm.deleteUI(hud_menu_name)
        if pm.headsUpDisplay(hudname, ex=1):
            pm.headsUpDisplay(hudname, rem=1)
            rm_hud_constraint_items()
    # find heads up display submenu(Display / Heads Up Display)
    gHeadsUpDisplayMenu = mel.eval("$temp_var = $gHeadsUpDisplayMenu")
    # shoul be added in main creator
    # cmds.menuItem(parent=gHeadsUpDisplayMenu, divider=True)
    
    # add to menu
    cmds.menuItem(
        hud_menu_name,
        parent=gHeadsUpDisplayMenu,
        checkBox=visible,
        label=hud_menu_lbl,
        command=HUD_constraint_trigger,
        annotation=annot)

def HUD_constraint_trigger(state):
    
    """runs only once or if checkbox is disabled"""
    
    # print hudname, wat
    print "1) HUD CREATOR", state

    hudname = "HUDConstraintInfo"
    opvar = "AVFX_" + hudname
    
    if pm.headsUpDisplay(hudname, ex=1):
        pm.headsUpDisplay(hudname, e=1, rem=1)
        rm_hud_constraint_items()
        # pm.headsUpDisplay(hudname, e=1, vis=state)
        
    cmds.optionVar(iv=(opvar, state))
    
    if state:
        sec=7
        blk = pm.headsUpDisplay(nfb=sec)
        lbl = "Constraint(s) on: "

        #pm.deleteUI(hudname)
        pm.headsUpDisplay(hudname,
                          s=sec,
                          b=blk,
                          l=lbl,
                          event="SelectionChanged",
                          command=pm.Callback(
                              HUD_constraint_info_creator,
                              hudname, s=sec, b=blk),
                          vis=state
                          )
        # get cur sel for label
        blk = pm.headsUpDisplay(nfb=sec)
        # hud_constraint_info_set_label(hudname, s=sec, b=blk)

def HUD_constraint_info_creator(*args, **kwargs):
    
    """spawns hud items per found constraint"""
    print "2) Items creator", args, kwargs
    
    hudname = args[0]
    # clear all data first
    rm_hud_constraint_items()
    
    cons = get_anim_constraints()
    cns_sz = len(cons)
    print " | creator.cons: ", cons
    if not cons:
        print " <finder has not found any constarint>"
        hud_constraint_info_set_label(hudname, **kwargs)
        return
    # make cool msg
    msg = "Constarined"
    hud_inview_msg(msg)
    # hud_msg_on_sel(msg, cons[0])

    print " | creator: constraints found, rdy for spawn"
    
    # check and rebuild kwargs
    sec = 7
    if kwargs.has_key("s") or kwargs.has_key("section"):
        if kwargs.has_key("s"):
            sec = kwargs["s"]
        else:
            sec = kwargs["section"]
    blk = pm.headsUpDisplay(nfb=sec)
    if kwargs.has_key("b") or kwargs.has_key("block"):
        if kwargs.has_key("b"):
            blk = kwargs["b"]
        else:
            blk = kwargs["block"]
    # place lbl first with right padding
    # lbl_blk = blk + cns_sz
    lbl_blk = blk + 1
    hud_constraint_info_set_label(hudname, s=sec, b=lbl_blk)
    
    kwargs.update({"s":sec})
    kwargs.update({"b":blk})
    
    # generate hud buttons
    # huds = []
    item = cons[-1]
    item = item + "..." if cns_sz > 1 else item
    hudid = mk_hud_constraint_item(
        item,
        releaseCommand=pm.Callback(pm.select, cons),
        **kwargs)
    # huds.append(hudid)
    # kwargs["b"] += 1
    #hud_constraint_info_set_label(hudname, s=sec, b=blk)
    print " | HUD label: ", pm.headsUpDisplay(hudname, q=1, l=1)
    print " ."
    # return huds

def get_anim_constraints(*args):

    """returns not referenced constraints
        [i] function can be updated without hud reload [i]
    """
    print "   a) Find Anim Constraints: ", args
    lssl = cmds.ls(args)
    if not lssl:
        lssl = cmds.ls(sl=1)
    print "   | Curent Selection: ", lssl
    items = []
    for sel in lssl:
        cons = cmds.listConnections(
                sel+".pim",
                type="constraint",
                s=0, d=1)
        if not cons:
            continue
        for con in cons:
            if not cmds.referenceQuery(con, inr=1):
                items.append(con)
    print "   ."
    return items

def mk_hud_constraint_item(item, **kwargs):
    
    print "  b) Create HUD items: ", kwargs
    # hudname = "HUDCNS_" + item
    hudname = "HUDCNS_"
    sz = len(item)*6
    print "   | hudname: ", hudname
    if pm.headsUpDisplay(hudname, ex=1):
        pm.headsUpDisplay(hudname, rem=1)
    hudid = cmds.hudButton(
        hudname,
        l=item,
        bw=sz,
        visible=1,
        **kwargs
        )
    print "   ."
    return hudid
    
def rm_hud_constraint_items():
    
    del_items = [x for x in cmds.headsUpDisplay(lh=1) if x.startswith("HUDCNS_")]
    [cmds.headsUpDisplay(x, rem=1) for x in del_items]

def rm_hud_lbl(hudname):
    
    if pm.headsUpDisplay(hudname, ex=1):
        pm.headsUpDisplay(hudname, e=1, l="")

def hud_constraint_info_set_label(hudname, **kwargs):
    
    print "3) HUD Label Change: ", hudname
    print " | kwargs: ", kwargs
    lbl = "Constraint(s) from: "
    lssl = pm.ls(sl=1)
    rm_hud_lbl(hudname)
    if lssl:
        trgs = get_cns_src(lssl[-1])
        if not trgs:
            msg = " | Broken constraint"
            print msg
            item = msg
        else:
            print " | item: ", trgs[-1]
            item = trgs[-1]
            lbl += str(item.split("|")[-1])
            if len(trgs) > 1:
                lbl += "..."
            
    print " | label: ", lbl
    # if not pm.headsUpDisplay(hudname, ex=1):
    #     pm.headsUpDisplay(hudname, l=lbl, **kwargs)
    pm.headsUpDisplay(hudname, e=1, l=lbl, **kwargs)

def hud_inview_msg(msg):
    html = ("<span style=\"color:#000000;\">"
                +"<h3>"
                    +"<span style=\"color:#6E6E6E;\">&lt;!&gt;</span> {0}"
                +"</h3>"
            +"</span>"
            )
    html = html.format(msg)
    print " !MSG ", html
    pm.inViewMessage(
        smg=html,
        bkc=0xD0F5A9,
        alpha=0.5,
        fade=1,
        fit=100,
        fot=100,
        pos="midCenterBot",
        fst=2000
        )
# ! crashes maya
def hud_msg_on_sel(msg, sel):

    pm.headsUpMessage(msg, o=sel)


def get_cns_src(item):
    cons = []
    items = pm.ls(item)
    for it in items:
        if pm.objectType(it, isa="constraint"):
            cons.append(it)
        else:
            if pm.objectType(it, isa="transform"):
                cons.extend(it.pim.outputs(type="constraint"))
    tgrs = [x.outputs(p=1)[0].getParent().tpm.inputs()[0] 
               for y in cons for x in y.listAttr(ud=1)]
    return tgrs
