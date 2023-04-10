from OpenGL.GL import *
from shader_program import ShaderProgram
from Point3D import *
from Ray import *
import numpy as np
import glm
import sys

class BaseModel:
    nextModelID = 0
    modelList = []
    newmodelList = {}
    updateListCallback = None
    selectedModel = None
    updateSelectionCallback = None
    
    def __init__(self, *args,**kwargs):
        self.baseInit()
        self.m_proj = glm.mat4()
        self.m_view = glm.mat4()
        self.pointColor = glm.vec4(1.0, 1.0, 1.0, 1.0)
        self.segmentColor = glm.vec4(1.0, 1.0, 1.0, 1.0)
        self.faceColor = glm.vec4(1.0, 1.0, 1.0, 1.0)

        self.maxDiag = 0.0
        self.maxXDiag = 0.0
        self.maxYDiag = 0.0
        self.maxZDiag = 0.0
        self.centerInWorld = glm.vec4(0.0,0.0,0.0,1.0)
        self.minmaxextent = []
        self.pointCloud = []
        self.pointWorld = []
        self.pointIndices = []
        self.pointSize = 1.0
        self.isOnModel = False
        self.hitDistance = 0.0
        
        self.progName = kwargs.get('progName',None)
        self.program = ShaderProgram.programs[self.progName]
        self.uniforms = ShaderProgram.uniforms[self.progName]
        self.attributes = ShaderProgram.attributes[self.progName]
        self.initAttribLocation()
        if 'm_proj' in self.uniforms and 'm_view' in self.uniforms and 'm_model' in self.uniforms:
            self.isMVP = True
        else:
            self.isMVP = False

        self.parentModel = kwargs.get('parent',None)

        self.pos = kwargs.get('pos',(0, 0, 0))
        self.rot = glm.vec3([glm.radians(a) for a in kwargs.get('rot',(0, 0, 0))])
        self.scale = kwargs.get('scale',(1, 1, 1))

        self.TextureID = kwargs.get('TextureID',None)
        self.blend = kwargs.get('Blend',False)
        self.renderMode = kwargs.get('mode',GL_TRIANGLES)
        self.wireframe = kwargs.get('wireframe',False)
        self.visible = kwargs.get('visible',True)
        self.internal = kwargs.get('internal',False)
        self.update_model_matrix()
        self.modelName = ""
        self.setModelName(kwargs.get('Name',"model_%d" % self.modelID))

    def baseInit(self):
        self.modelID = BaseModel.nextModelID
        BaseModel.nextModelID += 1

    def setModelName(self,name):
        if name != self.modelName:
            # find self  remove from list
            if self.modelName in BaseModel.newmodelList:
                my_dict.pop(self.modelName, None)
            if name in BaseModel.newmodelList:
                # new name already in list so add model id
                self.modelName = "%s(%d)" % (name,self.modelID)
            else:
                self.modelName = "%s" % name
            BaseModel.newmodelList[self.modelName] = self

