import numpy as np

import tigl3.configuration
import tigl3.geometry
import tigl3.tigl3wrapper
import tixi3.tixi3wrapper

from OCC.Display.SimpleGui import init_display
from OCC.BRepBndLib import brepbndlib_Add
from OCC.Bnd import Bnd_Box
import OCC.Quantity

# The following parameters will be modified smoothly in an animation (in the given order!).
# Note, that these parameters don't have to be cpacs parameters. Here, the final values are defined.
smooth_parameters_final = {
    "fuselage": {
        "length": 5,
        "section_height": 1.5,
        "section_width": 1.75,
        "nose_center": tigl3.geometry.CTiglPoint(0, 0, -0.4),
        "nose_area": 0,
        "section_2_center": tigl3.geometry.CTiglPoint(0.3, 0, -0.2),
        "section_2_area": 0.8,
        "section_3_center": tigl3.geometry.CTiglPoint(1.2, 0, 0),
        "section_3_area": 2,
        "section_4_center": tigl3.geometry.CTiglPoint(5, 0, 0),
        "section_4_area": 2,
        "tail_angle": 20,
        "tail_center": tigl3.geometry.CTiglPoint(10, 0, 0.75),
        "tail_width": 0.075,
        "tail_height": 0.5,
    },
    "wing_main": {
        "root_leposition": tigl3.geometry.CTiglPoint(1.5, 0, -0.33),
        "scale": 2,
        "half_span": 8,
        "section_2_rel_pos": 0.95,
        "root_width": 1.75,
        "root_height": 0.25,
        "tip_width": 0.33,
        "tip_height": 0.05,
        "sweep": 12,
        "dihedral": 7,
        "winglet_center_translation": tigl3.geometry.CTiglPoint(0.1, 0.2, 0.4),
        "winglet_rotation": tigl3.geometry.CTiglPoint(80, 0, 0),
        "winglet_width": 0.25
    },
    "wing_htp": {
        "root_leposition": tigl3.geometry.CTiglPoint(9.5, 0, 0.55),
        "sweep": 25,
        "dihedral": 5,
        "tip_width": 0.5,
        "tip_height": 0.1
    },
    "wing_vtp": {
        "root_leposition": tigl3.geometry.CTiglPoint(9.5, 0, 0.55),
        "rotation": tigl3.geometry.CTiglPoint(90, 0, 0),
        "sweep": 25,
        "dihedral": 5,
        "tip_width": 0.5,
        "tip_height": 0.1
    }
}


def interpolate_parameters(p0, p1, theta):
    """
    linearly interpolates the smooth parameters defined the the dictionaries p0 and p1
    :param p0: first parameter set
    :param p1: second parameter set
    :param theta: A value between 0 and 1. theta=0 recreates p0, theta=1 recreates p1
    :return: the linearly interpolated parameter set
    """
    p = {"fuselage": {}, "wing_main": {}, "wing_htp": {}, "wing_vtp": {}}

    for component in p0:
        for parameter in p1[component]:
            if isinstance(p0[component][parameter], tigl3.geometry.CTiglPoint):
                p[component][parameter] = tigl3.geometry.CTiglPoint()
                p[component][parameter].x = (1 - theta) * p0[component][parameter].x \
                                            + theta * p1[component][parameter].x
                p[component][parameter].y = (1 - theta) * p0[component][parameter].y \
                                            + theta * p1[component][parameter].y
                p[component][parameter].z = (1 - theta) * p0[component][parameter].z \
                                            + theta * p1[component][parameter].z
            else:
                p[component][parameter] = (1-theta)*p0[component][parameter] + theta*p1[component][parameter]

    return p


