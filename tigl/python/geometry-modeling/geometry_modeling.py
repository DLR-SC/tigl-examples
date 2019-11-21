from ipywidgets import FloatSlider, HBox, VBox, Button, Accordion
import tigl3
from OCC.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeEdge
import numpy as np

import tigl3.curve_factories
import tigl3.surface_factories

class SurfaceModelingDemo(object):

    def __init__(self):
        # list of points on NACA2412 profile
        px = [1.000084, 0.975825, 0.905287, 0.795069, 0.655665, 0.500588, 0.34468, 0.203313, 0.091996, 0.022051, 0.0, 0.026892, 0.098987, 0.208902, 0.346303, 0.499412, 0.653352, 0.792716, 0.90373, 0.975232, 0.999916]
        py = [0.001257, 0.006231, 0.019752, 0.03826, 0.057302, 0.072381, 0.079198, 0.072947, 0.054325, 0.028152, 0.0, -0.023408, -0.037507, -0.042346, -0.039941, -0.033493, -0.0245, -0.015499, -0.008033, -0.003035, -0.001257]

        self.points_c1 = np.array([pnt for pnt in zip(px, [0.]*len(px), py)]) * 2.
        self.points_c2 = np.array([pnt for pnt in zip(px, [0]*len(px), py)])
        self.points_c3 = np.array([pnt for pnt in zip(px, py, [0.]*len(px))]) * 0.2

        # shift sections to their correct position
        # second curve at y = 7
        self.points_c2 += np.array([1.0, 7, 0])

        # third curve at y = 7.5
        self.points_c3[:, 1] *= -1
        self.points_c3 += np.array([1.7, 7.8, 1.0])

        # upper trailing edge points
        self.te_up_points = np.array([self.points_c1[0,:], self.points_c2[0,:], self.points_c3[0,:]])

        # leading edge points. 
        self.le_points = np.array([
            self.points_c1[10,:],    # First profile LE

            [0.1, 2., -0.1],    # Additional point to control LE shape
            [0.3, 5., -0.2],    # Additional point to control LE shape
            
            self.points_c2[10,:],    # Second profile LE
            self.points_c3[10,:],    # Third profile LE
        ])


        self.skinning_parm = 0.7

        # lower trailing edge points
        self.te_lo_points = np.array([self.points_c1[-1,:], self.points_c2[-1,:], self.points_c3[-1,:]])

        self.curve1 = tigl3.curve_factories.interpolate_points(self.points_c1)
        self.curve2 = tigl3.curve_factories.interpolate_points(self.points_c2)
        self.curve3 = tigl3.curve_factories.interpolate_points(self.points_c3)

        self.profile_1_edge = BRepBuilderAPI_MakeEdge(self.curve1).Edge()
        self.profile_2_edge = BRepBuilderAPI_MakeEdge(self.curve2).Edge()
        self.profile_3_edge = BRepBuilderAPI_MakeEdge(self.curve3).Edge()

        self.te_up = tigl3.curve_factories.interpolate_points(self.te_up_points)
        self.le    = tigl3.curve_factories.interpolate_points(self.le_points)
        self.te_lo = tigl3.curve_factories.interpolate_points(self.te_lo_points)

        self.te_up_edge = BRepBuilderAPI_MakeEdge(self.te_up).Edge()
        self.le_edge = BRepBuilderAPI_MakeEdge(self.le).Edge()
        self.te_lo_edge = BRepBuilderAPI_MakeEdge(self.te_lo).Edge()

        self.surface_skin = None
        self.gordon_surface = None

    def get_updated_le(self):
        self.le = tigl3.curve_factories.interpolate_points(self.le_points, [0., 0.25, 0.55, 0.8, 1.0])
        return BRepBuilderAPI_MakeEdge(self.le).Edge()

    def show_profiles(self, renderer):
        renderer.DisplayPoints(self.points_c1, name='p1', size=5, color="red", update=False)
        renderer.DisplayPoints(self.points_c2, name='p2', size=5, color="red", update=False)
        renderer.DisplayPoints(self.points_c3, name='p3', size=5, color="red", update=False)
        renderer.DisplayShape(self.profile_1_edge, update=False, shape_color='#2cd342', quality=0.05)
        renderer.DisplayShape(self.profile_2_edge, update=False, shape_color='#2cd342', quality=0.05)
        renderer.DisplayShape(self.profile_3_edge, update=False, shape_color='#2cd342', quality=0.05)
        renderer._camera.fov=9.
        return renderer

    def get_gordon_surface(self):
        if self.gordon_surface is not None:
            return self.gordon_surface
        
        s = tigl3.surface_factories.interpolate_curve_network([self.curve1, self.curve2, self.curve3], [self.te_up, self.le, self.te_lo])
        self.gordon_surface = BRepBuilderAPI_MakeFace(s, 1e-6).Face()
        return self.surface_skin      

    def get_skinned_surface(self):
        if self.surface_skin is not None:
            return self.surface_skin
        
        s = tigl3.surface_factories.interpolate_curves([self.curve1, self.curve2, self.curve3])
        self.surface_skin = BRepBuilderAPI_MakeFace(s, 1e-6).Face()
        return self.surface_skin


    def show_wing_animation(self, renderer):


        renderer.DisplayPoints(self.le_points[1:3], name='lepoints', size=15, color="blue", update=False)
        renderer.DisplayShape(self.profile_1_edge, update=False, shape_color='#2cd342', quality=0.05)
        renderer.DisplayShape(self.profile_2_edge, update=False, shape_color='#2cd342', quality=0.05)
        renderer.DisplayShape(self.profile_3_edge, update=False, shape_color='#2cd342', quality=0.05)
        renderer.DisplayShape(self.te_up_edge, update=False, shape_color='blue', quality=0.1, render_edges=False)
        renderer.DisplayShape(self.le_edge, update=False, shape_color='blue', quality=0.1, render_edges=False)
        renderer.DisplayShape(self.te_lo_edge, update=False, shape_color='blue', quality=0.1, render_edges=False)
        renderer._camera.fov=9.

        def update(change):
            self.le_points[1, 0] = v1_slider.value
            self.le_points[2, 0] = v2_slider.value
            renderer.EraseObject('lepoints', update=False)
            renderer.DisplayPoints(self.le_points[1:3], name='lepoints', size=15, color="blue", update=False)

            le_edge_new = self.get_updated_le()
            renderer.DisplayShape(le_edge_new, quality=0.1, update=False, shape_color="blue")
            renderer.EraseShape(self.le_edge)
            self.le_edge = le_edge_new
            
            renderer.Update()

        def show_gordon_surface(b):
            b.disabled = True
            b.description = "... surface"


            surface = tigl3.surface_factories.interpolate_curve_network([self.curve1, self.curve2, self.curve3],
                                                                    [self.te_up, self.le, self.te_lo])
            wing_new = BRepBuilderAPI_MakeFace(surface, 1e-6).Face()

            b.disabled = False
            b.description = "... display"
            b.disabled = True
            renderer.DisplayShape(wing_new, shape_color='#0070a8', transparency=True, opacity=0.4, quality=0.2, update=False)
            if self.gordon_surface is not None:
                renderer.EraseShape(self.gordon_surface, update=False)
            if self.surface_skin is not None:
                renderer.EraseShape(self.surface_skin, update=False)
            renderer.Update()
            self.gordon_surface = wing_new
            b.disabled = False
            b.description = "Compute"

        def show_skinned_surface(b):
            b.disabled = True
            b.description = "... surface"
            self.skinning_parm = par_slider.value
            s = tigl3.surface_factories.interpolate_curves([self.curve1, self.curve2, self.curve3], [0., self.skinning_parm, 1.0])
            surface_skin_new = BRepBuilderAPI_MakeFace(s, 1e-6).Face()

            b.disabled = False
            b.description = "... display"
            b.disabled = True
            renderer.DisplayShape(surface_skin_new, shape_color='#0070a8', transparency=True, opacity=0.4, quality=0.2, update=False)
            if self.gordon_surface is not None:
                renderer.EraseShape(self.gordon_surface, update=False)
            if self.surface_skin is not None:
                renderer.EraseShape(self.surface_skin, update=False)
            renderer.Update()
            self.surface_skin = surface_skin_new
            b.disabled = False
            b.description = "Compute"
        
        
        button = Button(description="Compute")
        button.on_click(show_gordon_surface)
        button2 = Button(description="Compute")
        button2.on_click(show_skinned_surface)

        v1_slider, v2_slider = (FloatSlider(description='inner', min=-0.3, max=1., step=0.01, value=0.3,
                                                    continuous_update=False, orientation='horizontal'),
                                FloatSlider(description='outer', min=-0.1, max=1.3, step=0.01, value=0.3,
                                                    continuous_update=False, orientation='horizontal'))

        par_slider = FloatSlider(description='Parameter', min=0.3, max=0.95, step=0.01, value=self.skinning_parm,
                                                    continuous_update=False, orientation='horizontal')
        v1_slider.observe(update, names=['value'])
        v2_slider.observe(update, names=['value'])
        

        gordon_widget = VBox([v2_slider, v1_slider, button])
        skinning_wdget = VBox([par_slider, button2])

        accordion = Accordion(children=[
            gordon_widget,
            skinning_wdget])
        accordion.set_title(0, 'Gordon Surface')
        accordion.set_title(1, 'Skinning Surface')
        accordion

        return HBox([renderer._renderer, accordion])