#        # find if name exist in list
#        foundName = None
#        for idx in range(len(BaseModel.modelList)):
#            if BaseModel.modelList[idx][1] == name:
#                foundName = BaseModel.modelList[idx]
#        # find if self exist in list
#
#        foundSelf = None
#        foundIndex = -1
#        for idx in range(len(BaseModel.modelList)):
#            if BaseModel.modelList[idx][2] == self:
#                foundSelf = BaseModel.modelList[idx]
#                foundIndex = idx
#
#        if foundSelf is None:
#            if foundName is None:
#                BaseModel.modelList.append((self.modelID,name,self))
#            else:
#                self.modelName = "%s(%d)" % (name,self.modelID)
#                BaseModel.modelList.append((self.modelID,self.modelName,self))
#        else:
#            if foundName is None:
#                self.modelName = "%s" % name
#                foundSelf = (foundSelf[0],name,foundSelf[2])
#                BaseModel.modelList[foundIndex] = (foundSelf[0],name,foundSelf[2])
#            else:
#                if foundName != foundSelf: 
#                    self.modelName = "%s(%d)" % (name,self.modelID)
#                    BaseModel.modelList[foundIndex] = (foundSelf[0],self.modelName,foundSelf[2])
#                    foundSelf = (foundSelf[0],self.modelName,foundSelf[2])

        if BaseModel.updateListCallback is not None:
            BaseModel.updateListCallback()

    @classmethod
    def updateListCB(self, updateListCB):
        BaseModel.updateListCallback = updateListCB

    @classmethod
    def updateSelectionCB(self,updateSelectionCB):
        BaseModel.updateSelectionCallback = updateSelectionCB
        
    @classmethod
    def setSelectedModel(self,model):
        self.selectedModel = model
        if BaseModel.updateSelectionCallback is not None:
            BaseModel.updateSelectionCallback(model)

    @classmethod
    def getSelectedModel(self):
        return self.selectedModel
        
    def initAttribLocation(self):
        if self.program is not None:
            if 'in_position' in self.attributes:
                self.position = glGetAttribLocation(self.program, 'in_position')
            if 'in_tex_coord' in self.attributes:
                self.tex_coord = glGetAttribLocation(self.program, 'in_tex_coord')
            # get texture uniform location
            if 'texture1' in self.uniforms:
                self.tex_uloc = glGetUniformLocation(self.program, "texture1")
            if 'tex' in self.uniforms:
                self.tex_uloc = glGetUniformLocation(self.program, "tex")
            glBlendEquation(GL_FUNC_ADD)
    
    def paintGL(self):
        pass

    def update_model_matrix(self):
        self.m_model = glm.mat4()
        # translate
        self.m_model = glm.translate(self.m_model, self.pos)
        # rotate
        self.m_model = glm.rotate(self.m_model, self.rot.z, glm.vec3(0, 0, 1))
        self.m_model = glm.rotate(self.m_model, self.rot.y, glm.vec3(0, 1, 0))
        self.m_model = glm.rotate(self.m_model, self.rot.x, glm.vec3(1, 0, 0))
        # scale
        self.m_model = glm.scale(self.m_model, self.scale)
        self.fixDiagonalandCenter(self.m_model)
        self.updateWorldCoord()

    def updateWorldCoord(self):
        self.pointWorld.clear()
        for point in self.pointCloud:
            self.pointWorld.append(self.m_model * glm.vec4(point.x,point.y,point.z,1.0))


    def updateBBox(self,point):
        if len(self.minmaxextent) < 1:
            self.minmaxextent = [point.x,point.y,point.z,point.x,point.y,point.z]
        else:
            if self.minmaxextent[0] > point.x:
                self.minmaxextent[0] = point.x
            if self.minmaxextent[1] > point.y:
                self.minmaxextent[1] = point.y
            if self.minmaxextent[2] > point.z:
                self.minmaxextent[2] = point.z
            if self.minmaxextent[3] < point.x:
                self.minmaxextent[3] = point.x
            if self.minmaxextent[4] < point.y:
                self.minmaxextent[4] = point.y
            if self.minmaxextent[5] < point.z:
                self.minmaxextent[5] = point.z
        self.update_model_matrix()

    def fixDiagonalandCenter(self,newMatrix):
        if len(self.minmaxextent) > 1:
            self.maxXDiag = math.fabs(self.minmaxextent[3] - self.minmaxextent[0])
            self.maxDiag = self.maxXDiag
            self.maxYDiag = math.fabs(self.minmaxextent[4] - self.minmaxextent[1])
            if self.maxDiag < self.maxYDiag:
                self.maxDiag = self.maxYDiag
            self.maxZDiag = math.fabs(self.minmaxextent[5] - self.minmaxextent[2])
            if self.maxDiag < self.maxZDiag:
                self.maxDiag = self.maxZDiag
            self.centerInWorld.x = self.minmaxextent[0] + (self.maxXDiag / 2)
            self.centerInWorld.y = self.minmaxextent[1] + (self.maxYDiag / 2)
            self.centerInWorld.z = self.minmaxextent[2] + (self.maxZDiag / 2)
            self.centerInWorld = newMatrix*self.centerInWorld

    def HitTest(self,ray,triangleTest = False):
        self.isOnModel, self.hitDistance = ray.intersectionSphere(self.centerInWorld,self.maxDiag)
        return self.isOnModel, self.hitDistance, False , False

    def setPosition(self,pos):
        self.pos = pos
        self.update_model_matrix()

    def getPosition(self,pos):
        return self.pos

    def setRotation(self,rotation):
        self.rot = glm.vec3([glm.radians(a) for a in rotation])
        self.update_model_matrix()

    def getRotation(self):
        return glm.vec3([round(glm.degrees(a),6) for a in self.rot])

    def setScale(self,scale):
        self.scale = scale
        self.update_model_matrix()

    def getScale(self):
        return self.scale

    def _setRotate(self,rotate):
        self.rot = rotate
        self.update_model_matrix()

    def setWireFrame(self,wireframe):
        self.wireframe = wireframe

    def getWireFrame(self):
        return self.wireframe
        
    def update(self,camera):
        # mvp
        if 'm_proj' in self.uniforms:
            self.m_proj = camera.get_projection()
        if 'm_view' in self.uniforms:
            self.m_view = camera.get_view()

    def addPoint3D(self,point3D): # Point3D
        if type(point3D) == type([]):
            self.pointCloud.extend(point3D) # add many points
            x = 0
            while x < len(point3D):
                self.updateBBox(point3D[x])
                x = x + 1
        else:
            self.pointCloud.append(point3D) # add one point
            self.updateBBox(point3D)


