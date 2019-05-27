#v0.0

"""Main procs:
 1) to export select object sets
    >> dump()
 2) to import:
    >> load()
"""

import json

import pymel.core as pm

def get_obj_set_data(set):
    prsrv_ns = True
    prsrv_dagp = False
    nm_kwargs = {"long":prsrv_dagp, "stripNamespace":not prsrv_ns}
    obs_data = {}
    pm_items = pm.sets(set, q=1)
    items = [x.name(**nm_kwargs) for x in pm_items]
    obs_data[str(set)] = items
    return obs_data

def dump_data(json_data, fpath=None):
    if not fpath:
        ls_fpath = pm.fileDialog2(fm=0, ff="*.json", cap="Export Object Set")
        if not ls_fpath:
            return
        fpath = ls_fpath[0]
    print " Writing Object Sets data:\n > ", fpath
    with open(fpath, "w") as writefile:
        json.dump(json_data, writefile, indent=1)
    res = pm.Path(fpath).exists()
    if res:
        print " Object Sets >", fpath
        return fpath
    return

def read_data(fpath=None):
    if not fpath:
        ls_fpath = pm.fileDialog2(fm=1, ff="*.json", cap="Import Object Set")
        if not ls_fpath:
            return
        fpath = ls_fpath[0]
    print "\n Importing Object Sets data:\n > ", fpath
    json_data = {}
    with open(fpath) as readfile:
        json_data = json.load(readfile)
    # print json_data
    if json_data:
        print " Object Sets:\n > ", json_data
    return json_data

def create_obj_sets(json_data, ove=None):
    if ove is None:
        ove = False
    objsets = []
    chk_success = True
    for objset, items in json_data.items():
        ls_items = pm.ls(items)
        chk_exists = len(items) == len(ls_items)
        if not chk_exists:
            chk_success = False
            abs_items = [x for x in items if not pm.objExists(x)]
            print "\n (i) {0}: Some objects not found".format(objset), 
            print "\n   > ", abs_items,

        if pm.objExists(objset):
            if ove:
                pm.delete(objset)
        if not pm.objExists(objset):
            pm.sets(n=objset, em=1)
        
        pm.sets(objset, add=ls_items)
        objsets.append(objset)
    if chk_success:
        print "\n ^_^",
    return objsets

def dump():
    lssl = pm.ls(sl=1, sets=1)
    if not lssl:
        print " Select \"objectSet\"s",
        return
    json_data = {}
    [json_data.update(get_obj_set_data(x)) for x in lssl]
    fpath = dump_data(json_data)
    if not fpath:
        print "Export failed. Check directory write restriction",
        return
    return fpath

def load(*args, **kwargs):
    """kwargs: may acces: ove - bool, override existing object sets
    """
    json_data = read_data(*args)
    if not json_data:
        print "Import failed. Check if file exists, nor its not empty",
        return
    json_obj_sets = json_data.keys()
    chk_exists = pm.ls(json_obj_sets, sets=1)
    if chk_exists:
        if not kwargs.has_key("ove"):
            count = ""
            if len(chk_exists) == json_obj_sets:
                count = "Some "
            user_inp = pm.confirmDialog(m=count + "Ojbect Sets already exist",
                                        b=["Override", "Append", "Cancel"],
                                        cb="Cancel",
                                        db="Cancel",
                                        ds="Cancel")
            if user_inp == "Cancel":
                return
            if user_inp == "Override":
                kwargs["ove"] = True
    print " kwargs:", kwargs
    create_obj_sets(json_data, **kwargs)