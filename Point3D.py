from dataclasses import dataclass
import glm
import numpy as np

@dataclass
class Point3D:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    u: float = 0.0
    v: float = 0.0

    def __repr__(self):
        str = F"{self.x},{self.y},{self.z},{self.u},{self.v}"
        return str;
        
    def array(self):
        return [self.x,self.y,self.z,self.u,self.v]


class Segment:
    def __init__(self, *args,**kwargs):
        if len(args) == 2:
            if type(args[0]) == Point3D:
                self.start = args[0]
            else:
                self.start = Point3D()
            if type(args[1]) == Point3D:
                self.end = args[1]
            else:
                self.end = Point3D()
        else:
            self.start = kwargs.get('start',Point3D())
            self.end = kwargs.get('end',Point3D())

    def __repr__(self):
        str = F"start = {self.start},end = {self.end}"
        return str;

    def array(self):
        return [start.array(),end.array()]

class Triangle:
    def __init__(self, *args,**kwargs):
        if len(args) > 0:
            if type(args[0]) == Point3D:
                self.p1 = args[0]
            else:
                self.p1 = Point3D()
            if type(args[1]) == Point3D:
                self.p2 = args[1]
            else:
                self.p2 = Point3D()
            if type(args[2]) == Point3D:
                self.p3 = args[2]
            else:
                self.p3 = Point3D()
            if len(args) > 3:
                if type(args[3]) == type(glm.vec2(0.0,0.0)):
                    self.p1uv = args[3]
                else:
                    self.p1uv = glm.vec2(0.0,0.0)
                if type(args[4]) == type(glm.vec2(0.0,0.0)):
                    self.p2uv = args[4]
                else:
                    self.p2uv = glm.vec2(0.0,0.0)
                if type(args[5]) == type(glm.vec2(0.0,0.0)):
                    self.p3uv = args[5]
                else:
                    self.p3uv = glm.vec2(0.0,0.0)
        else:
            self.p1 = kwargs.get('p1',Point3D())
            self.p2 = kwargs.get('p2',Point3D())
            self.p3 = kwargs.get('p3',Point3D())
            self.p1uv = kwargs.get('uv1',glm.vec2(0.0,0.0))
            self.p2uv = kwargs.get('uv2',glm.vec2(0.0,0.0))
            self.p3uv = kwargs.get('uv3',glm.vec2(0.0,0.0))

    def __repr__(self):
        str = F"p1 = {self.p1},p2 = {self.p2},p3 = {self.p3}"
        return str;

    def array(self):
        return [p1.array(),p2.array(),p3.array()]
