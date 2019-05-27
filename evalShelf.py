import pymel.core as pm
#template = "hand_L_##_org"
def doRename(template, lssl=None):
    if not lssl:
        lssl = pm.selected()
    sz = len(lssl)
    print "Renaming by template: {}".format(template)
    ls_padding = [x for x in template.split("_") if x.startswith("#")]
    padding = 1
    if ls_padding:
        padding = len(ls_padding[0])
        print "Given padding: ", padding
    # check if padding can store selection size
    cur_pad = len(repr(sz))
    if  cur_pad > padding:
        print " Extending currentPadding to: ", cur_pad
        padding = cur_pad
    for i, sel in enumerate(lssl):
        setCurrentName(sel)
        idx = i+1
        idx_part = "{}".format(idx).zfill(padding)
        new_name = template.replace(ls_padding[0], idx_part)
        print "Renameing: {} to: {}".format(sel, new_name)
        if pm.objExists(new_name):
            print " ! Already exists {}".format(new_name)
            new_name += "#"
            print "   adding number at the end {}".format(new_name)
        sel.rename(new_name)
        sel.isRenamed.set(1)
#setCurrentName(pm.selected()[0])
def setCurrentName(sel):
    at = "oldName"
    at2 = "isRenamed"
    if not sel.hasAttr(at):
        sel.addAttr(at, dt="string")
    sel.attr(at).set(sel.nodeName())
    if not sel.hasAttr(at2):
        sel.addAttr(at2, at="bool")
    sel.attr(at2).set(0)

def getUIResultAndRename(lay):
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

def main():
    win = pm.window()
    lay = pm.formLayout()
    add_btn_pfx = pm.button("pfxAddBtn", p=lay, l="+")
    rm_btn_pfx = pm.button("pfxRmBtn", p=lay, l="-")
    add_btn_sfx = pm.button("sfxAddBtn", p=lay, l="+")
    rm_btn_sfx = pm.button("sfxRmBtn", p=lay, l="-")
    lay1 = pm.rowColumnLayout()
    txf = pm.textField(placeholderText="hand")
    #lay1.setHeight()
    add_btn_pfx.setCommand(pm.Callback(addBtnPress, rm_btn_pfx, rm_btn_sfx, lay1, 0))
    rm_btn_pfx.setCommand(pm.Callback(rmBtnPress, rm_btn_pfx, rm_btn_sfx, lay1, 0))
    add_btn_sfx.setCommand(pm.Callback(addBtnPress, rm_btn_pfx, rm_btn_sfx, lay1))
    rm_btn_sfx.setCommand(pm.Callback(rmBtnPress, rm_btn_pfx, rm_btn_sfx, lay1, -1))
    okbtn = pm.button("Rename", p=lay)
    
    lay.attachForm(add_btn_pfx, "left", 5)
    lay.attachControl(rm_btn_pfx, "left", 5, add_btn_pfx)
    lay.attachControl(lay1, "left", 5, rm_btn_pfx)
    lay.attachControl(rm_btn_sfx, "left", 5, lay1)
    lay.attachControl(add_btn_sfx, "left", 5, rm_btn_sfx)
    lay.attachForm(lay1, "top", 0)
    
    lay.attachForm(okbtn, "left", 5)
    lay.attachControl(okbtn, "top", 5, lay1)
    pm.formLayout(lay, e=1, aoc=(okbtn, "right", 0, add_btn_sfx))    
    
    okbtn.setCommand(pm.Callback(getUIResultAndRename, lay1))
    
    updateButtons(rm_btn_pfx, rm_btn_sfx, lay1)
    pm.dimWhen("SomethingSelected", okbtn, f=1)
    win.show()

def updateButtons(rmbtn1, rmbtn2, lay):
    print "Chceking"
    sz = len(lay.getChildren())
    res = sz > 1
    rmbtn1.setEnable(res)
    rmbtn2.setEnable(res)

def rmBtnPress(rmbtn1, rmbtn2, lay, pos=None):
    res = rmTXF(lay, pos=pos)
    rmbtn1.setEnable(res)
    rmbtn2.setEnable(res)
    
def addBtnPress(rmbtn1, rmbtn2, lay, pos=None):
    new = addTXF(lay, pos=pos)
    pm.setFocus(new)
    print new
    rmbtn1.setEnable(1)
    rmbtn2.setEnable(1)
#lay = lay1
def addTXF(lay, pos=None):
    # default appends
    ls_ch = lay.getChildren()
    txf = pm.textField(p=lay)
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
    #pm.textField(txf, e=1, p=lay)
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