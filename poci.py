# v0.0

####################### closest point on curve ########################
import pymel.core as pm
from pymel.core import datatypes as dt

def doIt(connect=None):
    poci = None
    if not connect:
        poci = pm.createNode("pointOnCurveInfo", ss=1)
    lssl = pm.selected()
    objects, data = get_closest_u(lssl, poci=poci)
    for obj in objects:
        pos_at_u(obj,
                 data[obj]["crv"], data[obj]["u"],
                 poci=poci, connect=connect)
    if poci:
        pm.delete(poci)

def get_closest_u(lssl=None,
                  range_min=None, range_max=None,
                  poci=None):
    """Select 
    """
    # pm.timer(e=1, n="tmpr_poci")
    pm.timer(s=1, n="tmr_poci")
    if lssl:
        lssl = pm.ls(lssl, tr=1)
    else:
        lssl = pm.ls(sl=1, tr=1)
    if not lssl:
        return
    ls_crv = [x for x in lssl if x.getShape().type() == "nurbsCurve"]
    if not ls_crv:
        print "<!> NURBSCurve not found"
        return
    lssl.remove(ls_crv[0])
    if not lssl:
        print "<!> Add any transform to selection"
        return
    # sel = lssl[0]
    # create info nodedata = {}
    delpoci = False
    if not poci:
        poci = pm.createNode("pointOnCurveInfo", ss=1)
        delpoci = True
    else:
        poci = pm.PyNode(poci)
    poci.top.set(1)
    ls_crv[0].ws >> poci.ic
    eps = 0.01
    data = {}
    objects = []
    # print lssl
    # print "A"
    # per object: loop can be add here
    for sel in lssl:
        # print sel
        closest_u = 0.0
        objects.append(str(sel))
        pos = dt.Vector(pm.xform(sel, q=1, ws=1, rp=1))
        range_min, range_max = find_range(ls_crv[0], pos, poci)
        # print "range_min :", range_min, "range_max :", range_max
        if not (range_min and range_max):
            if range_min is None:
                closest_u = range_max
            if range_max is None:
                closest_u = range_min
        else:
                
            i = 0
            cur_u = range_min
            # init values
            poci.pr.set(cur_u)
            u_pos = poci.position.get()
            tang = poci.nt.get()
            vec = u_pos-pos
            # pm.move("joint2", vec, os=1)
            dist = vec.length()
            dot = vec.normal().dot(tang)
            init_dir = -1 if dot < 0 else 1
            while i<300:
                # print "min: ", range_min
                # print "max: ", range_max
                dif = range_max - range_min
                cur_u = range_min + dif/2
                # print i, cur_u, dot
                poci.pr.set(cur_u)
                u_pos = poci.position.get()
                tang = poci.nt.get()
                cur_vec = u_pos - pos
                # pm.move("joint2", cur_vec, os=1)
                cur_dist = cur_vec.length()
                cur_dot = cur_vec.normal().dot(tang)
                # print "dot: ", cur_dot
                if cur_dist < dist:
                    if cur_dot*init_dir < 0.0:
                        range_max = cur_u
                    else:
                        range_min = cur_u
                        dist = cur_dist
                        dot = cur_dot
                else:
                    range_max = cur_u     # if 0.5 is far than 0.0
                    # range_min = cur_u   

                if abs(cur_dot) < eps:
                    closest_u = cur_u
                    print "<i> Found closest point, at: ", i
                    break
                i+=1
        data[str(sel)] = {"u":closest_u, "crv":str(ls_crv[0])}
    # delete info node
    if delpoci:
        pm.delete(poci)
    print "Time:", pm.timer(e=1, n="tmr_poci")
    return objects, data

#crv = ls_crv[0]
#find_range(ls_crv[0], pos, poci)
def find_range(crv, pos, poci=None):
    """divide path by eps*mult and find closest segment
    
        Returns, tuple - first - start range, second - end
            if start is None - Position is closer to end
            if end is None - Object is closer to start
    """
    # pm.timer(s=1)
    detail_mult = 4
    div = len(crv.ep) * detail_mult
    
    rng_min = 0.0
    rng_max = 1.0
    step = (rng_max - rng_min) / div
    
    # create and connect measure tool
    delpoci = False
    ls_poci = pm.ls(poci)
    if ls_poci:
        poci = ls_poci[0]
    else:
        poci = pm.createNode("pointOnCurveInfo", ss=1)
        delpoci = True
    crv.ws >> poci.ic
    poci.top.set(1)
    
    # base params
    dist = prev_dist = None     # most closest value
    distA = distB = None
    rngA = rng_min
    rngB = None
    closest_u = prev_u = None
    # i += 1
    for i in range(div+1):
        cur_u = i * step
        poci.pr.set(cur_u)
        cur_dot, cur_dist = get_dot(pos, poci.p.get(),
                                    poci.nt.get())
        if not dist:
            dist = cur_dist
            dot = cur_dot
            closest_u = cur_u
        else:
            
            if (cur_dot * dot) > 0.0:
                if cur_dist < dist:
                    rng_min = cur_u
            else:
                if prev_dist <= dist:
                    rng_max = cur_u
            if cur_dist < dist:
                dist = cur_dist
                closest_u = cur_u
        dot = cur_dot
        prev_u = cur_u
        prev_dist = cur_dist
        ## debug
    
    if rng_min > rng_max:
        rng_max = rng_min
        rng_min = None
    else:
        if closest_u == rng_min:
            rng_max = None
    if delpoci:
        pm.delete(poci)
    return rng_min, rng_max

def pos_at_u(sel, curve, u, poci=None, connect=None):
    
    delete = False
    sel = pm.PyNode(sel)
    curve = pm.PyNode(curve)
    if poci:
        poci = pm.PyNode(poci)
    else:
        poci = pm.createNode("pointOnCurveInfo", ss=1)
        delete = True
    poci.top.set(1)
    curve.ws >> poci.ic
    poci.pr.set(u)
    u_pos = poci.position.get()
    pm.xform(sel, ws=1, t=u_pos)
    if connect:
        poci.p >> sel.t
    else:
        if delete:
            pm.delete(poci)
    return u_pos
#get_dot(sel.getTranslation(ws=1), poci.p.get(), poci.nt.get())
def get_dot(pos, upos, utang):
    """returns dot of vector from given position to
        curve's u position with its tangent
    """
    vec = (dt.Vector(pos) - dt.Vector(upos))
    dot = dt.Vector(utang).dot(vec.normal())
    dist = vec.length()
    return dot, dist

if __name__ == "__main__":
    doIt()
#######################################################################