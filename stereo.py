#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

# all the opengl stuff to swizzle and display a quilt for CubeVi C1/Cubestage.ai Companion 01
import ctypes
import numpy as np
from OpenGL import GL
from pyopengltk import OpenGLFrame


# Vertex Shader source code
VERTEX_SHADER = """
            #version 140
            in vec2 pos;
            in vec2 texCoord;
            out vec2 fragTexCoord;

            void main()
            {
                gl_Position = vec4(pos, 0.0, 1.0);
                fragTexCoord = texCoord;
            }
"""

# Fragment Shader source code
FRAGMENT_SHADER = """
            #version 140
            uniform sampler2D image1;
            uniform float _OutputSizeX;
            uniform float _OutputSizeY;
            uniform float _Slope;
            uniform float _X0;
            uniform float _Interval;
            uniform float _ImgsCountAll;
            uniform float _ImgsCountX;
            uniform float _ImgsCountY;
            uniform float _gamma;
            in vec2 fragTexCoord;
            out vec4 FragColor;

            float get_choice_float(vec2 pos, float bias) {
                float x = pos.x * _OutputSizeX + 0.5;
                float y = (1- pos.y) * _OutputSizeY + 0.5;
                // float y = pos.y * _OutputSizeY + 0.5;
                float x1 = (x + y * _Slope) * 3.0 + bias;
                float x_local = mod(x1 + _X0, _Interval);
                return (x_local / _Interval);
            }

            vec3 linear_to_srgb(vec3 linear) {
                bvec3 cutoff = lessThan(linear, vec3(0.0031308));
                vec3 higher = vec3(1.055) * pow(linear, vec3(1.0 / 2.4)) - vec3(0.055);
                vec3 lower = linear * vec3(12.92);
                return mix(higher, lower, cutoff);
            }

            vec2 get_uv_from_choice(vec2 pos, float choice_float) {
                float choice = floor(choice_float * _ImgsCountAll);
                vec2 choice_vec = vec2(
                _ImgsCountX - 1.0 - mod(choice, _ImgsCountX),  // Right to left
                // _ImgsCountY - 1.0 - floor(choice / _ImgsCountX) 
                floor(choice / _ImgsCountX) // Bottom to top
                );

                vec2 reciprocals = vec2(1.0 / _ImgsCountX, 1.0 / _ImgsCountY);
                return (choice_vec + pos) * reciprocals;
            }

            vec4 get_color(vec2 pos, float bias) {
                float choice_float = get_choice_float(pos, bias);
                vec2 sel_pos = get_uv_from_choice(pos, choice_float);
                return texture(image1, sel_pos);
            }

            void main() {
                vec4 color = get_color(fragTexCoord, 0.0);
                color.g = get_color(fragTexCoord, 1.0).g;
                color.b = get_color(fragTexCoord, 2.0).b;                
                FragColor = vec4(pow(linear_to_srgb(color.rgb), vec3(1.0/_gamma)), color.a);
            }
"""