class ModelDef2(BaseModel):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        self.drawRender = False
        self.VAO = None
        self.VBO = None
        self.EBO = None
        self.renderLenght = 0
        self.renders = []
        self.isOnATriangle = False

    def createVAO(self):
        if self.VAO is None:
            self.VAO = glGenVertexArrays(1)
        glBindVertexArray(self.VAO)
        if self.VBO is None:
            self.VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        verticesList = np.array([x.array() for x in self.pointCloud],dtype = np.float32).flatten()
        # size of float = 4
        glBufferData(GL_ARRAY_BUFFER, len(verticesList) * 4, verticesList, GL_STATIC_DRAW)

        stride = 20   # (x,y,z,u,v) (5)float * (4)size of float

        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, None) # size 3  X,Y,Z
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12)) # size 2  U,V   start = size of X,Y,Z  3 * 4



        indicesList = np.array(self.pointIndices,dtype = np.uint32)
        if self.EBO is None:
            self.EBO = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        # size of int = 4
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indicesList) * 4, indicesList, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        self.drawRender = True

    def addPoint3D(self,point3D): # Point3D
        super().addPoint3D(point3D)
        self.createVAO()


    # GL_POINTS
    #       Points       x                                              1 Vertex x Point
    # GL_LINES,GL_LINE_STRIP,GL_LINE_LOOP                   
    #       Lines        2x   0,1 1,2...  0,1 1,2... x,0                2 Vertex x Line
    # GL_TRIANGLES,GL_TRIANGLE_FAN,GL_TRIANGLE_STRIP        
    #       Triangles    3x   0,1,2 0,2,3 ...  0,1,2 1,2,3(2,1,3) ...   3 Vertex x Triangle

    def HitTest(self,ray,triangleTest = False):
        self.isOnModel, self.hitDistance = ray.intersectionSphere(self.centerInWorld,self.maxDiag)
        self.isOnATriangle = False
        isOnVertex = False
        if triangleTest and self.isOnModel:
            for vertex in self.pointWorld:
                test1,test2 = ray.intersectionSphere(vertex,0.03)
                if test1:
                    isOnVertex = True
            self.isOnATriangle = False
            for render in self.renders:
                if render[0] == GL_TRIANGLES:
                    # test chaque Triangle  ray.IntersectTriangle(p1,p2,p3)
                    numberOfTriangle = int(render[1]/3)
                    startAt = int(render[2]/4)
                    for x in range(startAt,startAt+numberOfTriangle):
                        if ray.IntersectTriangle(self.pointWorld[self.pointIndices[x]],self.pointWorld[self.pointIndices[x+1]],self.pointWorld[self.pointIndices[x+2]]):
                            self.isOnATriangle = True
        return self.isOnModel, self.hitDistance,self.isOnATriangle,isOnVertex

    def addIndices(self,indices): # Point3D
        if type(indices) == type([]):
            self.pointIndices.extend(indices) # add many points
        else:
            self.pointIndices.append(indices) # add one point
        self.createVAO()

    def addRender(self,modes,size,start,color):
        self.renders.append((modes,size,start,color))

    def paintGL(self):
