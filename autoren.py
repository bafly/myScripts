#0.1f   upd doRename(): fix idx placeholder find logic(works with "spine#_env")
#0.1e   upd doRename(): fix endless renaming loops
#0.1d   new findNextIndex()
#v0.1c      saveCurrentNames
#v0.1b      adding tabs
#v0.1a

"""UI for renaming selected items
"""

import pymel.core as pm

#template = "hand_L_##_org"
def doRename(template, lssl=None):
    if not lssl:
        lssl = pm.selected()
    sz = len(lssl)
    print "Renaming by template: {}".format(template)
    ls_padding = [x for x in template.split("_") if x.startswith("#")]
    padding = 1
    if not ls_padding:
        ls_padding = [x for x in template.split("_") if x.endswith("#")]
        if not ls_padding:
            print " Index paddings not found, use: ## if one of the field"
            return
    padding = ls_padding[0].count("#")
    print "Given padding: ", padding
    # check if padding can store selection size
    cur_pad = len(repr(sz))
    # if padding is greater than one and number of item is exceeds
    #   padding will conform that items count
    if  padding > 1 and cur_pad > padding:
        print " Extending currentPadding to: ", cur_pad
        padding = cur_pad
    idx_part = "1"
    pad_stt = template.find("#")
    pad_cnt = template.count("#")
    repl = template[pad_stt:pad_stt+pad_cnt]
    for i, sel in enumerate(lssl):
        setCurrentName(sel)
        idx = int(idx_part)
        idx_part = findNextIndex(template, idx)
        # idx_part = "{}".format(idx).zfill(padding)
        # new_name = template.replace(ls_padding[0], idx_part)
        print "repl: " + repl
        new_name = template.replace(repl, idx_part)
        if sel.nodeName() == new_name:
            continue
        print "newn: " + new_name
        print "Renaming: {} to: {}".format(sel, new_name)
        if pm.objExists(new_name):
            print " ! Already exists {}".format(new_name)
            new_name += "#"
            print "   adding number at the end {}".format(new_name)
        sel.rename(new_name)
        sel.isRenamed.set(1)

def saveCurrentNames(lssl=None):
    if not lssl:
        lssl = pm.selected()
    if not lssl:
        return
    for sel in lssl:
        setCurrentName(sel)
        
def setCurrentName(sel):
    at = "oldName"
    at2 = "isRenamed"
    if not sel.hasAttr(at):
        sel.addAttr(at, dt="string")
    sel.attr(at).set(sel.nodeName())
    if not sel.hasAttr(at2):
        sel.addAttr(at2, at="bool")
    sel.attr(at2).set(0)

def findNextIndex(template, idx=None, placer=None):
    """Iterating from 1 to 10000 replacing placer('##')
        in template with iteration
    
    # Args:
        # template - str, "name_##"
        # idx - starting with given index instead of 1
    # Returns: str, "index"
    """
    placer = placer or "#"
    # ls_placer = [x for x in template.split("_") if x.endswith("#")]
    pad_stt = template.find(placer)
    if not pad_stt:
        print "  Index Placer(\"#\") not found"
        return
    pad_cnt = template.count(placer)
    idx = 1 if idx is None else int(idx)
    print "\n#              {}              #\n".format(idx)
    idx_str = str(idx).zfill(pad_cnt)
    repl = template[pad_stt:pad_stt+pad_cnt]
    check_name = template.replace(repl, idx_str)
    print "chk: ", check_name
    if not pm.objExists(check_name):
        print "! Exists"
    while pm.objExists(check_name) and int(idx) < 10000:
        print "Exists: {}".format(check_name)
        idx += 1
        idx_str = str(idx).zfill(pad_cnt)
        check_name = template.replace(repl, idx_str)
    return idx_str

################################## UI #################################
def main():
    
    # create controls
    win = pm.window(t="autoren", tlb=1)
    tab = pm.tabLayout(showNewTab=1, tc=1)
    tab.newTabCommand(pm.Callback(createNewTab, tab))
    
    # create first tab
    createNewTab(tab, "base")

    win.show()