class SwizzleFrame(OpenGLFrame):

    def initgl(self):
        self.ImgsCountX = 8.0
        self.ImgsCountY = 5.0
        self.ImgsCountAll = 40.0
        self.OutputSizeX = 1440.0
        self.OutputSizeY = 2560.0

        self.UNIFORMS = {}
        
        # Compile shaders
        self.vertex_shader = GL.glCreateShader(GL.GL_VERTEX_SHADER)
        GL.glShaderSource(self.vertex_shader, VERTEX_SHADER)
        GL.glCompileShader(self.vertex_shader)

        self.fragment_shader = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
        GL.glShaderSource(self.fragment_shader, FRAGMENT_SHADER)
        GL.glCompileShader(self.fragment_shader)

        # Create shader program and link shaders
        self.shader_program = GL.glCreateProgram()
        GL.glAttachShader(self.shader_program, self.vertex_shader)
        GL.glAttachShader(self.shader_program, self.fragment_shader)
        GL.glLinkProgram(self.shader_program)
        
        # Clean up shaders
        GL.glDeleteShader(self.vertex_shader)
        GL.glDeleteShader(self.fragment_shader)

        GL.glUseProgram(self.shader_program)

        GL.glBindAttribLocation(self.shader_program, 0, "pos")
        GL.glBindAttribLocation(self.shader_program, 1, "texCoord")

        self.UNIFORMS['OutputSizeX'] = GL.glGetUniformLocation(self.shader_program, '_OutputSizeX')
        self.UNIFORMS['OutputSizeY'] = GL.glGetUniformLocation(self.shader_program, '_OutputSizeY')
        self.UNIFORMS['Slope'] = GL.glGetUniformLocation(self.shader_program, '_Slope')
        self.UNIFORMS['X0'] = GL.glGetUniformLocation(self.shader_program, '_X0')
        self.UNIFORMS['Interval'] = GL.glGetUniformLocation(self.shader_program, '_Interval')
        self.UNIFORMS['ImgsCountAll'] = GL.glGetUniformLocation(self.shader_program, '_ImgsCountAll')
        self.UNIFORMS['ImgsCountX'] = GL.glGetUniformLocation(self.shader_program, '_ImgsCountX')
        self.UNIFORMS['ImgsCountY'] = GL.glGetUniformLocation(self.shader_program, '_ImgsCountY')
        self.UNIFORMS['image1'] = GL.glGetUniformLocation(self.shader_program, 'image1')
        self.UNIFORMS['gamma'] = GL.glGetUniformLocation(self.shader_program, '_gamma')

        # Define vertex data for a quad (two triangles)
        self.vertices = np.array([
            -1.0, -1.0, 0.0,
             1.0, -1.0, 0.0,
             1.0,  1.0, 0.0,

             1.0,  1.0, 0.0,
            -1.0,  1.0, 0.0,
            -1.0, -1.0, 0.0,
        ], dtype=np.float32)

        self.uv = np.array([
            0.0, 0.0,
            1.0, 0.0,
            1.0, 1.0,

            1.0, 1.0,
            0.0, 1.0,
            0.0, 0.0
        ], dtype=np.float32)

        # Create a Vertex Array Object (VAO) to store attribute configurations
        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)
        self.vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.vertices.nbytes+self.uv.nbytes, np.concatenate((self.vertices, self.uv), axis=0), GL.GL_STATIC_DRAW)

        # Specify the layout of the vertex data
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, ctypes.c_void_p(0))
        GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, GL.GL_FALSE, 0, ctypes.c_void_p(self.vertices.nbytes))
        GL.glEnableVertexAttribArray(0)
        GL.glEnableVertexAttribArray(1)

        # Unind VAO and VBO
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        # bind texture
        GL.glActiveTexture(GL.GL_TEXTURE0)
        self.texture_id = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

        GL.glViewport(0, 0, self.width, self.height)

        sze = GL.glGetIntegerv(GL.GL_MAX_TEXTURE_SIZE)
        print(f"Max texture size: {sze}")

    def redraw(self):
        GL.glUseProgram(self.shader_program)

        GL.glUniform1f(self.UNIFORMS['OutputSizeX'], self.OutputSizeX)
        GL.glUniform1f(self.UNIFORMS['OutputSizeY'], self.OutputSizeY)
        GL.glUniform1f(self.UNIFORMS['Slope'], self.obliquity)
        GL.glUniform1f(self.UNIFORMS['X0'], self.deviation)
        GL.glUniform1f(self.UNIFORMS['Interval'], self.linenumber)
        GL.glUniform1f(self.UNIFORMS['ImgsCountAll'], self.ImgsCountAll)
        GL.glUniform1f(self.UNIFORMS['ImgsCountX'], self.ImgsCountX)
        GL.glUniform1f(self.UNIFORMS['ImgsCountY'], self.ImgsCountY)
        # GL.glUniform1f(self.UNIFORMS['gamma'], 0.35)
        GL.glUniform1f(self.UNIFORMS['gamma'], 0.2)

        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)        
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, self.texwidth, self.texheight, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, self.image)

        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)

        GL.glBindVertexArray(0)
        GL.glUseProgram(0)

    def SetShaderParams(self, obliquity, linenumber, deviation):
        self.obliquity = obliquity
        self.linenumber = linenumber
        self.deviation = deviation

    def SetImage(self, image, width, height):    
        self.image = image
        self.texwidth = width
        self.texheight = height
        

            
        return
