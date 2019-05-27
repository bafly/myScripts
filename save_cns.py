#v0.0b -fix- restore(): return immediately if no constraints
#      -new- find(), save(), restore()
#      -ren- eval() > cns_eval(), save() > doSave(), restore() > doResotre()
#      -upd- save(), restore(): handle point, orient and aim constraints
#v0.0a -fix- save(): return immediately if no constraints
#v0.0

import maya.mel as mel
import pymel.core as pm

# sel = pm.selected()[0]
# save_cns_data(sel)
# restore_cns(sel)

def save(lssl=None):
    lssl = pm.ls(lssl)
    if not lssl:
        lssl = pm.selected()
    for sel in lssl:
        doSave(sel)

def doSave(sel):
    
    sel = pm.PyNode(sel)
    ls_cns = sel.pim.outputs(type="constraint")
    cns_at = "cnsData"
    cns_data = {}
    lock = 1
    if ls_cns:
        if not sel.hasAttr(cns_at):
            sel.addAttr(cns_at, dt="string")
        else:
            if not sel.isReferenced():
                sel.attr(cns_at).unlock()
    else:
        return cns_data
    for cns in ls_cns:
        cns_t = cns.type()
        print cns_t
        trg_sz = cns.tg.get(s=1)
        trgs_data = {}
        offsets = ["tot", "tor", "tos"]
        # 0: target, offset_t, offset_r, offset_r, weight)
        for i in range(trg_sz):
            trg_data = {}
            trg_offset_d = dict((x,[0, 0, 0]) for x in offsets)
            trg_plg = getattr(cns, "tg[{}]".format(i))
            ls_trg = trg_plg.tpm.inputs()
            if not ls_trg:
                # constraint is broken
                continue
            trg = ls_trg[0]
            # trgs_data["targets"].append(trg.nodeName())
            if cns_t == "parentConstraint":
                trg_offset_d["tot"] = trg_plg.tot.get().tolist()
                trg_offset_d["tor"] = trg_plg.tor.get().tolist()
            else:
                key = None
                if cns_t == "pointConstraint":
                    key = "tot"
                else:
                    if cns_t in ["orientConstraint", "aimConstraint"]:
                        key = "tor"
                    else:
                        if cns_t == "scaleConstraint":
                            key = "tos"
                if key:
                    trg_offset_d[key] = cns.o.get().tolist()
            # if cns_t == "scaleConstraint":
            #     trg_offset_d["tos"] = cns.o.get().tolist()
            # if cns_t == "pointConstraint":
            #     trg_offset_d["tot"] = cns.o.get().tolist()
            # if cns_t == "pointConstraint":
            #     trg_offset_d["tot"] = cns.o.get().tolist()
            trg_w = cns.attr("w{}".format(i)).get()
            trg_data.update({"name":trg.nodeName()})
            trg_data.update({"weight":trg_w})
            trg_data.update(trg_offset_d)
            trgs_data[i] = trg_data
        cns_data[cns_t] = trgs_data
    print cns_data
    sel.attr(cns_at).set(repr(cns_data))
    if lock and not sel.isReferenced():
        sel.attr(cns_at).lock(lock)
    return cns_data

def restore(lssl=None):
    """select transform(s)"""
    lssl = pm.ls(lssl)
    if not lssl:
        lssl = pm.selected()
    for sel in lssl:
        ls_cns = find(sel)
        if ls_cns:
            user_inp = pm.confirmDialog(
                m="Delete existing constraints on {}?".format(sel),
                b=["Delete", "Cancel"],
                cb="Cancel",
                db="Cancel"
                )
            if user_inp == "Cancel":
                continue
        pm.delete(ls_cns)
        doRestore(sel)

def doRestore(sel):
    sel = pm.PyNode(sel)
    cns_at = "cnsData"
    if not sel.hasAttr(cns_at):
        return
    cns_data = eval(sel.attr(cns_at).get())
    
    for cns_t, dat in cns_data.items():
        trgs = [dat[x]["name"] for x in dat]
        cns = eval_cns(cns_t, trgs, sel)
        if not cns:
            continue
        cns = pm.PyNode(cns)
        if cns_t == "parentConstraint":
            for i in dat:
                trg_plg = cns.attr("tg[{}]".format(i))
                trg_plg.tot.set(dat[i]["tot"])
                trg_plg.tor.set(dat[i]["tor"])
        else:
            key = None
            if cns_t == "scaleConstraint":
                key = "tos"
            else:
                if cns_t == "pointConstraint":
                    key = "tot"
                else:
                    if cns_t in ["orientConstraint", "aimConstraint"]:
                        key = "tor"
            if key:
                for i in dat:
                    cns.o.set(dat[i][key])

def eval_cns(cns_t, targets, child):
    cns = None
    eval_cmd = str(cns_t)
    targets = pm.ls(targets)
    for trg in targets:
        eval_cmd += " " + str(trg)
    eval_cmd += " " + str(child)
    ls_cns = mel.eval(eval_cmd)
    if ls_cns:
        cns = ls_cns[0]
    return cns

def find(sel):
    sel = pm.PyNode(sel)
    ls_cns = sel.pim.outputs(type="constraint")
    return ls_cns
