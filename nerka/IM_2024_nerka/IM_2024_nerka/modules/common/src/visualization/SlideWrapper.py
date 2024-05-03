import vtk


class SliderWrapper:
    def __init__(self, title_text, value_range, initial_value, position):
        slider_rep = vtk.vtkSliderRepresentation2D()
        slider_rep.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
        slider_rep.GetPoint1Coordinate().SetValue(*position[0])
        slider_rep.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
        slider_rep.GetPoint2Coordinate().SetValue(*position[1])
        slider_rep.SetMinimumValue(value_range[0])
        slider_rep.SetMaximumValue(value_range[1])
        slider_rep.SetValue(initial_value)
        slider_rep.SetTitleText(title_text)
        self._slider_rep = slider_rep

    def get_widget(self, interactor):
        widget = vtk.vtkSliderWidget()
        widget.SetInteractor(interactor)
        widget.SetRepresentation(self._slider_rep)
        widget.SetAnimationModeToAnimate()
        widget.EnabledOn()
        return widget
