from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Shader, Texture, FrameBufferProperties, WindowProperties

#folder z deafultowymi modelami
#import panda3d
#print(panda3d.__file__)

class App(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        #środowisko - tło
        self.scene = self.loader.loadModel("models/environment") #wgranie wbudowanego modelu
        self.scene.reparentTo(self.render) #przypisanie do wezla render
        self.scene.setScale(0.25, 0.25, 0.25) #skalowanie
        self.scene.setPos(-8, 42, 0) #ustawianie w przestrzeni

        #obiekt refrakcyjny
        #models/misc/sphere - nie działa tylko kolor??, models/box - działa
        self.refractive_object = self.loader.loadModel("models/panda") #wgranie wbudowanego modelu 
        self.refractive_object.reparentTo(self.render) #przypisanie do wezla render
        self.refractive_object.setScale(2) #powiekszenie obiektu 
        self.refractive_object.setPos(0, 10, 3) #ustawenie w przestrzeni

        #renderowanie geometrii i głębi do tekstury
        fb_props = FrameBufferProperties() #tworzymy bufor klatki
        fb_props.setRgbColor(True) #bufor przechowuje informacje na temat koloru klatki RGB
        fb_props.setDepthBits(1) #ilość bitów na przechowanie informacji na temat głębokości 
        win_props = WindowProperties.size(512, 512)  #rozdzielczość tekstury 
        #bufor wyjsciowy
        self.buffer = self.graphicsEngine.makeOutput(
            self.pipe, "offscreen buffer", -2, fb_props, win_props,
            GraphicsPipe.BFRefuseWindow, self.win.getGsg(), self.win)

        self.color_texture = Texture() #tekstura przechowująca kolor
        self.depth_texture = Texture() #tekstura przechowująca głębie
        #dodanie tekstur do bufora
        self.buffer.addRenderTexture(self.color_texture, GraphicsOutput.RTMCopyRam)
        self.buffer.addRenderTexture(self.depth_texture, GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPDepth)

        #kopia sceny do hidden_scene
        self.hidden_scene = NodePath("Hidden Scene")
        self.scene.instanceTo(self.hidden_scene)

        #kamera do hidden_scene
        self.buffer_cam = self.makeCamera(self.buffer, scene=self.hidden_scene)
        self.buffer_cam.reparentTo(self.cam)

        self.refractive_index = 1.5  #TODO: przyjąć input od usera
        #Załadowanie shaderów
        self.refractive_object.setShader(Shader.load(Shader.SLGLSL, vertex="shaders/refraction.vert", fragment="shaders/refraction.frag"))
        self.refractive_object.setShaderInput("color_texture", self.color_texture)
        self.refractive_object.setShaderInput("depth_texture", self.depth_texture)
        self.refractive_object.setShaderInput("camera_nearfar", Vec2(self.camLens.getNear(), self.camLens.getFar()))#odległość kamery od najbliższego obiektu i najdalszego obiektu 
        self.refractive_object.setShaderInput("refractive_index", self.refractive_index)


#uruchomienie głównej pętli        
app = App()
app.run()
