import vtk
from scipy.ndimage import zoom

from modules.common.src.visualization.SlideWrapper import SliderWrapper
from modules.common.src.visualization.common import get_transform_function, get_color_function


class VolumeVisualizer:
    def __init__(self, volume, binary=True, data_scalar_range='auto'):
        self._volume = volume
        self._binary = binary

        if data_scalar_range == 'auto':
            data_scalar_range = (int(volume.min()), int(volume.max()))

        self._data_scalar_range = data_scalar_range

        self._dynamic_properties = {
            'opacity_function_midpoint': (data_scalar_range[0] + data_scalar_range[1]) / 2.,
            'opacity_function_max': 1.,
            'opacity_function_width': (data_scalar_range[1] - data_scalar_range[0]) / 2.
        }

    def visualize(self, scale=1, interpolation_order=0, primary_color=None):
        volume = zoom(self._volume, scale, order=interpolation_order)
        flat_volume = volume.transpose((2, 1, 0)).flatten()

        # --- data_importer
        data_importer = vtk.vtkImageImport()
        data_string = flat_volume.tostring()
        data_importer.CopyImportVoidPointer(data_string, len(data_string))
        data_importer.SetDataScalarTypeToUnsignedChar()
        data_importer.SetNumberOfScalarComponents(1)
        data_importer.SetDataExtent(0, volume.shape[0] - 1, 0, volume.shape[1] - 1, 0, volume.shape[2] - 1)
        data_importer.SetWholeExtent(0, volume.shape[0] - 1, 0, volume.shape[1] - 1, 0, volume.shape[2] - 1)

        # --- mapper
        mapper = vtk.vtkSmartVolumeMapper()
        mapper.SetInputConnection(data_importer.GetOutputPort())

        # --- actor
        actor = vtk.vtkVolume()
        actor.SetMapper(mapper)

        # --- renderer
        renderer = vtk.vtkRenderer()
        renderer.AddActor(actor)

        # --- window
        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)
        render_window.SetSize(800, 600)

        # --- interactor
        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(render_window)

        if self._binary:
            actor.GetProperty().SetScalarOpacity(0, get_transform_function(1, 0.5, 1, 0))
            color_function = get_color_function(1, primary_color if primary_color is not None else (1, 1, 1))
            actor.GetProperty().SetColor(0, color_function)
        else:
            def slider_callback_wrapper(property_name):
                def callback(caller, _):
                    value = caller.GetSliderRepresentation().GetValue()
                    self._dynamic_properties[property_name] = value
                    l_transform_function = get_transform_function(
                        mid_point=self._dynamic_properties['opacity_function_midpoint'],
                        delta=self._dynamic_properties['opacity_function_width'] / 2.,
                        margin_value=0.,
                        central_value=self._dynamic_properties['opacity_function_max']
                    )
                    actor.GetProperty().SetScalarOpacity(0, l_transform_function)
                    if primary_color is not None:
                        l_color_function = get_color_function(self._dynamic_properties['opacity_function_midpoint'],
                                                            primary_color)
                        actor.GetProperty().SetColor(0, l_color_function)
                    render_window.Render()

                return callback

            midpoint_slider_widget = SliderWrapper(
                title_text='opacity function midpoint',
                value_range=self._data_scalar_range,
                initial_value=self._dynamic_properties['opacity_function_midpoint'],
                position=((.7, .1), (.9, .1))
            ).get_widget(interactor)
            midpoint_slider_widget.AddObserver('InteractionEvent', slider_callback_wrapper('opacity_function_midpoint'))

            width_slider_widget = SliderWrapper(
                title_text='opacity function width',
                value_range=(0, self._data_scalar_range[1] - self._data_scalar_range[0]),
                initial_value=self._dynamic_properties['opacity_function_width'],
                position=((.7, .25), (.9, .25))
            ).get_widget(interactor)
            width_slider_widget.AddObserver('InteractionEvent', slider_callback_wrapper('opacity_function_width'))

            opacity_slider_widget = SliderWrapper(
                title_text='max opacity',
                value_range=(0., 1.),
                initial_value=1.,
                position=((.7, .4), (.9, .4))
            ).get_widget(interactor)
            opacity_slider_widget.AddObserver('InteractionEvent', slider_callback_wrapper('opacity_function_max'))

            transform_function = get_transform_function(
                mid_point=self._dynamic_properties['opacity_function_midpoint'],
                delta=self._dynamic_properties['opacity_function_width'] / 2.,
                margin_value=0.,
                central_value=self._dynamic_properties['opacity_function_max']
            )
            actor.GetProperty().SetScalarOpacity(0, transform_function)
            if primary_color is not None:
                color_function = get_color_function(self._dynamic_properties['opacity_function_midpoint'],
                                                    primary_color)
                actor.GetProperty().SetColor(0, color_function)

        # --- start
        render_window.Render()
        style = vtk.vtkInteractorStyleTrackballCamera()
        interactor.SetInteractorStyle(style)
        interactor.Initialize()
        interactor.Start()
