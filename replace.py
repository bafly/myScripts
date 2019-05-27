import pymel.core as pm

def repshp(*args, **kwargs):
    print "args:", args
    inmesh = False if not kwargs.has_key("inmesh") else kwargs["inmesh"]
    rename = True if not kwargs.has_key("rename") else kwargs["rename"]
    lssl = None
    if not args:
        lssl = pm.selected()
    else:
        lssl = pm.ls(*args)
    print " Selection:", lssl
    if len(lssl)%2:
        print " <!> Given objects are not even, select by pairs",
        return
    pairs = [(lssl[x], lssl[x+1]) for x in range(0, len(lssl)-1, 2)]
    for pair in pairs:
        src, trg = pair
        if rename:
            trg.rename(src.name(stripNamespace=1))
        src_shps = src.getShapes(ni=1)
        trg_shps = trg.getShapes(ni=1)
        tshps_sz = len(trg_shps)
        if inmesh:
            inm = ".ws"
            outm = "cr"
            if src_shp.type() == "mesh":
                inm = "i"
                outm = "o"
        else:
            pm.delete(trg_shps)
        for s, src_shp in enumerate(src_shps):
            if s == tshps_sz:
                break
            if inmesh:
                trg_shp = trg_shps[s]
                if not (src_shp.attr(outm).isConnectedTo(trg_shp.attr(inm))):
                    pm.evalDeferred(
                        pm.Callback(src_shp.attr(outm).connect, trg_shp.attr(inm)),
                        en=1
                        )
                pm.evalDeferred(
                    pm.Callback(src_shp.attr(outm).disconnect, trg_shp.attr(inm)),
                    low=1
                    )
            else:
                dup = pm.duplicate(src_shp, addShape=1)
                dup[0].setParent(trg, r=1, s=1)