def deduce_parameters(aircraft):
    """
    Given a tigl handle to the cpacs node of the aircraft, try to deduce the parameters to get initial
    conditions for the animation. Note that this only works well for the simple initial geometries.
    :param aircraft: a tigl handle to the cpacs node of the aircraft
    :return: a parameters dictionary
    """

    params = {"fuselage": {}, "wing_main": {}, "wing_htp": {}, "wing_vtp": {}}


    # deduce fuselage parameters

    fuselage = aircraft.get_fuselages().get_fuselage("fuselage")
    shape = fuselage.get_loft().shape()
    bbox = Bnd_Box()
    brepbndlib_Add(shape, bbox)
    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()

    params["fuselage"]["length"] = xmax - xmin
    params["fuselage"]["section_height"] = zmax - zmin
    params["fuselage"]["section_width"] = ymax - ymin

    c = fuselage.get_circumference(1, 0)
    params["fuselage"]["nose_area"] = 0.25*c**2/np.pi
    s = fuselage.get_section(1)
    e = s.get_section_element(1)
    ce = e.get_ctigl_section_element()
    params["fuselage"]["nose_center"] = ce.get_center()

    s = fuselage.get_section(2)
    e = s.get_section_element(1)
    ce = e.get_ctigl_section_element()
    params["fuselage"]["section_2_center"] = ce.get_center()
    c = fuselage.get_circumference(1, 1)
    params["fuselage"]["section_2_area"] = 0.25 * c ** 2 / np.pi

    s = fuselage.get_section(3)
    e = s.get_section_element(1)
    ce = e.get_ctigl_section_element()
    params["fuselage"]["section_3_center"] = ce.get_center()
    c = fuselage.get_circumference(2, 1)
    params["fuselage"]["section_3_area"] = 0.25 * c ** 2 / np.pi

    s = fuselage.get_section(4)
    e = s.get_section_element(1)
    ce = e.get_ctigl_section_element()
    params["fuselage"]["section_4_center"] = ce.get_center()
    c = fuselage.get_circumference(3, 1)
    params["fuselage"]["section_4_area"] = 0.25 * c ** 2 / np.pi

    tail_idx = fuselage.get_section_count()
    s = fuselage.get_section(tail_idx)
    e = s.get_section_element(1)
    ce = e.get_ctigl_section_element()
    params["fuselage"]["tail_width"] = ymax - ymin
    params["fuselage"]["tail_height"] = zmax - zmin
    params["fuselage"]["tail_angle"] = 0
    params["fuselage"]["tail_center"] = ce.get_center()

    # deduce main wing parameters

    wing_main = aircraft.get_wings().get_wing("wing_main")
    shape = wing_main.get_loft().shape()
    bbox = Bnd_Box()
    brepbndlib_Add(shape, bbox)
    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()

    params["wing_main"]["root_leposition"] = wing_main.get_root_leposition()
    params["wing_main"]["scale"] = 1
    params["wing_main"]["half_span"] = ymax - ymin
    params["wing_main"]["section_2_rel_pos"] = 0.5
    params["wing_main"]["root_width"] = xmax - xmin
    params["wing_main"]["root_height"] = zmax - zmin
    params["wing_main"]["tip_width"] = xmax - xmin
    params["wing_main"]["tip_height"] = zmax - zmin
    params["wing_main"]["sweep"] = 0
    params["wing_main"]["dihedral"] = 0
    params["wing_main"]["winglet_rotation"] = tigl3.geometry.CTiglPoint(0, 0, 0)
    tip_idx = wing_main.get_section_count()
    tip = wing_main.get_section(tip_idx).get_section_element(1).get_ctigl_section_element().get_center()
    pre_tip = wing_main.get_section(tip_idx-1).get_section_element(1).get_ctigl_section_element().get_center()
    params["wing_main"]["winglet_center_translation"] = tip - pre_tip
    params["wing_main"]["winglet_width"] = xmax - xmin

    # deduce htp wing parameters

    wing_htp = aircraft.get_wings().get_wing("wing_htp")
    shape = wing_htp.get_loft().shape()
    bbox = Bnd_Box()
    brepbndlib_Add(shape, bbox)
    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()

    params["wing_htp"]["root_leposition"] = wing_htp.get_root_leposition()
    params["wing_htp"]["sweep"] = 0
    params["wing_htp"]["dihedral"] = 0
    params["wing_htp"]["tip_width"] = xmax - xmin
    params["wing_htp"]["tip_height"] = zmax - zmin

    # deduce vtp wing parameters

    wing_vtp = aircraft.get_wings().get_wing("wing_vtp")
    shape = wing_vtp.get_loft().shape()
    bbox = Bnd_Box()
    brepbndlib_Add(shape, bbox)
    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()

    params["wing_vtp"]["root_leposition"] = wing_vtp.get_root_leposition()
    params["wing_vtp"]["rotation"] = tigl3.geometry.CTiglPoint(0, 0, 0)
    params["wing_vtp"]["sweep"] = 0
    params["wing_vtp"]["dihedral"] = 0
    params["wing_vtp"]["tip_width"] = xmax - xmin
    params["wing_vtp"]["tip_height"] = zmax - zmin

    return params


