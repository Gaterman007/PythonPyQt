import glm
from PIL import Image,ImageDraw
from OpenGL.GL import *

class HUDTexture():
    def __init__(self,oglWin):
        self.oglWin = oglWin
        self.width = 2048
        self.height = 2048
        self.init_textureHUD()

    def getID(self):
        return self.HUDID
        
    def init_textureHUD(self):
        self.img = Image.new('RGBA',(self.width,self.height))
        self.overlayimg = Image.new('RGBA',(self.width,self.height))
        self.HUDID = glGenTextures(1)
        self.overlayimg = Image.open('textures\\HUD.png')
        self.overlayimg.convert('RGBA')
        self.overlayimg = self.overlayimg.resize((self.width,self.height))
        self.img.paste(self.overlayimg)

    def resize(self,width, height):
        self.width = width
        self.height = height
        self.img = self.img.resize((self.width, self.height))
        self.overlayimg = self.overlayimg.resize((self.width, self.height))
        self.textureHUD()

    def clear(self):
        draw = ImageDraw.Draw(self.img)
        draw.rectangle([(0, 0), (self.width, self.height)], fill=(0,0,0,0))
        self.img.paste(self.overlayimg)
        self.textureHUD()

    def drawLine(self,start,end):
        draw = ImageDraw.Draw(self.img)
        draw.line((start,end), fill=(255,255,255,255),width=1)
        self.textureHUD()

    def drawCircle(self,xPos,yPos,size,color = (255,0,0,255),outline=(255,255,255,255), width=1):
        draw = ImageDraw.Draw(self.img)
        halfsize = size/2
        draw.ellipse([xPos-halfsize,yPos- halfsize,xPos+halfsize,yPos+halfsize], fill=color,outline=outline, width=width)
        self.textureHUD()


    def drawRectangle(self,start,end):
        draw = ImageDraw.Draw(self.img)
        point1 = start
        point2 = start[0],end[1]
        point3 = end
        point4 = end[0],start[1]
        draw.line((point1,point2), fill=(255,255,255,255),width=1)
        draw.line((point2,point3), fill=(255,255,255,255),width=1)
        draw.line((point3,point4), fill=(255,255,255,255),width=1)
        draw.line((point4,point1), fill=(255,255,255,255),width=1)
        self.textureHUD()


    def textureHUD(self):
        self.oglWin.makeCurrent()
        imdata = self.img.convert("RGBA").transpose(Image.FLIP_TOP_BOTTOM ).tobytes()
        glBindTexture(GL_TEXTURE_2D, self.HUDID)
        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, self.img.size[0], self.img.size[1], 0,GL_RGBA, GL_UNSIGNED_BYTE, imdata)
#        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
#        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
#        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)
        self.oglWin.doneCurrent()


class Textures(dict):

    _instance = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def inst(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            super().__init__({})
        return cls._instance

    def addTexture(self,name,filename,ext='png',cube = False,alpha = False):
        if cube:
            self.__setitem__(name,self.get_texture_cube(dir_path=filename, ext=ext))
        else:
            self.__setitem__(name,self.get_texture(path=filename,alpha=alpha))
    
    def get_texture_cube(self, dir_path, ext='png'):
        faces = ['right', 'left', 'top', 'bottom'] + ['front', 'back'][::-1]
        textures = []
        for face in faces:
            img = Image.open(dir_path + f'{face}.{ext}')
            convert = img.convert("RGB")
            if face in ['right', 'left', 'front', 'back']:
                im_flipped = convert.transpose(method=Image.Transpose.FLIP_LEFT_RIGHT)
            else:
                im_flipped = convert.transpose(method=Image.Transpose.FLIP_TOP_BOTTOM)

#            texture = self.ctx.texture(im_flipped.size, 3, im_flipped.tobytes(), alignment=4)
#            textures.append(texture)

#        size = textures[0].size
#        texture_cube = self.ctx.texture_cube(size=size, components=3, data=None)

#        for i in range(6):
#            texture_data = textures[i].read()
#            texture_cube.write(face=i, data=texture_data)

        return texture_cube

    def get_texture(self, path, alpha = False):
        texture = self._loadTexture(path,alpha)
        return texture

    def _loadTexture(self, path, alpha = False):
        img = Image.open(path)
        if alpha:
            image = img.transpose(Image.FLIP_TOP_BOTTOM).convert("RGBA")
            width, height = image.size
            image_data = image.tobytes()
            ID = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, ID)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
            glGenerateMipmap(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, 0)
        
        else:
            image = img.transpose(Image.FLIP_TOP_BOTTOM).convert("RGB")
            width, height = image.size
            image_data = image.tobytes()
            ID = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, ID)
#            glPixelStorei(GL_UNPACK_ALIGNMENT,1)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB8, img.size[0], img.size[1], 0,GL_RGB, GL_UNSIGNED_BYTE, image_data)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
            glGenerateMipmap(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, 0)
        return ID


    def destroy(self):
        [GL.glDeleteTextures(tex) for tex in self.values()]