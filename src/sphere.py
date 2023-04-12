from OpenGL.GL import *
from shader_program import ShaderProgram
import numpy as np
import glm
import math

class Sphere:
    # sphere radius , longitude division Count, latittude division Count
    def __init__(self,radius,sectorCount = 18,stackCount = 18):
        self.radius = radius
        self.vertices = []
        self.normals = []
        self.texCoords = []
        self.sphereVAO = None
        self.sphereVBO = None
        self.sphereEBO = None
        self.sphereDrawRender = False
        self.program = None
        self.wireframe = True
        self.isMVP = True
        self.m_proj = glm.mat4()
        self.m_view = glm.mat4()
        self.m_model = glm.mat4()
        self.m_projID = None
        self.m_viewID = None
        self.m_modelID = None
        
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
        self.createSphereVAO()

    def getVertices(self):
        return np.hstack([self.vertices,self.texCoords])

    def createSphereVAO(self):
        if self.sphereVAO is None:
            self.sphereVAO = glGenVertexArrays(1)
        glBindVertexArray(self.sphereVAO)
        if self.sphereVBO is None:
            self.sphereVBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.sphereVBO)

        verticesList = np.array(self.getVertices(),dtype = np.float32).flatten()
        # size of float = 4
        glBufferData(GL_ARRAY_BUFFER, len(verticesList) * 4, verticesList, GL_STATIC_DRAW)
        stride = 20   # (x,y,z,u,v) (5)float * (4)size of float
        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, None) # size 3  X,Y,Z
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12)) # size 2  U,V   start = size of X,Y,Z  3 * 4


        indicesList = np.array(self.indices,dtype = np.uint32).flatten()
        if self.sphereEBO is None:
            self.sphereEBO = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.sphereEBO)
        # size of int = 4
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indicesList) * 4, indicesList, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        self.sphereDrawRender = True

    def paintGL(self):
        if self.sphereDrawRender:
            if self.program is not None:
                ShaderProgram.inst().UseProgram(self.program)
                glBindVertexArray(self.sphereVAO)

                if self.wireframe:
                    glPolygonMode( GL_FRONT_AND_BACK, GL_LINE )
                if self.isMVP:
                    glUniformMatrix4fv(self.m_projID, 1, GL_FALSE, glm.value_ptr(self.m_proj))
                    glUniformMatrix4fv(self.m_viewID, 1, GL_FALSE, glm.value_ptr(self.m_view))
                    glUniformMatrix4fv(self.m_modelID, 1, GL_FALSE, glm.value_ptr(self.m_model))
                glPointSize(5.0)   
                glDrawElements(GL_TRIANGLES, len(self.indices)*3, GL_UNSIGNED_INT, ctypes.c_void_p(0))
                if self.wireframe:
                    glPolygonMode( GL_FRONT_AND_BACK, GL_FILL )
                glBindVertexArray(0)
                ShaderProgram.inst().UseProgram(0)