def createNewTab(tab, name=None):
    
    if not name:
        user_inp = pm.promptDialog(m="Tab Name")
        if user_inp != "Confirm":
            return
        name = pm.promptDialog(q=1, tx=1)
        if not name:
            name = "name set#"
    lay = pm.formLayout(name, p=tab)
    add_btn_pfx = pm.button("pfxAddBtn", p=lay, l="+")
    rm_btn_pfx = pm.button("pfxRmBtn", p=lay, l="-")
    add_btn_sfx = pm.button("sfxAddBtn", p=lay, l="+")
    rm_btn_sfx = pm.button("sfxRmBtn", p=lay, l="-")
    lay1 = pm.rowColumnLayout(adj=1)
    # txf = pm.textField()
    txf = pm.textField(sf=1, h=25)
    okbtn = pm.button("Rename", p=lay)
    
    # align controls
    lay.attachForm(add_btn_pfx, "left", 5)
    lay.attachControl(rm_btn_pfx, "left", 5, add_btn_pfx)
    lay.attachControl(lay1, "left", 5, rm_btn_pfx)
    lay.attachForm(add_btn_sfx, "right", 5)
    lay.attachControl(rm_btn_sfx, "right", 5, add_btn_sfx)
    lay.attachControl(lay1, "right", 5, rm_btn_sfx)
    lay.attachForm(lay1, "top", 0)
    lay.attachForm(okbtn, "left", 5)
    lay.attachControl(okbtn, "top", 5, lay1)
    pm.formLayout(lay, e=1, aoc=(okbtn, "right", 0, add_btn_sfx))
    
    # assign commands
    add_btn_pfx.setCommand(pm.Callback(addBtnPress, rm_btn_pfx, rm_btn_sfx, lay1, 0))
    rm_btn_pfx.setCommand(pm.Callback(rmBtnPress, rm_btn_pfx, rm_btn_sfx, lay1, 0))
    add_btn_sfx.setCommand(pm.Callback(addBtnPress, rm_btn_pfx, rm_btn_sfx, lay1))
    rm_btn_sfx.setCommand(pm.Callback(rmBtnPress, rm_btn_pfx, rm_btn_sfx, lay1, -1))
    txf.enterCommand(pm.Callback(addBtnPress, rm_btn_pfx, rm_btn_sfx, lay1))
    okbtn.setCommand(pm.Callback(okCmd, lay1))
    
    # update controls
    updateButtons(rm_btn_pfx, rm_btn_sfx, lay1)
    pm.dimWhen("SomethingSelected", okbtn, f=1)

def okCmd(lay):
    lssl = pm.selected()
    res = getRenameScheme(lay)
    doRename(res)

def getRenameScheme(lay):
    ls_ch = lay.getChildren()
    parts = []
    for txf in ls_ch:
        parts.append(txf.getText())
    res = "_".join(parts)
    return res

def updateButtons(rmbtn1, rmbtn2, lay):
    print "Chceking"
    items = lay.getChildren()
    sz = len(items)
    # set textfiled tooltips
    tooltips = [
        "upperArm/prop",
        "L/M/R",
        "##/org/sim/noSubdiv"
    ]
    
    for idx, txf in enumerate(items):
        pos = idx if idx < 3 else -1
        txf.setPlaceholderText(tooltips[pos])
    # set button states
    res = sz > 1
    rmbtn1.setEnable(res)
    rmbtn2.setEnable(res)

def rmBtnPress(rmbtn1, rmbtn2, lay, pos=None):
    res = rmTXF(lay, pos=pos)
    updateButtons(rmbtn1, rmbtn2, lay)
    #rmbtn1.setEnable(res)
    #rmbtn2.setEnable(res)
    
def addBtnPress(rmbtn1, rmbtn2, lay, pos=None):
    new = addTXF(lay, pos=pos)
    new.enterCommand(pm.Callback(addBtnPress, rmbtn1, rmbtn2, lay))
    pm.setFocus(new)
    print new
    updateButtons(rmbtn1, rmbtn2, lay)
    #rmbtn1.setEnable(1)
    #rmbtn2.setEnable(1)
#lay = lay1
def addTXF(lay, pos=None):
    # default appends
    ls_ch = lay.getChildren()
    txf = pm.textField(sf=1, h=25, p=lay)
    if pos is None:
        ls_ch.append(txf)
    else:
        ls_ch.insert(pos, txf)
        lay_new = pm.rowColumnLayout()
        for x in ls_ch:
            pm.textField(x, e=1, p=lay_new)
        for x in ls_ch:
            pm.textField(x, e=1, p=lay)
        lay_new.delete()
    return txf
    
def rmTXF(lay, pos=None):
    """returns False if last item left"""
    pos = pos or 0
    ls_ch = lay.getChildren()
    sz = len(ls_ch)
    if sz > 1:
        to_rm = ls_ch[pos]
        print "Removing: {} at pos: {}".format(pos, to_rm)
        pm.deleteUI(to_rm)
        ls_ch.remove(to_rm)
        sz -= 1
    return bool(sz-1)
    #to_rm.delete()

if __name__ == "__main__":
    main()