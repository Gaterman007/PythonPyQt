import numpy as np
import math

class Sphere:
    # sphere radius , longitude division Count, latittude division Count
    def __init__(self,radius,sectorCount = 18,stackCount = 18):
        self.vertices = []
        self.normals = []
        self.texCoords = []
        
        lengthInv = 1.0 / radius
        sectorStep = 2 * math.pi / sectorCount # longitude division Count
        stackStep = math.pi / stackCount       # latittude division Count

        for i in range(0,stackCount + 1):
            stackAngle = math.pi / 2.0 - i * stackStep       # starting from pi/2 to -pi/2
            xz = radius * math.cos(stackAngle)           # r * cos(u)
            y = radius * math.sin(stackAngle)            # r * sin(u)
            
            # add (sectorCount+1) vertices per stack
            # the first and last vertices have same position and normal, but different tex coords

            for j in range(0,sectorCount + 1):
                sectorAngle = j * sectorStep    # starting from 0 to 2pi
                x = xz * math.cos(sectorAngle)   # r * cos(u) * cos(v)
                z = xz * math.sin(sectorAngle)      # r * cos(u) * sin(v)
                x = round(x,5)
                y = round(y,5)
                z = round(-z,5)
                self.vertices.append((x,y,z))
                # normalized vertex normal (nx, ny, nz)
                nx = x * lengthInv;
                ny = y * lengthInv;
                nz = z * lengthInv;
                self.normals.append((nx,ny,nz))
                # vertex tex coord (s, t) range between [0, 1]
                s = j / sectorCount
                t = i / stackCount
                self.texCoords.append((s,t))
        vertex_data = np.array(self.vertices, dtype='f4')

# generate CCW index list of sphere triangles
# k1--k1+1
# |  / |
# | /  |
# k2--k2+1
        self.indices = []
        self.lineIndices = []
        for i in range(0,stackCount):
            k1 = i * (sectorCount + 1)          # beginning of current stack
            k2 = k1 + sectorCount + 1          # beginning of next stack
            for j in range(0,sectorCount):
                # 2 triangles per sector excluding first and last stacks
                # k1 => k2 => k1+1
                if i != 0:
                    self.indices.append((k1,k2,k1 + 1))
                # k1+1 => k2 => k2+1
                if i != (stackCount-1):
                    self.indices.append((k1 + 1,k2,k2 + 1))
                self.lineIndices.append((k1,k2))
                if i != 0:  # horizontal lines except 1st stack, k1 => k+1
                    self.lineIndices.append((k1,k1 + 1))
                k1 = k1 + 1
                k2 = k2 + 1