#        self._paintGL((self.renderMode,self.renderLenght,0))
        
        for render in self.renders:
            self._paintGL(render)

    def _paintGL(self,render):
        if self.drawRender:
            if self.visible:
                if self.program is not None:
                    ShaderProgram.inst().UseProgram(self.program)
                    glBindVertexArray(self.VAO)
                    if self.TextureID is not None:
#                        print(self.modelName, " texture ID = ",self.TextureID)
                        glEnable(GL_TEXTURE_2D)
                        glActiveTexture(GL_TEXTURE0)
                        glBindTexture(GL_TEXTURE_2D, self.TextureID)
                        if 'useTexture' in self.uniforms:
                            glUniform1i(self.uniforms['useTexture'], 1)
                        if 'texture1' in self.uniforms:
                            glUniform1i(glGetUniformLocation(self.program, "texture1"), 0)
                        if self.blend:
                            glEnable(GL_BLEND)

                    if self.wireframe:
                        glPolygonMode( GL_FRONT_AND_BACK, GL_LINE )
                    if self.isMVP:
                        glUniformMatrix4fv(self.uniforms['m_proj'], 1, GL_FALSE, glm.value_ptr(self.m_proj))
                        glUniformMatrix4fv(self.uniforms['m_view'], 1, GL_FALSE, glm.value_ptr(self.m_view))
                        glUniformMatrix4fv(self.uniforms['m_model'], 1, GL_FALSE, glm.value_ptr(self.m_model))
                        
                    if 'color' in self.uniforms:
                        glUniform4f(self.uniforms['color'], render[3][0], render[3][1], render[3][2], render[3][3])
                    if self.pointSize > 1.0:
                        glPointSize(self.pointSize)
                    glDrawElements(render[0], render[1], GL_UNSIGNED_INT, ctypes.c_void_p(render[2]))
                    if self.pointSize > 1.0:
                        glPointSize(1.0)
                    if self.wireframe:
                        glPolygonMode( GL_FRONT_AND_BACK, GL_FILL )
                    glBindVertexArray(0)
                    if self.TextureID is not None:
                        glBindTexture(GL_TEXTURE_2D, 0)
                        glDisable(GL_TEXTURE_2D)
                    if self.blend:
                        glDisable(GL_BLEND)
                    ShaderProgram.inst().UseProgram(0)


