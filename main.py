import os
import tkinter as tk
from tkinter import simpledialog

from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from panda3d.core import FrameBufferProperties, Shader, Texture, WindowProperties


class App(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        root = tk.Tk()
        root.withdraw()

        while True:
            model_name = simpledialog.askstring(
                "Input", "Enter model name (e.g., ball.bam):"
            )
            if model_name is None:
                print("No model specified. Using default 'ball.bam'.")
                model_name = "ball.bam"
                break
            if not model_name:
                print("No model specified. Using default 'ball.bam'.")
                model_name = "ball.bam"
                break

            model_path = os.path.join("my-models", model_name)
            if os.path.exists(model_path):
                break
            else:
                print(f"Model '{model_name}' not found in 'my-models'.")

        while True:
            try:
                refractive_index_str = simpledialog.askstring(
                    "Input", "Enter refractive index:", initialvalue="1.5"
                )
                if refractive_index_str is None:
                    self.refractive_index = 1.5
                    print("Using default refractive index: 1.5")
                    break
                self.refractive_index = float(refractive_index_str)
                if self.refractive_index <= 0:
                    raise ValueError("Refractive index must be positive.")
                break
            except ValueError as e:
                print(f"Invalid input: {e}")
            except TypeError:
                self.refractive_index = 1.5
                print("Using default refractive index: 1.5")
                break

        # Background
        self.scene = self.loader.loadModel("models/environment")
        self.scene.reparentTo(self.render)
        self.scene.setScale(1, 1, 1)
        self.scene.setPos(-8, 42, 0)

        # Refraction
        self.refractive_object = self.loader.loadModel(
            os.path.join("my-models", model_name)
        )
        self.refractive_object.reparentTo(self.render)
        # self.refractive_object.setScale(1) # dragon
        # self.refractive_object.setPos(0, -82, 3)
        # self.refractive_object.setScale(40)  # ball
        # self.refractive_object.setPos(0, -82, 20)
        # self.refractive_object.setScale(40)  # ship
        # self.refractive_object.setPos(0, -102, 20)

        # Buffer for Depth and Color
        fb_props = FrameBufferProperties()
        fb_props.setRgbColor(True)
        fb_props.setDepthBits(1)
        win_props = WindowProperties.size(512, 512)

        # Buffer main scene
        self.buffer = self.graphicsEngine.makeOutput(
            self.pipe,
            "offscreen buffer",
            -2,
            fb_props,
            win_props,
            GraphicsPipe.BFRefuseWindow,
            self.win.getGsg(),
            self.win,
        )

        self.color_texture = Texture()
        self.depth_texture = Texture()
        self.buffer.addRenderTexture(self.color_texture, GraphicsOutput.RTMCopyRam)
        self.buffer.addRenderTexture(
            self.depth_texture, GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPDepth
        )

        # Near geometry buffer
        self.near_geometry_buffer = self.graphicsEngine.makeOutput(
            self.pipe,
            "near geometry buffer",
            -2,
            fb_props,
            win_props,
            GraphicsPipe.BFRefuseWindow,
            self.win.getGsg(),
            self.win,
        )

        self.near_geometry_color_texture = Texture()
        self.near_geometry_depth_texture = Texture()
        self.near_geometry_buffer.addRenderTexture(
            self.near_geometry_color_texture, GraphicsOutput.RTMCopyRam
        )
        self.near_geometry_buffer.addRenderTexture(
            self.near_geometry_depth_texture,
            GraphicsOutput.RTMBindOrCopy,
            GraphicsOutput.RTPDepth,
        )

        # Camera for hidden scene (depth rendering)
        self.hidden_scene = NodePath("Hidden Scene")
        self.scene.instanceTo(self.hidden_scene)
        self.buffer_cam = self.makeCamera(self.buffer, scene=self.hidden_scene)
        self.buffer_cam.reparentTo(self.cam)

        # Camera for near geometry
        self.near_geometry_scene = NodePath("Near Geometry Scene")
        self.scene.instanceTo(self.near_geometry_scene)
        self.buffer_cam_near_geom = self.makeCamera(
            self.near_geometry_buffer, scene=self.near_geometry_scene
        )

        # Shaders
        self.refractive_object.setShader(
            Shader.load(
                Shader.SLGLSL,
                vertex="shaders/refraction.vert",
                fragment="shaders/refraction.frag",
            )
        )
        self.refractive_object.setShaderInput("color_texture", self.color_texture)
        self.refractive_object.setShaderInput("depth_texture", self.depth_texture)
        self.refractive_object.setShaderInput(
            "near_geometry_color", self.near_geometry_color_texture
        )
        self.refractive_object.setShaderInput(
            "near_geometry_depth", self.near_geometry_depth_texture
        )
        self.refractive_object.setShaderInput(
            "camera_nearfar", Vec2(self.camLens.getNear(), self.camLens.getFar())
        )
        self.refractive_object.setShaderInput("refractive_index", self.refractive_index)


app = App()
app.run()
