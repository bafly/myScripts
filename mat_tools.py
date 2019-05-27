def inv_mat(m):
    
    m_i = m[:]
    # extract scale x
    m_x = pm.datatypes.Vector(m[0:3])
    sx = m_x.length()   # scale x
    m_x_n = m_x.normal()
    # extract scale y
    m_y = pm.datatypes.Vector(m[4:7])
    sy = m_y.length()   # scale y
    m_y_n = m_y.normal()
    # extract scale z
    m_z = pm.datatypes.Vector(m[8:11])
    sz = m_z.length()   # scale z
    m_z_n = m_z.normal()
    
    m_i[0], m_i[1], m_i[2] = m_x_n[0], m_y_n[0], m_z_n[0]
    m_i[4], m_i[5], m_i[6] = m_x_n[1], m_y_n[1], m_z_n[1]
    m_i[8], m_i[9], m_i[10] = m_x_n[2], m_y_n[2], m_z_n[2]
    
    return m_i
    
def mir_mat(m, plane=None, axis=None,
               translate=None, rotate=None):
    mir_m = m[:]
    # plane yz
    plane = 0 if plane is None else plane
    # axis x
    axis = 0 if axis is None else axis
    
    # transform by arguments
    translate = 1 if translate is None else translate
    rotate = 1 if rotate is None else rotate
    
    for i, v in enumerate(m):
        col = i%4
        if col == plane:
            print i
            if i >= 12:
                if not translate:
                    continue
                print " Translating: ", col
            else:
                if not rotate:
                    continue
                print " Rotating: ", col
            mir_m[i] *= -1
    
    # mirror matrix
    if not axis:
        mir_m[0] = mir_m[5]*mir_m[10] - mir_m[6]*mir_m[9]
        mir_m[1] = mir_m[6]*mir_m[8] - mir_m[4]*mir_m[10]
        mir_m[2] = mir_m[4]*mir_m[9] - mir_m[5]*mir_m[8]
    else:
        # y
        if axis == 1:
            mir_m[4] = mir_m[2]*mir_m[9] - mir_m[10]*mir_m[1]
            mir_m[5] = mir_m[10]*mir_m[0] - mir_m[8]*mir_m[2]
            mir_m[6] = mir_m[1]*mir_m[8] - mir_m[9]*mir_m[0]
        else:
            # z
            if axis == 2:
                mir_m[8] = mir_m[1]*mir_m[6] - mir_m[2]*mir_m[5]
                mir_m[9] = mir_m[2]*mir_m[4] - mir_m[0]*mir_m[6]
                mir_m[10] = mir_m[0]*mir_m[5] - mir_m[1]*mir_m[4]
    return mir_m