def modify_parameters(aircraft, params):
    """
    modify the parameters of an aircraft instance according to the parameters defined in the dictionary params
    :param aircraft: a tigl handle to the cpacs node of the aircraft
    :param params: a dictionary containing the parameter values
    :return: a list of the aircraft's lofts (i.e. fuselage, main wing, vtp and htp)
    """
    # collect all relevant lofts of the airplane (fuselage, main wing, htp, vtp)
    lofts = []

    # shape the fuselage
    fuselage = aircraft.get_fuselages().get_fuselage("fuselage")
    # fuselage.set_length(params["fuselage"]["length"])
    for i in range(1, fuselage.get_section_count()+1):
        e = fuselage.get_section(i).get_section_element(1)
        ce = e.get_ctigl_section_element()
        ce.set_height(params["fuselage"]["section_height"])
        ce.set_width(params["fuselage"]["section_width"])

    # shrink nose to a point
    s1 = fuselage.get_section(1)
    s1e1 = s1.get_section_element(1)
    s1e1ce = s1e1.get_ctigl_section_element()
    s1e1ce.set_center(params["fuselage"]["nose_center"])
    s1e1ce.set_area(params["fuselage"]["nose_area"])

    # move second section towards the nose
    s2 = fuselage.get_section(2)
    s2e1 = s2.get_section_element(1)
    s2e1ce = s2e1.get_ctigl_section_element()
    s2e1ce.set_center(params["fuselage"]["section_2_center"])
    s2e1ce.set_area(params["fuselage"]["section_2_area"])

    # move second section towards the nose
    s3 = fuselage.get_section(3)
    s3e1 = s3.get_section_element(1)
    s3e1ce = s3e1.get_ctigl_section_element()
    s3e1ce.set_center(params["fuselage"]["section_3_center"])
    s3e1ce.set_area(params["fuselage"]["section_3_area"])

    # move fourth section towards the tail
    s4 = fuselage.get_section(4)
    s4e1 = s4.get_section_element(1)
    s4e1ce = s4e1.get_ctigl_section_element()
    s4e1ce.set_center(params["fuselage"]["section_4_center"])
    s4e1ce.set_area(params["fuselage"]["section_4_area"])

    # transform the tail
    tail_idx = fuselage.get_section_count()
    st = fuselage.get_section(tail_idx)
    ste1 = st.get_section_element(1)
    ste1ce = ste1.get_ctigl_section_element()
    ste1ce.set_center(params["fuselage"]["tail_center"])
    # tail_angle = np.deg2rad(params["fuselage"]["tail_angle"])
    # ste1ce.set_normal(tigl3.geometry.CTiglPoint(np.cos(tail_angle), 0, np.sin(tail_angle)))
    ste1ce.set_width(params["fuselage"]["tail_width"])
    ste1ce.set_height(params["fuselage"]["tail_height"])

    lofts.append(fuselage.get_loft())

    # shape main wing
    wing_main = aircraft.get_wings().get_wing("wing_main")
    wing_main.set_root_leposition(params["wing_main"]["root_leposition"])
    wing_main.scale(params["wing_main"]["scale"])
    wing_main_half_span = params["wing_main"]["half_span"]
    wing_main.set_half_span_keep_area(wing_main_half_span)

    # move second to last section towards tip
    tip_idx = wing_main.get_section_count()
    tip = wing_main.get_section(tip_idx).get_section_element(1).get_ctigl_section_element().get_center()
    pre_tip = wing_main.get_section(tip_idx - 2).get_section_element(1).get_ctigl_section_element().get_center()
    s = wing_main.get_section(tip_idx - 1)
    e = s.get_section_element(1)
    ce = e.get_ctigl_section_element()
    center = ce.get_center()
    theta = params["wing_main"]["section_2_rel_pos"]
    center.x = theta * tip.x + (1 - theta) * pre_tip.x
    center.y = theta * tip.y + (1 - theta) * pre_tip.y
    center.z = theta * tip.z + (1 - theta) * pre_tip.z
    ce.set_center(center)

    # decrease section size towards wing tips
    root_width = params["wing_main"]["root_width"]
    root_height = params["wing_main"]["root_height"]
    tip_width = params["wing_main"]["tip_width"]
    tip_height = params["wing_main"]["tip_height"]
    n_sections = wing_main.get_section_count()
    for idx in range(1, n_sections + 1):
        s = wing_main.get_section(idx)
        e = s.get_section_element(1)
        ce = e.get_ctigl_section_element()

        theta = ce.get_center().y / wing_main_half_span

        ce.set_width((1 - theta) * root_width + theta * tip_width)
        ce.set_height((1 - theta) * root_height + theta * tip_height)

    wing_main.set_sweep(params["wing_main"]["sweep"])
    wing_main.set_dihedral(params["wing_main"]["dihedral"])

    # create winglet
    s = wing_main.get_section(tip_idx)
    e = s.get_section_element(1)
    ce = e.get_ctigl_section_element()
    pre_tip = wing_main.get_section(tip_idx - 1).get_section_element(1).get_ctigl_section_element().get_center()
    ce.set_center(pre_tip + params["wing_main"]["winglet_center_translation"])
    s.set_rotation(params["wing_main"]["winglet_rotation"])
    ce.set_width(params["wing_main"]["winglet_width"])

    lofts.append(wing_main.get_loft())
    lofts.append(wing_main.get_mirrored_loft())

    # shape htp
    wing_htp = aircraft.get_wings().get_wing("wing_htp")

    wing_htp.set_root_leposition(params["wing_htp"]["root_leposition"])
    wing_htp.set_sweep(params["wing_htp"]["sweep"])
    wing_htp.set_dihedral(params["wing_htp"]["dihedral"])

    tip_idx = wing_htp.get_section_count()
    s = wing_htp.get_section(tip_idx)
    e = s.get_section_element(1)
    ce = e.get_ctigl_section_element()
    ce.set_width(params["wing_htp"]["tip_width"])
    ce.set_height(params["wing_htp"]["tip_height"])

    lofts.append(wing_htp.get_loft())
    lofts.append(wing_htp.get_mirrored_loft())

    # shape vtp
    wing_vtp = aircraft.get_wings().get_wing("wing_vtp")

    wing_vtp.set_root_leposition(params["wing_vtp"]["root_leposition"])
    wing_vtp.set_rotation(params["wing_vtp"]["rotation"])
    wing_vtp.set_sweep(params["wing_vtp"]["sweep"])

    tip_idx = wing_vtp.get_section_count()
    s = wing_vtp.get_section(tip_idx)
    e = s.get_section_element(1)
    ce = e.get_ctigl_section_element()
    ce.set_width(params["wing_vtp"]["tip_width"])
    ce.set_height(params["wing_vtp"]["tip_height"])

    lofts.append(wing_vtp.get_loft())

    return lofts