class ModelDefault(BaseModel):
    def __init__(self,*args,**kwargs):

        self.segments = []
        self.triangles = []
        self.drawPoints = False
        self.drawLines = False
        self.drawTrangles = False

        self.VAOPoints = None
        self.VBOPoints = None
        self.EBOPoints = None

        self.VAOSegments = None
        self.VBOSegments = None
        self.EBOSegments = None

        self.VAOTriangles = None
        self.VBOTriangles = None
        self.EBOTriangles = None
        # minx,miny,minz,maxx,maxy,maxz
        self.minmaxextent = []
        self.isOnVertex = False
        super().__init__(*args,**kwargs)
        
    def createPointBuffer(self):
        if len(self.pointCloud) > 0:
            if self.VAOPoints is None:
                self.VAOPoints = glGenVertexArrays(1)
                self.VBOPoints = glGenBuffers(1)
                self.EBOPoints = glGenBuffers(1)
            glBindVertexArray(self.VAOPoints)
            glBindBuffer(GL_ARRAY_BUFFER, self.VBOPoints)

    #        pointVertices = np.array([],dtype = 'f4')
            pointVertices = []
            for i in self.pointCloud:
                pointVertices.append(i.x)
                pointVertices.append(i.y)
                pointVertices.append(i.z)
                pointVertices.append(0.0)
                pointVertices.append(0.0)
            pointVertices = np.array(pointVertices,dtype = np.float32)
            # create buffer for vertices
            sizeOfvertices = len(pointVertices) * 4  # size of float = 4
            glBufferData(GL_ARRAY_BUFFER, sizeOfvertices, pointVertices, GL_STATIC_DRAW)
            
            pointIndices = np.array(range(len(self.pointCloud)),dtype = np.uint32)
            # create buffer for index1
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBOPoints)
            sizeOfpointIndices = len(pointIndices) * 4  # size of int = 4
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeOfpointIndices, pointIndices, GL_STATIC_DRAW)
            glEnableVertexAttribArray(0)
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * 4, None) # stride = 5(x,y,z,u,v) * size of float = 4
            glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * 4, 3 * 4) # stride = 5(x,y,z,u,v) * size of float = 4
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindVertexArray(0)
            self.drawPoints = True
        else:
            self.drawPoints = False
            
    def addPoint3D(self,point3D): # Point3D
        super().addPoint3D(point3D)
        self.createPointBuffer()

    def removePoint3D(self,point3D): # Point3D
        self.pointCloud.remove(point3D)
        self.createPointBuffer()

    def popPoint3D(self,listNo): # Point3D
        self.pointCloud.pop(listNo)
        self.createPointBuffer()
        
    def printPoints(self):
        print(self.pointCloud)


    def createSegmentBuffer(self):
        if len(self.segments) > 0:

            pointVertices = []
            pointIndices = []
            x = 0
            for i in self.segments:
                pointVertices.append(i.start.x)
                pointVertices.append(i.start.y)
                pointVertices.append(i.start.z)
                pointVertices.append(0.0)
                pointVertices.append(0.0)
                pointVertices.append(i.end.x)
                pointVertices.append(i.end.y)
                pointVertices.append(i.end.z)
                pointVertices.append(0.0)
                pointVertices.append(0.0)
                pointIndices.append(x)
                pointIndices.append(x+1)
                x = x + 2
            pointVertices = np.array(pointVertices,dtype = np.float32) 

            pointIndices = np.array(pointIndices,dtype = np.uint32)

            if self.VAOSegments is None:
                self.VAOSegments = glGenVertexArrays(1)
            glBindVertexArray(self.VAOSegments)
            if self.VBOSegments is None:
                self.VBOSegments = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, self.VBOSegments)
            # create buffer for vertices
            # size of float = 4
            glBufferData(GL_ARRAY_BUFFER, len(pointVertices) * 4, pointVertices, GL_STATIC_DRAW)
            glEnableVertexAttribArray(0)
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * 4, None) # stride = 5(x,y,z,u,v) * size of float = 4
            glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * 4, 3 * 4) # stride = 5(x,y,z,u,v) * size of float = 4

            # create buffer for indexes
            if self.EBOSegments is None:
                self.EBOSegments = glGenBuffers(1)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBOSegments)
            # size of int = 4
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(pointIndices) * 4, pointIndices, GL_STATIC_DRAW)
            glBindVertexArray(0)
            glBindBuffer(GL_ARRAY_BUFFER, 0)



            self.drawLines = True
        else:
            self.drawLines = False

    def addSegment(self,segment3D): # Segment
        if type(segment3D) == type([]):
            self.segments.extend(segment3D) # add many segment
            x = 0
            while x < len(segment3D):
                self.updateBBox(segment3D[x].start)
                self.updateBBox(segment3D[x].end)
                x = x + 1
        else:
            self.segments.append(segment3D) # add one segment
            self.updateBBox(segment3D.start)
            self.updateBBox(segment3D.end)
        self.createSegmentBuffer()

    def printSegment(self):
        print(self.segments)
            
    def createTriangleBuffer(self):
        if len(self.triangles) > 0:
            
    #        pointVertices = np.array([],dtype = 'f4') 
            pointVertices = []
            pointIndices = []
            x = 0
            for i in self.triangles:
                pointVertices.append(i.p1.x)
                pointVertices.append(i.p1.y)
                pointVertices.append(i.p1.z)
                pointVertices.append(i.p1uv[0])
                pointVertices.append(i.p1uv[1])
                
                pointVertices.append(i.p2.x)
                pointVertices.append(i.p2.y)
                pointVertices.append(i.p2.z)
                pointVertices.append(i.p2uv[0])
                pointVertices.append(i.p2uv[1])
                
                pointVertices.append(i.p3.x)
                pointVertices.append(i.p3.y)
                pointVertices.append(i.p3.z)
                pointVertices.append(i.p3uv[0])
                pointVertices.append(i.p3uv[1])
                
                pointIndices.append(x)
                pointIndices.append(x+1)
                pointIndices.append(x+2)
                x = x + 3
            pointVertices = np.array(pointVertices,dtype = np.float32) 
            pointIndices = np.array(pointIndices,dtype = np.uint32)

            if self.VAOTriangles is None:
                self.VAOTriangles = glGenVertexArrays(1)
            glBindVertexArray(self.VAOTriangles)
            if self.VBOTriangles is None:
                self.VBOTriangles = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, self.VBOTriangles)
            # create buffer for vertices
            # size of float = 4
            glBufferData(GL_ARRAY_BUFFER, len(pointVertices) * 4 , pointVertices, GL_STATIC_DRAW)


            if self.EBOTriangles is None:
                self.EBOTriangles = glGenBuffers(1)
            # create buffer for index1 
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBOTriangles)
            # size of int = 4
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(pointIndices) * 4 , pointIndices, GL_STATIC_DRAW)
            glEnableVertexAttribArray(0)
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * 4, None) # stride = 5(x,y,z,u,v) * size of float = 4
            glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * 4, 3 * 4) # stride = 5(x,y,z,u,v) * size of float = 4
            glBindVertexArray(0)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            self.drawTrangles = True
        else:
            self.drawTrangles = False

    def addTriangle(self,triangle3D): # Triangle
        if type(triangle3D) == type([]):
            self.triangles.extend(triangle3D) # add many Triangle
            x = 0
            while x < len(triangle3D):
                self.updateBBox(triangle3D[x].p1)
                self.updateBBox(triangle3D[x].p2)
                self.updateBBox(triangle3D[x].p3)
                x = x + 1
        else:
            self.triangles.append(triangle3D) # add one Triangle
            self.updateBBox(triangle3D.p1)
            self.updateBBox(triangle3D.p2)
            self.updateBBox(triangle3D.p3)
        self.createTriangleBuffer()
        self.fixDiagonalandCenter(self.m_model)
