import ctypes
import OpenGL.GL as GL
from OpenGL.GL import shaders

class ShaderProgram:
    VERTEX_SHADER = """
        #extension GL_ARB_explicit_attrib_location : enable
        attribute vec4 in_position;
        attribute vec2 in_tex_coord;
        varying vec2 vs_tex_coord;

        void main(void){
            gl_Position = in_position;
            vs_tex_coord = in_tex_coord;
        }"""

    FRAGMENT_SHADER = """
        uniform sampler2D tex;
        varying vec2 vs_tex_coord;

        void main(void){
            gl_FragColor = texture2D(tex, vs_tex_coord);
        }"""

    TEXTURED_VERTEX_SHADER = """#version 330 core
layout (location = 0) in vec3 in_position;
layout (location = 1) in vec2 in_tex_coord;


uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

out vec2 TexCoord;

void main()
{
    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
	TexCoord = in_tex_coord;
}
"""

    TEXTURED_FRAGMENT_SHADER = """#version 330 core
out vec4 FragColor;

in vec2 TexCoord;

// texture samplers
uniform sampler2D texture1;

void main()
{
//    FragColor = vec4(1.0,0.0,1.0,1.0);
	FragColor = texture(texture1, TexCoord);
}
"""

    DEFAULT_VERT_SHADER = """#version 330 core

layout (location = 0) in vec2 in_texcoord_0;
layout (location = 1) in vec3 in_normal;
layout (location = 2) in vec3 in_position;

out vec2 uv_0;
out vec3 normal;
out vec3 fragPos;
out vec4 shadowCoord;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_view_light;
uniform mat4 m_model;

mat4 m_shadow_bias = mat4(
    0.5, 0.0, 0.0, 0.0,
    0.0, 0.5, 0.0, 0.0,
    0.0, 0.0, 0.5, 0.0,
    0.5, 0.5, 0.5, 1.0
);

void main() {
    uv_0 = in_texcoord_0;
    fragPos = vec3(m_model * vec4(in_position, 1.0));
    normal = mat3(transpose(inverse(m_model))) * normalize(in_normal);
    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);

    mat4 shadowMVP = m_proj * m_view_light * m_model;
    shadowCoord = m_shadow_bias * shadowMVP * vec4(in_position, 1.0);
    shadowCoord.z -= 0.0005;
}
"""

    DEFAULT_FRAG_SHADER = """#version 330 core

layout (location = 0) out vec4 fragColor;

in vec2 uv_0;
in vec3 normal;
in vec3 fragPos;
in vec4 shadowCoord;

struct Light {
    vec3 position;
    vec3 Ia;
    vec3 Id;
    vec3 Is;
};

uniform Light light;
uniform sampler2D tex;
uniform vec3 camPos;
uniform sampler2DShadow shadowMap;
uniform vec2 u_resolution;


float lookup(float ox, float oy) {
    vec2 pixelOffset = 1 / u_resolution;
    return textureProj(shadowMap, shadowCoord + vec4(ox * pixelOffset.x * shadowCoord.w,
                                                     oy * pixelOffset.y * shadowCoord.w, 0.0, 0.0));
}


//float getSoftShadowX4() {
//    float shadow;
//    float swidth = 1.5;  // shadow spread
//    vec2 offset = mod(floor(gl_FragCoord.xy), 2.0) * swidth;
//    shadow += lookup(-1.5 * swidth + offset.x, 1.5 * swidth - offset.y);
//    shadow += lookup(-1.5 * swidth + offset.x, -0.5 * swidth - offset.y);
//    shadow += lookup( 0.5 * swidth + offset.x, 1.5 * swidth - offset.y);
//    shadow += lookup( 0.5 * swidth + offset.x, -0.5 * swidth - offset.y);
//    return shadow / 4.0;
//}



float getSoftShadowX16() {
    float shadow16 = 1.0;
    float swidth = 1.0;
    float endp = swidth * 1.5;
    for (float y = -endp; y <= endp; y += swidth) {
        for (float x = -endp; x <= endp; x += swidth) {
            shadow16 += lookup(x, y);
        }
    }
    return shadow16 / 16.0;
}


//float getSoftShadowX64() {
//    float shadow;
//    float swidth = 0.6;
//    float endp = swidth * 3.0 + swidth / 2.0;
//    for (float y = -endp; y <= endp; y += swidth) {
//        for (float x = -endp; x <= endp; x += swidth) {
//            shadow += lookup(x, y);
//        }
//   }
//    return shadow / 64;
//}


float getShadow() {
    float shadow = textureProj(shadowMap, shadowCoord);
    return shadow;
}


vec3 getLight(vec3 color) {
    vec3 Normal = normalize(normal);

    // ambient light
    vec3 ambient = light.Ia;

    // diffuse light
    vec3 lightDir = normalize(light.position - fragPos);
    float diff = max(0, dot(lightDir, Normal));
    vec3 diffuse = diff * light.Id;

    // specular light
    vec3 viewDir = normalize(camPos - fragPos);
    vec3 reflectDir = reflect(-lightDir, Normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0), 32);
    vec3 specular = spec * light.Is;

    // shadow
//    float shadow = getShadow();
    float shadow = getSoftShadowX16();

    return color * (ambient + (diffuse + specular) * shadow);
}


void main() {
    float gamma = 2.2;
    vec3 color = texture(tex, uv_0).rgb;
    color = pow(color, vec3(gamma));

    color = getLight(color);

    color = pow(color, 1 / vec3(gamma));
    fragColor = vec4(color, 1.0);
}
"""

    DEF2_VERT_SHADER = """#version 330 core

layout (location = 0) in vec2 in_texcoord_0;
layout (location = 1) in vec3 in_normal;
layout (location = 2) in vec3 in_position;

out vec2 uv_0;
out vec3 normal;
out vec3 fragPos;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

void main() {
    uv_0 = in_texcoord_0;
    fragPos = vec3(m_model * vec4(in_position, 1.0));
    normal = mat3(transpose(inverse(m_model))) * normalize(in_normal);
    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
}
"""

    DEF2_FRAG_SHADER = """#version 330 core

layout (location = 0) out vec4 fragColor;

in vec2 uv_0;
in vec3 normal;
in vec3 fragPos;  

struct Light {
    vec3 position;
    vec3 Ia;
    vec3 Id;
    vec3 Is;
};

uniform Light light;
uniform sampler2D tex;
uniform vec3 objectColor;
uniform vec3 camPos;

void main()
{
    vec3 Normal = normalize(normal);

    // ambient light
    vec3 ambient = light.Ia;

    // diffuse light
    vec3 lightDir = normalize(light.position - fragPos);
    float diff = max(0, dot(lightDir, Normal));
    vec3 diffuse = diff * light.Id;

    // specular light
    vec3 viewDir = normalize(camPos - fragPos);
    vec3 reflectDir = reflect(-lightDir, Normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0), 32);
    vec3 specular = spec * light.Is;
	vec3 color = texture(tex, uv_0).rgb;
    vec3 result = (ambient + diffuse + specular) * color;
    fragColor = vec4(result, 1.0);
} 
"""

    HUDvertStr = '''#version 330 core 
layout (location = 0) in vec3 in_position;
layout (location = 1) in vec2 in_tex_coord;

out vec2 uv_0;

void main() {
    uv_0 = in_tex_coord;
    gl_Position = vec4(in_position.x,in_position.y,0.1, 1.0);
}'''

    HUDfragStr = '''#version 330 core
layout (location = 0) out vec4 fragColor;
in vec2 uv_0;
uniform sampler2D texture1;

void main() {
    fragColor = texture(texture1, uv_0);
}'''


    Def3vertStr = """#version 330 core
    layout (location = 0) in vec3 in_position;
    layout (location = 1) in vec2 in_tex_coord;

    out vec2 uv_0;
    
    uniform mat4 m_proj;
    uniform mat4 m_view;
    uniform mat4 m_model;
    
    void main()
    {
       uv_0 = in_tex_coord;
       gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
    }"""
    
    Def3fragStr = """#version 330 core
    out vec4 FragColor;

    in vec2 uv_0;
    uniform sampler2D texture1;

    uniform int useTexture;
    uniform vec4 color;
        
    void main()
    {
       if (useTexture == 0) {
        FragColor = texture(texture1, uv_0);
       } else {
        FragColor = color;
       }
    }"""
    
    Def4vertStr = """#version 330 core
    layout (location = 0) in vec3 in_position;

    uniform mat4 m_proj;
    uniform mat4 m_view;
    uniform mat4 m_model;
    
    void main()
    {
       gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
    }"""
    
    Def4fragStr = """#version 330 core
    out vec4 FragColor;

    uniform sampler2D texture1;

    uniform int useTexture;
    uniform vec4 color;
        
    void main()
    {
       if (useTexture == 0) {
        FragColor = color;
       } else {
        FragColor = color;
       }
    }"""


    programs = {}
    uniforms = {}
    attributes = {}
    _instance = None
 
    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def inst(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            # Put any initialization here.
        return cls._instance

    def defaultValue(self):
        self.addShaderProgramFrom('def2',self.DEFAULT_VERT_SHADER,self.DEF2_FRAG_SHADER)
        self.addShaderProgramFrom('def3',self.Def3vertStr,self.Def3fragStr)
        self.addShaderProgramFrom('def4',self.Def4vertStr,self.Def4fragStr)
        self.addShaderProgramFrom('test',self.VERTEX_SHADER,self.FRAGMENT_SHADER)
        self.addShaderProgramFrom('test2',self.TEXTURED_VERTEX_SHADER,self.TEXTURED_FRAGMENT_SHADER)
        self.addShaderProgramFrom('HUD',self.HUDvertStr,self.HUDfragStr)

    def UseProgram(self,progNo):
        shaders.glUseProgram(progNo)

    def addAttributAndUniform(self,shaderProgName):
        program = ShaderProgram.programs[shaderProgName]
        count = GL.glGetProgramiv(program, GL.GL_ACTIVE_ATTRIBUTES)
        if count > 0:
            ShaderProgram.attributes[shaderProgName] = []
            bufsize = 128
            buf = (GL.GLchar * 128)()
            namesize = GL.GLsizei()
            size = GL.GLint()
            kind = GL.GLenum()
            for i in range(count):
                GL.glGetActiveAttrib(program, i, bufsize, namesize, size, kind, buf)
                name = buf.value.decode('utf-8')
                ShaderProgram.attributes[shaderProgName].append(name)
#        print(ShaderProgram.attributes[shaderProgName])

        count = GL.glGetProgramiv(program, GL.GL_ACTIVE_UNIFORMS)
        ShaderProgram.uniforms[shaderProgName] = {}
        if count > 0:
            for i in range(count):
                name, size, kind = GL.glGetActiveUniform(program, i)
                name = name.decode('utf-8')
                idx = GL.glGetUniformLocation(program, name)
                ShaderProgram.uniforms[shaderProgName][name] = idx
#        print(ShaderProgram.uniforms[shaderProgName])
                
                

    def _get_program(self, shader_program_name):
        with open(f'shaders/{shader_program_name}.vert') as file:
            vertex_shader = file.read()

        with open(f'shaders/{shader_program_name}.frag') as file:
            fragment_shader = file.read()

        vs = shaders.compileShader(vertex_shader, GL.GL_VERTEX_SHADER)
        fs = shaders.compileShader(fragment_shader, GL.GL_FRAGMENT_SHADER)
        ShaderProgram.programs[shader_program_name] = shaders.compileProgram(vs, fs)

    def destroy(self):
        [program.release() for program in ShaderProgram.programs.values()]

    def addShaderProgram(self,filename):
        self._get_program(filename)
        self.addAttributAndUniform(filename)
        
    def addShaderProgramFrom(self,shaderProgName,vertString,fragString):
        vs = shaders.compileShader(vertString, GL.GL_VERTEX_SHADER)
        fs = shaders.compileShader(fragString, GL.GL_FRAGMENT_SHADER)
        ShaderProgram.programs[shaderProgName] = shaders.compileProgram(vs, fs)
        self.addAttributAndUniform(shaderProgName)