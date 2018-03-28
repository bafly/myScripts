"""Extend/cut/move edges to specific plane"""

import pymel.core as pm

# P, N
# v, n
# d
# d = ((N - P) * n) / v * n
lssl = pm.selected(fl=1)
A1 = lssl[0].getPoint(0)
A2 = lssl[0].getPoint(1)
B1 = lssl[1].getPoint(0)
B2 = lssl[1].getPoint(1)
vecA = A2 - A1
vecB = B2 - B1
jA = pm.joint(p=vecA.normal())
jB = pm.joint(p=vecB.normal())

dotR = vecA.dot(vecB)
vecC = B1 - A1
dotS = vecA.dot(vecC)
dotT = vecB.dot(vecC)

# t = dotT / dotR
vecN = (vecC - (vecB * dotT)).normal()
t = (vecC * vecN) / (vecA.normal() * vecN)
#vecN.length()
#vecA.normal().length()
P = A1 + (vecA * t)
#pm.joint(p=vecA * t)

jA1 = pm.joint(p=A1, n="A1")
jA2 = pm.joint(p=A2, n="A2")
jB1 = pm.joint(p=B1, n="B1")
jB2 = pm.joint(p=B2, n="B2")
jC = pm.joint(p=P, n="C")
pm.joint(p=vecA, n="vecA")
pm.joint(p=vecB, n="vecB")
pm.joint(p=vecN, n="vecN")
pm.joint(p=vecC, n="vecC")
pm.joint(p=vecA * t, n="vecA_new")

jN = pm.joint(p=vecN, n="n")

dot = vecB.normal().dot(vecA.normalize())

# check if on one line(stackoverflow.com)
denomZ = vecA.x * vecB.y - vecB.x * vecA.y
denomX = vecA.y * vecB.z - vecB.y * vecA.z
if not (denomZ and denomX):
    print "Looks like given segments are colinear"
    return

dir(vecB)