#        print(self.minmaxextent)

    def updateWorldCoord(self):
        self.pointWorld.clear()
        for i in self.triangles:
            self.pointWorld.append(self.m_model * glm.vec4(i.p1.x,i.p1.y,i.p1.z,1.0))
            self.pointWorld.append(self.m_model * glm.vec4(i.p2.x,i.p2.y,i.p2.z,1.0))
            self.pointWorld.append(self.m_model * glm.vec4(i.p3.x,i.p3.y,i.p3.z,1.0))
        
    def printTriangle(self):
        print(self.triangles)
    
    def HitTest(self,ray,triangleTest = False):
        self.isOnModel, self.hitDistance = ray.intersectionSphere(self.centerInWorld,self.maxDiag)
        self.isOnATriangle = False
        self.isOnVertex = False
        if triangleTest and self.isOnModel:
            for i in range(len(self.triangles)):
                if ray.IntersectTriangle(self.pointWorld[(i*3)],self.pointWorld[(i*3)+1],self.pointWorld[(i*3)+2]):
                    self.isOnATriangle = True
        return self.isOnModel, self.hitDistance,self.isOnATriangle,self.isOnVertex
        
    def paintGL(self):
        if self.visible:
            if self.program is not None:
                if self.drawPoints:
                    self._paintGLPoints()
                if self.drawLines:
                    self._paintGLSegments()
                if self.drawTrangles:
                    self._paintGLTriangles()
                    
    def _paintGLPoints(self):
        ShaderProgram.inst().UseProgram(self.program)
        if self.isMVP:
            glUniformMatrix4fv(self.uniforms['m_proj'], 1, GL_FALSE, glm.value_ptr(self.m_proj))
            glUniformMatrix4fv(self.uniforms['m_view'], 1, GL_FALSE, glm.value_ptr(self.m_view))
            glUniformMatrix4fv(self.uniforms['m_model'], 1, GL_FALSE, glm.value_ptr(self.m_model))
        if 'useTexture' in self.uniforms:
            glUniform1i(self.uniforms['useTexture'], 1)
        if 'color' in self.uniforms:
            glUniform4f(self.uniforms['color'], self.pointColor[0], self.pointColor[1], self.pointColor[2], self.pointColor[3])
        glBindVertexArray(self.VAOPoints)
        glPointSize(self.pointSize)
        glDrawElements(GL_POINTS, len(self.pointCloud), GL_UNSIGNED_INT, ctypes.c_void_p(0))
        glPointSize(1.0)
        glBindVertexArray(0)
        ShaderProgram.inst().UseProgram(0)

    def _paintGLSegments(self):
        ShaderProgram.inst().UseProgram(self.program)
        glBindVertexArray(self.VAOSegments)
        if self.isMVP:
            glUniformMatrix4fv(self.uniforms['m_proj'], 1, GL_FALSE, glm.value_ptr(self.m_proj))
            glUniformMatrix4fv(self.uniforms['m_view'], 1, GL_FALSE, glm.value_ptr(self.m_view))
            glUniformMatrix4fv(self.uniforms['m_model'], 1, GL_FALSE, glm.value_ptr(self.m_model))
        if 'useTexture' in self.uniforms:
            glUniform1i(self.uniforms['useTexture'], 1)
        if 'color' in self.uniforms:
            glUniform4f(self.uniforms['color'], self.segmentColor[0], self.segmentColor[1], self.segmentColor[2], self.segmentColor[3])
        glDrawElements(GL_LINES, len(self.segments) * 2, GL_UNSIGNED_INT, ctypes.c_void_p(0))
        glBindVertexArray(0)
        ShaderProgram.inst().UseProgram(0)

    def _paintGLTriangles(self):
        ShaderProgram.inst().UseProgram(self.program)
        glBindVertexArray(self.VAOTriangles)
        if self.isMVP:
            glUniformMatrix4fv(self.uniforms['m_proj'], 1, GL_FALSE, glm.value_ptr(self.m_proj))
            glUniformMatrix4fv(self.uniforms['m_view'], 1, GL_FALSE, glm.value_ptr(self.m_view))
            glUniformMatrix4fv(self.uniforms['m_model'], 1, GL_FALSE, glm.value_ptr(self.m_model))
        if 'useTexture' in self.uniforms:
            glUniform1i(self.uniforms['useTexture'], 1)
        if 'color' in self.uniforms:
            glUniform4f(self.uniforms['color'], self.faceColor[0], self.faceColor[1], self.faceColor[2], self.faceColor[3])
        glDrawElements(GL_TRIANGLES, len(self.triangles) * 3, GL_UNSIGNED_INT, ctypes.c_void_p(0))
        glBindVertexArray(0)
        ShaderProgram.inst().UseProgram(0)
