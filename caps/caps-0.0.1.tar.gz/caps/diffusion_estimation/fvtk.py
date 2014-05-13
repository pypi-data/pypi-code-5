#! /usr/bin/env python
##########################################################################
# CAPS - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
import numpy

# Caps import
from monomials import construct_matrix_of_monomials

# VTK import
try:
    import vtk
except ImportError:
    raise ImportError("VTK is not installed.")


def ren():
    """Create a renderer

    Returns
    --------
    ren: vtkRenderer() object

    Examples
    --------
    >>> import fvtk
    >>> ren = fvtk.ren()
    >>> fvtk.add(ren, actor)
    >>> fvtk.show(ren)
    """
    return vtk.vtkRenderer()


def add(ren, actor):
    """ Add a specific actor
    """
    if isinstance(actor, vtk.vtkVolume):
        ren.AddVolume(actor)
    else:
        ren.AddActor(actor)


def rm(ren, actor):
    """ Remove a specific actor
    """
    ren.RemoveActor(actor)


def clear(ren):
    """ Remove all actors from the renderer
    """
    ren.RemoveAllViewProps()


def show(ren, title="fvtk", size=(300, 300)):
    """ Show window

    Parameters
    ----------
    ren : vtkRenderer() object
        as returned from function ren()
    title : string
        a string for the window title bar
    size : (int, int)
        (width,height) of the window
    """
    ren.ResetCameraClippingRange()

    window = vtk.vtkRenderWindow()
    window.AddRenderer(ren)
    window.SetWindowName(title)
    window.SetSize(size)

    style = vtk.vtkInteractorStyleTrackballCamera()
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(window)
    iren.SetInteractorStyle(style)
    iren.Initialize()

    window.Render()
    iren.Start()


def tensor(coeff, order, position=(0, 0, 0),
           radius=0.5, thetares=20, phires=20, opacity=1, tessel=0):
    """ Generate a generic tensor actor
    """
    # Create a sphere that we will deform
    sphere = vtk.vtkSphereSource()
    sphere.SetRadius(radius)
    sphere.SetLatLongTessellation(tessel)
    sphere.SetThetaResolution(thetares)
    sphere.SetPhiResolution(phires)

    # Get the polydata
    poly = sphere.GetOutput()
    poly.Update()

    # Get the mesh
    numPts = poly.GetNumberOfPoints()
    mesh = numpy.zeros((numPts, 3), dtype=numpy.single)
    for i in range(numPts):
        mesh[i, :] = (poly.GetPoint(i)[0], poly.GetPoint(i)[1],
                      poly.GetPoint(i)[2])

    # Deform mesh
    design_matrix = construct_matrix_of_monomials(mesh, order)
    signal = numpy.dot(design_matrix, coeff)
    #signal = np.maximum(signal, 0.0)
    signal /= signal.max()
    signal *= 0.5

    scalars = vtk.vtkFloatArray()
    pts = vtk.vtkPoints()
    pts.SetNumberOfPoints(numPts)
    for i in range(numPts):
        pts.SetPoint(i, signal[i] * mesh[i, 0], signal[i] * mesh[i, 1],
                     signal[i] * mesh[i, 2])
        scalars.InsertTuple1(i, signal[i])

    poly.SetPoints(pts)
    poly.GetPointData().SetScalars(scalars)
    poly.Update()

    lut = vtk.vtkLookupTable()
    lut.SetHueRange(0.667, 0.0)
    lut.Build()

    spherem = vtk.vtkPolyDataMapper()
    spherem.SetInput(poly)
    spherem.SetLookupTable(lut)
    spherem.ScalarVisibilityOn()
    spherem.SetColorModeToMapScalars()
    spherem.SetScalarRange(0.0, 0.5)

    actor = vtk.vtkActor()
    actor.SetMapper(spherem)
    actor.SetPosition(position)
    actor.GetProperty().SetOpacity(opacity)

    return actor