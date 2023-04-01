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
        # dot of ray direction
        a = (self.rayDirection.x * self.rayDirection.x) + (self.rayDirection.y * self.rayDirection.y) + (self.rayDirection.z * self.rayDirection.z)
        b = 2*(self.rayDirection.x*(self.startPoint.x-SphereOrigine.x) + self.rayDirection.y*(self.startPoint.y-SphereOrigine.y) + self.rayDirection.z*(self.startPoint.z-SphereOrigine.z))

        xx = self.startPoint.x - SphereOrigine.x
        yy = self.startPoint.y - SphereOrigine.y
        zz = self.startPoint.z - SphereOrigine.z
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

    def IntersectPlan(self):
        pass


    def __repr__(self):
        return f'Ray(\'{self.startPoint}\', {self.rayDirection})'
