from enum import Enum
import glm
import numpy as np
import math

class Ray():
    def __init__(self,startPoint = glm.vec3(0.0,0.0,0.0),rayDirection = glm.vec3(0.0,0.0,1.0)):
        self.startPoint = startPoint
        self.rayDirection = rayDirection
        self.t = 1

    def pointFromRay(self):
        return self.startPoint + (self.rayDirection * self.t)

    def intersectionSphere(self,SphereOrigine,SphereRayon):
        intersection_distance = 0
        dist_to_sphere = self.startPoint - SphereOrigine
        b = glm.dot(self.rayDirection, dist_to_sphere)
        c = glm.dot(dist_to_sphere, dist_to_sphere) - SphereRayon * SphereRayon
        b_squared_minus_c = b * b - c

        # check for "imaginary" answer. == ray completely misses sphere
        if b_squared_minus_c < 0.0:
            return False,0
        # check for ray hitting twice (in and out of the sphere)
        if b_squared_minus_c > 0.0:
            # get the 2 intersection distances along ray
            t_a = -b + math.sqrt(b_squared_minus_c)
            t_b = -b - math.sqrt(b_squared_minus_c)
            intersection_distance = t_b
            # if behind viewer, throw one or both away
            if t_a < 0.0:
                if t_b < 0.0:
                    return False,0
            else:
                if t_b < 0.0:
                    intersection_distance = t_a
            return True,intersection_distance
        # check for ray hitting once (skimming the surface)
        if 0.0 == b_squared_minus_c:
            # if behind viewer, throw away
            t = -b + math.sqrt(b_squared_minus_c)
            if t < 0.0:
                return False,0
            intersection_distance = t
            return True,intersection_distance
        # note: could also check if ray origin is inside sphere radius
        return False,0

    def intersectionSphere2(self,SphereOrigine,SphereRayon):

        # dot of ray direction
        a = (self.rayDirection.x * self.rayDirection.x) + (self.rayDirection.y * self.rayDirection.y) + (self.rayDirection.z * self.rayDirection.z)

        xx = self.startPoint.x - SphereOrigine.x
        yy = self.startPoint.y - SphereOrigine.y
        zz = self.startPoint.z - SphereOrigine.z

        b = 2*(self.rayDirection.x*(xx) + self.rayDirection.y*(yy) + self.rayDirection.z*(zz))


        c = xx*xx + yy*yy + zz*zz - SphereRayon*SphereRayon

        discriminant = b*b - 4*a*c

        if(discriminant <= 0):
            return False,0

        _t = (-b - math.sqrt(discriminant))/(2*a)
        if(_t <= 0):
            _t = (-b + math.sqrt(discriminant))/(2*a)
            if(_t <= 0):
                return False,0
        return True,_t

    def IntersectPlan(self,plane):
        n_dot_d = glm.dot(plane.normal,self.rayDirection)
        if glm.abs(n_dot_d) < 0.0001:
            return False,0.0
        n_dot_ps = glm.dot(plane.normal,plane.pointOnPlane - self.startPoint)
        self.t = n_dot_ps / n_dot_d
        planePoint = self.startPoint + self.t * self.rayDirection
        return True,planePoint

    def IntersectTriangle(self,triPoint_A,triPoint_B,triPoint_C):
        triPoint_BA = (triPoint_B - triPoint_A).xyz
        triPoint_CA = (triPoint_C - triPoint_A).xyz
        normalTriangle = glm.cross(triPoint_BA,triPoint_CA)
#        plane = Plane(triPoint_A,normalTriangle)
        n_dot_d = glm.dot(normalTriangle,self.rayDirection)
        if glm.abs(n_dot_d) < 0.0001:
            return False
        n_dot_ps = glm.dot(normalTriangle,triPoint_A.xyz - self.startPoint)
        self.t = n_dot_ps / n_dot_d
#        planePoint = self.startPoint + self.t * self.rayDirection
        planePoint = self.pointFromRay()
        AtoB_Edge = triPoint_B.xyz - triPoint_A.xyz
        BtoC_Edge = triPoint_C.xyz - triPoint_B.xyz
        CtoA_Edge = triPoint_A.xyz - triPoint_C.xyz
        AtoPoint = planePoint - triPoint_A.xyz
        BtoPoint = planePoint - triPoint_B.xyz
        CtoPoint = planePoint - triPoint_C.xyz
        ATestVec = glm.cross(AtoB_Edge,AtoPoint)
        BTestVec = glm.cross(BtoC_Edge,BtoPoint)
        CTestVec = glm.cross(CtoA_Edge,CtoPoint)
        AtestVecMatchNormal = glm.dot(ATestVec,normalTriangle) > 0.0
        BtestVecMatchNormal = glm.dot(BTestVec,normalTriangle) > 0.0
        CtestVecMatchNormal = glm.dot(CTestVec,normalTriangle) > 0.0
        hitTriangle = AtestVecMatchNormal and BtestVecMatchNormal and CtestVecMatchNormal
        return hitTriangle

    def RayLineIntersect(point3,point4):
        point1 = self.startPoint + (self.rayDirection * 0.01)
        point2 = self.startPoint + (self.rayDirection * 500)
        point13 = point1 - point3
        point43 = point4 - point3
        Epsilon = 0.0000001
        if math.abs(point43.x) < Epsilon and math.abs(point43.y) < Epsilon and math.abs(point43.z) < Epsilon:
            return False
        point21 = point2 - point1
        if math.abs(point21.x) < Epsilon and math.abs(point21.y) < Epsilon and math.abs(point21.z) < Epsilon:
            return False
        dot1343 = glm.dot(point13,point43)
        dot4321 = glm.dot(point43,point21)
        dot1321 = glm.dot(point13,point21)
        dot4343 = glm.dot(point43,point43)
        dot2121 = glm.dot(point21,point21)
        denom = dot2121 * dot4343 - dot4321 * dot4321
        if math.abs(denom) < Epsilon:
            return False,0,0,0,0
        numer = dot1343 * dot4321 - dot1321 * dot4343
        mua = numer / denom
        mub = (dot1343 + dot4321 * mua) / dot4343
        pa.x = point1.x + mua * point21.x;
        pa.y = point1.y + mua * point21.y;
        pa.z = point1.z + mua * point21.z;
        pb.x = point3.x + mub * point43.x;
        pb.y = point3.y + mub * point43.y;
        pb.z = point3.z + mub * point43.z;
        return True,mua,mub,pa,pb

    def __repr__(self):
        return f'Ray(\'{self.startPoint}\', {self.rayDirection})'
