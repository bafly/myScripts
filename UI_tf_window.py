import maya.mel as mel
import pymel.core as pm

class SelFilter(object):
    
    tf = None
    
    def main(self):
        win = pm.window("SelectionFilter#")
        lay = pm.formLayout()
        tf = pm.iconTextScrollList("ITMFILTERLIST", ams=1,
                                   dcc=self.showInAE)
        lay1 = pm.rowColumnLayout(nc=4)
        okbt = pm.iconTextButton("OKBTN", l="Reload", i1="cube",
                                 c=self.update)
        selbt = pm.button("SELBTN", l="Select",
                                  c=self.select)
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
    
    def showInAE(self, *args):
        items = self.getNodeNames()
        mel.eval("updateAE {}".format(items[0]))
        
    def getNodeNames(self, *args):
        lssl = None
        items = self.tf.getSelectItem()
        if items:
            lssl = [x.split("\t")[0] for x in items]
        return lssl
    
    def select(self, *args):
        pm.select(pm.ls(self.getNodeNames()))
            
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
    class_typ = sel.type(i=1)[2]
    node_typ = "nondag"
    if class_typ == "dagNode":
        node_typ = sel.type(i=1)[3]
        if sel.getShape():
            typ = sel.getShape().type()
    
    return "{}\t{}\t({})".format(sel, node_typ, typ)

if __name__ == "__main__":
    e = SelFilter()
    e.main()