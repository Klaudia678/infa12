import vtk


def get_transform_function(mid_point, delta, central_value, margin_value):
    transform_function = vtk.vtkPiecewiseFunction()
    transform_function.AddPoint(mid_point - delta, margin_value)
    transform_function.AddPoint(mid_point, central_value)
    transform_function.AddPoint(mid_point + delta, margin_value)
    transform_function.AddPoint(0, 0)
    return transform_function


def get_color_function(mid_point, primary_color):
    volume_color = vtk.vtkColorTransferFunction()
    volume_color.AddRGBPoint(mid_point - 50, *(0, 0, 0))
    volume_color.AddRGBPoint(mid_point, *primary_color)
    volume_color.AddRGBPoint(mid_point + 50, *(0, 0, 0))
    return volume_color
