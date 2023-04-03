import moderngl as mgl
import glm
from PIL import Image




class TextureList:
    textures = {}
    def __init__(self, app):
        self.app = app

    def addTexture(self,name,filename,ext='png',cube = False,alpha = False):
        if cube:
            TextureList.textures[name] = self.get_texture_cube(dir_path=filename, ext=ext)
        else:
            TextureList.textures[name] = self.get_texture(path=filename,alpha=alpha)
    
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
            texture = self.ctx.texture(im_flipped.size, 3, im_flipped.tobytes(), alignment=4)
            textures.append(texture)

        size = textures[0].size
        texture_cube = self.ctx.texture_cube(size=size, components=3, data=None)

        for i in range(6):
            texture_data = textures[i].read()
            texture_cube.write(face=i, data=texture_data)

        return texture_cube

    def get_texture(self, path, alpha = False):
        texture = self.loadTexture(path,alpha)
        texture[filter] = {GL_TEXTURE_WRAP_S, GL_REPEAT}
        texture[filter] = (GL_TEXTURE_WRAP_T, GL_REPEAT)
        texture[filter] = (GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        texture[filter] = (GL_TEXTURE_MIN_FILTER, GL_NEAREST)
#        texture.build_mipmaps()
        # AF
        texture.anisotropy = 32.0
        return texture

    def loadTexture(self, path, alpha = False):
        img = Image.open(path)
        if alpha:
            convert = img.convert("RGBA")
            im_flipped = img.transpose(method=Image.Transpose.FLIP_TOP_BOTTOM
            ID = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, ID)
            glPixelStorei(GL_UNPACK_ALIGNMENT,1)
            glTexImage2D(GL_TEXTURE_2D, 0, 3, im_flipped.size[0], im_flipped.size[1], 0,GL_RGBA, GL_UNSIGNED_BYTE, image)
        else:
            convert = img.convert("RGB")
            im_flipped = img.transpose(method=Image.Transpose.FLIP_TOP_BOTTOM)
            ID = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, ID)
            glPixelStorei(GL_UNPACK_ALIGNMENT,1)
            glTexImage2D(GL_TEXTURE_2D, 0, 3, im_flipped.size[0], im_flipped.size[1], 0,GL_RGBA, GL_UNSIGNED_BYTE, image)
        return {textureID = ID}


    def destroy(self):
        [tex.release() for tex in TextureList.textures.values()]