def show_lofts(display, lofts, write_screenshots=True, basename='animation_', counter=0):

    #TODO: It would be awesome if I could update the shapes and not erase and redraw
    display.EraseAll()

    for loft in lofts:
        display.DisplayShape(loft.shape(), update=False)

    display.View.SetProj(-1, -1, 1)
    display.View.SetAt(5, 0, 0)
    display.View.SetScale(90)

    if write_screenshots:
        filename = basename + str(counter).zfill(4) + '.png'
        display.View.Dump(filename)
        counter += 1

    return counter


if __name__ == "__main__":

    # set some parameters for the animation

    n_frames_still = 5  # how many frames should be used for still images
    n_frames_animation = 20  # how many frames should be used for the main animation
    basename_animation = 'result/animation_'
    cpacs_file_out = 'out.xml'
    write_screenshots = True
    create_gif = True

    # start the display
    display, start_display, add_menu, add_function_to_menu = init_display()
    display.View.SetBackgroundColor(OCC.Quantity.Quantity_NOC_WHITE)
    display.hide_triedron()

    # initialize an empty aircraft from "empty.cpacs3.xml"
    filename = "empty.cpacs3.xml"
    tixi_h = tixi3.tixi3wrapper.Tixi3()
    tixi_h.open(filename)
    tigl_h = tigl3.tigl3wrapper.Tigl3()
    tigl_h.open(tixi_h, "")

    mgr = tigl3.configuration.CCPACSConfigurationManager_get_instance()
    aircraft = mgr.get_configuration(tigl_h._handle.value)

    # create a cylindrical fuselage and display for a few frames
    fuselages = aircraft.get_fuselages()
    fuselage = fuselages.create_fuselage("fuselage", 5, "fuselageCircleProfileuID")
    lofts = [fuselage.get_loft(), ]

    frame_cnt = 0
    for i in range(0, n_frames_still):
        frame_cnt = show_lofts(display, lofts,
                               write_screenshots=write_screenshots,
                               basename=basename_animation,
                               counter=frame_cnt)

    # create main wing and display for a few frames
    wings = aircraft.get_wings()
    wing_main = wings.create_wing("wing_main", 3, "NACA0012")
    wing_main.set_symmetry(tigl3.geometry.TIGL_X_Z_PLANE)
    wing_main.set_root_leposition(tigl3.geometry.CTiglPoint(-2, 0, 0))
    lofts.append(wing_main.get_loft())

    for i in range(0, n_frames_still):
        frame_cnt = show_lofts(display, lofts,
                               write_screenshots=write_screenshots,
                               basename=basename_animation,
                               counter=frame_cnt)

    # create the horizontal tailplane and display for a few frames
    wing_htp = wings.create_wing("wing_htp", 2, "NACA0012")
    wing_htp.set_symmetry(tigl3.geometry.TIGL_X_Z_PLANE)
    wing_htp.set_root_leposition(tigl3.geometry.CTiglPoint(5, 0, 0))
    lofts.append(wing_htp.get_loft())

    for i in range(0, n_frames_still):
        frame_cnt = show_lofts(display, lofts,
                               write_screenshots=write_screenshots,
                               basename=basename_animation,
                               counter=frame_cnt)

    # create the vertical tailplane and display for a few frames
    wing_vtp = wings.create_wing("wing_vtp", 2, "NACA0012")
    wing_vtp.set_root_leposition(tigl3.geometry.CTiglPoint(7, 0, 0))
    lofts.append(wing_vtp.get_loft())

    for i in range(0, n_frames_still):
        frame_cnt = show_lofts(display, lofts,
                               write_screenshots=write_screenshots,
                               basename=basename_animation,
                               counter=frame_cnt)

    # now that all parts of the airplane are defined and the topology is fixed, we can deduce the
    # initial condition of the parameters we want to change
    p0 = deduce_parameters(aircraft)
    p1 = smooth_parameters_final

    # now smoothly change the chosen parameters from the initial to the final state to get an animation
    # note that we get a valid cpacs configuration for each frame of the animation
    for i in range(0, n_frames_animation):

        if n_frames_animation == 1:
            theta = 1
        else:
            theta = i / (n_frames_animation - 1)

        p = interpolate_parameters(p0, p1, theta)
        lofts = modify_parameters(aircraft, p)
        frame_cnt = show_lofts(display, lofts,
                               write_screenshots=write_screenshots,
                               basename=basename_animation,
                               counter=frame_cnt)

    # create a few frames of the finished airplane
    for i in range(0, n_frames_still):
        frame_cnt = show_lofts(display, lofts,
                               write_screenshots=write_screenshots,
                               basename=basename_animation,
                               counter=frame_cnt)

    # write the CPACS file of the finished airplane. Note that we could move this into the for loop
    # if we wanted to save the cpacs configuration at each increment
    aircraft.write_cpacs(aircraft.get_uid())
    config_as_string = tixi_h.exportDocumentAsString()
    text_file = open(cpacs_file_out, "w")
    text_file.write(config_as_string)
    text_file.close()

    # create an animated GIF from the generated screenshots, if imageio is available
    if create_gif:
        try:
            import imageio
            import os

            png_dir = 'result/'
            images = []
            for file_name in os.listdir(png_dir):
                if file_name.endswith('.png'):
                    file_path = os.path.join(png_dir, file_name)
                    images.append(imageio.imread(file_path))
            imageio.mimsave('movie.gif', images)
        except:
            print("Not creating gif: imageio not available")

    # make display interactive
    start_display()
