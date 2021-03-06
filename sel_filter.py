#v0.1a -fix- form_label(): non dag types

import maya.mel as mel
import pymel.core as pm

class SelFilter(object):
    
    tf = None
    
    def main(self):
        win = pm.window("SelectionFilter#", tlb=1)
        lay = pm.formLayout()
        tf = pm.iconTextScrollList("ITMFILTERLIST", ams=1,
                                   dcc=self.select)
        lay1 = pm.rowColumnLayout(nc=5)
        okbt = pm.iconTextButton("OKBTN", l="Reload", i1="cube",
                                 c=self.update)
        addbt = pm.iconTextButton("ADDBTN", l="Add", i1="addDivision24",
                                 c=self.append)
        selbt = pm.iconTextButton("SELBTN", l="Select", st="iconAndTextCentered",
                                  i1="aselect",
                                  # i1="menuIconSelect",
                                  c=self.select,
                                  dcc=pm.Callback(self.select, add=1))
        cbt = pm.button("Close", c=pm.Callback(pm.deleteUI, win))
        aebt = pm.iconTextButton("TOAE", l="Show in AE", i1="attributes",
                                 c=self.showInAE)
        
        lay.attachForm(tf, "top", 2)
        lay.attachForm(tf, "left", 2)
        lay.attachForm(tf, "right", 2)
        lay.attachControl(tf, "bottom", 2, lay1)
        lay.attachForm(lay1, "left", 2)
        lay.attachForm(lay1, "right", 2)
        lay.attachForm(lay1, "bottom", 5)
        
        self.tf = tf
        
        self.update()
        win.show()

    def update(self):
        tf = self.tf
        tf = pm.ui.IconTextScrollList(str(tf))
        tf.removeAll()
        lssl = pm.selected()
        # tf.extend(form_labels(lssl))
        items = form_labels(lssl)
        for it in items:
            tf.append(it)
        tf.setSelectItem(items)
    
    def append(self):
        tf = self.tf
        tf = pm.ui.IconTextScrollList(str(tf))
        lssl = pm.selected()
        # tf.extend(form_labels(lssl))
        items = form_labels(lssl)
        for it in items:
            tf.append(it)
        tf.setSelectItem(items)
    
    def showInAE(self, *args):
        items = self.getNodeNames()
        mel.eval("updateAE {}".format(items[0]))
        
    def getNodeNames(self, *args):
        lssl = None
        items = self.tf.getSelectItem()
        if items:
            lssl = [x.split("\t")[0] for x in items]
        return lssl
    
    def select(self, *args, **kwargs):
        pm.select(pm.ls(self.getNodeNames()), **kwargs)
            
# lssl = pm.selected()
# sel = lssl[0]
# print form_label(sel)
# print form_labels(lssl)

def form_labels(lssl):
    
    uq_items = []
    for sel in lssl:
        lbl = form_label(sel)
        if lbl not in uq_items:
            uq_items.append(lbl)
    return uq_items
def form_label(sel):
    """IF transform has shape returns string with 
    its type in parentesis: transform(mesh)
    ELSE: transform will be shown as group
    ELSEIF transform is constrained or connected: transform(constrained)
    ELSE: nondag
    """
    
    sel, typ = pm.ls(sel, st=1)
    # inh_types = sel.type(i=1)
    # class_typ = "dagNode" if pm.objectType(sel, isa="dagNode") else "nondag"
    node_cls = "dagNode"
    if  not pm.objectType(sel, isa="dagNode"):
        node_cls = "nondag"
    if pm.objectType(sel, isa="shape"):
        node_cls = "shape"
            

    # if class_typ == "dagNode":
    #     node_typ = sel.type(i=1)[3]
    #     if sel.getShape():
    #         typ = sel.getShape().type()
    sel_data = "{}\t[{}]\t({})".format(sel, node_cls, typ)    
    print sel_data
    return sel_data

if __name__ == "__main__":
    _e = SelFilter()
    _e.main()