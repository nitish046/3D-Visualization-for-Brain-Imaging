import vtk
import itk
from vtk import vtkRenderer, vtkRenderWindow
from vtk import vtkRenderWindowInteractor
from vtk import vtkMetaImageReader

MRI_FILE_PATH = "/Users/sachin_veera/Desktop/brain-tumor-segmentation-master-2/data/BRATS_HG0015_T1C.mha"
MASK_OUTPUT_PATH = (
    "/Users/sachin_veera/Desktop/brain-tumor-segmentation-master-2/temp/output_mask.mha"
)


def custom_morpho_filters(image, filters):
    history = [image]
    for attribute, number, reverse in filters:
        history.append(
            itk.LabelShapeKeepNObjectsImageFilter.New(
                Input=history[-1],
                BackgroundValue=0,
                NumberOfObjects=number,
                Attribute=attribute,
                ReverseOrdering=reverse,
            )
        )
    return history


def generate_custom_mask(image, path_out=None):
    mask = itk.NotImageFilter(Input=image)
    mask = itk.NotImageFilter(Input=mask)

    converted = itk.CastImageFilter[itk.Image[itk.SS, 3], itk.Image[itk.UC, 3]].New(
        Input=mask
    )

    result_image = itk.RescaleIntensityImageFilter.New(
        Input=converted,
        OutputMinimum=0,
        OutputMaximum=1,
    )

    if path_out:
        writer = itk.ImageFileWriter.New(Input=result_image, FileName=path_out)
        writer.Update()
    else:
        result_image.Update()

    return result_image


mri_reader = itk.ImageFileReader(FileName=MRI_FILE_PATH)

rescaled_mri = itk.RescaleIntensityImageFilter.New(
    Input=mri_reader, OutputMinimum=0, OutputMaximum=255
)

binary_image = itk.ThresholdImageFilter.New(
    Input=rescaled_mri,
    Lower=102,
)

connected_components = itk.ConnectedComponentImageFilter.New(
    Input=binary_image,
)

# Define and apply connected components filters
CUSTOM_FILTERS = [
    ("NumberOfPixels", 10, False),
    ("Flatness", 5, True),
    ("NumberOfPixels", 3, False),
]

cc_filters_result = custom_morpho_filters(connected_components, filters=CUSTOM_FILTERS)
custom_mask = generate_custom_mask(cc_filters_result[-1], path_out=MASK_OUTPUT_PATH)


# VTK Rendering
def _check_custom_arg(val, name, available):
    if val not in available:
        raise ValueError(
            f"{name}='{val}' is not a valid arg. Valid values are: {available}"
        )


def load_custom_volume(
    reader, color=(1.0, 1.0, 1.0), render_with="gl", interpolation="linear"
):
    _check_custom_arg(render_with, "render_with", {"gl", "gpu", "cpu"})
    _check_custom_arg(interpolation, "interpolation", {"linear", "nearest"})

    reader.Update()

    if render_with == "gl":
        mapper = vtk.vtkOpenGLGPUVolumeRayCastMapper()
    elif render_with == "gpu":
        mapper = vtk.vtkGPUVolumeRayCastMapper()
    elif render_with == "cpu":
        mapper = vtk.vtkFixedPointVolumeRayCastMapper()
    else:
        raise ValueError("Unexpected value for render_with")

    mapper.SetInputConnection(reader.GetOutputPort())
    mapper.SetAutoAdjustSampleDistances(0)
    mapper.SetSampleDistance(0.5)
    mapper.SetMaskTypeToLabelMap()
    mapper.SetMaskBlendFactor(0.7)
    mapper.SetBlendModeToComposite()

    props = vtk.vtkVolumeProperty()
    props.SetIndependentComponents(True)
    props.ShadeOff()

    if interpolation == "linear":
        props.SetInterpolationTypeToLinear()
    elif interpolation == "nearest":
        props.SetInterpolationTypeToNearest()
    else:
        raise ValueError("Unexpected value for interpolation")

    volume_object = vtk.vtkVolume()
    volume_object.SetMapper(mapper)
    volume_object.SetProperty(props)

    return volume_object


# Load volumes and generated custom mask
reader_mri = vtk.vtkMetaImageReader()
reader_mri.SetFileName(MRI_FILE_PATH)
reader_mask = vtk.vtkMetaImageReader()
reader_mask.SetFileName(MASK_OUTPUT_PATH)
reader_mask.Update()

custom_volume = load_custom_volume(reader_mri)
custom_volume_property = custom_volume.GetProperty()
custom_volume_mapper = custom_volume.GetMapper()

# Set rendering properties (color, opacity)
data_min_val, data_max_val = reader_mri.GetOutput().GetScalarRange()

seg_min_val, seg_max_val = 0, 0.6 * data_max_val
custom_color_function = vtk.vtkColorTransferFunction()
custom_color_function.AddRGBSegment(seg_min_val, *(0, 0, 0), seg_max_val, *(1, 1, 1))

custom_color_mask_function = vtk.vtkColorTransferFunction()
custom_color_mask_function.AddRGBSegment(
    seg_min_val, *(0, 0, 0), seg_max_val, *(1, 0, 0)
)

custom_opacity_function = vtk.vtkPiecewiseFunction()
custom_opacity_function.AddSegment(seg_min_val, 0.0, seg_max_val, 0.1)

custom_opacity_mask_function = vtk.vtkPiecewiseFunction()
custom_opacity_mask_function.AddSegment(seg_min_val, 0.0, seg_max_val, 1.0)

custom_volume_property.SetColor(custom_color_function)
custom_volume_property.SetScalarOpacity(custom_opacity_function)
custom_volume_property.SetLabelColor(1, custom_color_mask_function)
custom_volume_property.SetLabelScalarOpacity(1, custom_opacity_mask_function)

# Apply generated custom mask
custom_volume_mapper.SetMaskInput(reader_mask.GetOutput())


# Define UI callbacks
def OnCustomClose(interactor, event):
    # Callback to correctly close the UI
    interactor.GetRenderWindow().Finalize()
    interactor.TerminateApp()


def cb_opacity_custom(x):
    # Callback to update custom volume opacity
    custom_opacity_function.AddSegment(seg_min_val, 0.0, seg_max_val, x)


def cb_opacity_mask_custom(x):
    # Callback to update custom mask opacity
    custom_volume_mapper.SetMaskBlendFactor(x)


def cb_custom_morpho_filters(idx):
    # Generate callbacks to update the custom morpho filters
    def cb(x):
        attr, _, negate = CUSTOM_FILTERS[idx]
        CUSTOM_FILTERS[idx] = (attr, x, negate)

        cc_filters_result = custom_morpho_filters(
            connected_components, filters=CUSTOM_FILTERS
        )

        result_image = generate_custom_mask(cc_filters_result[-1], MASK_OUTPUT_PATH)
        reader_mask = vtkMetaImageReader()
        reader_mask.SetFileName(MASK_OUTPUT_PATH)
        reader_mask.Update()
        custom_volume_mapper.SetMaskInput(reader_mask.GetOutput())

    return cb


def AddCustomSlider(
    interactor,
    value_range,
    x,
    y,
    length=0.25,
    title="",
    default_value=None,
    callback=lambda x: _,
    integer_steps=False,
):
    assert 0 <= x <= 1 and 0 <= y <= 1

    def _cb(s, *args):
        slider_representation = s.GetSliderRepresentation()
        value = slider_representation.GetValue()
        if integer_steps:
            value = round(value)
            slider_representation.SetValue(value)
        callback(value)
        sliderWidget.AddObserver(
            "InteractionEvent",
            lambda s, *args: callback(s.GetSliderRepresentation().GetValue()),
        )

    # Set slider properties
    slider = vtk.vtkSliderRepresentation2D()
    slider.SetMinimumValue(value_range[0])
    slider.SetMaximumValue(value_range[-1])
    slider.SetValue(value_range[0] if default_value is None else default_value)
    slider.SetTitleText(title)
    slider.ShowSliderLabelOn()
    slider.SetSliderWidth(0.03)
    slider.SetSliderLength(0.0001)
    slider.SetEndCapWidth(0)
    slider.SetTitleHeight(0.02)
    slider.SetTubeWidth(0.005)

    # Set the slider position
    slider.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
    slider.GetPoint1Coordinate().SetValue(x, y)
    slider.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
    slider.GetPoint2Coordinate().SetValue(x + length, y)

    # Add the slider to the UI
    sliderWidget = vtk.vtkSliderWidget()
    sliderWidget.SetInteractor(interactor)
    sliderWidget.SetRepresentation(slider)
    sliderWidget.EnabledOn()

    # Add callback
    sliderWidget.AddObserver("InteractionEvent", _cb)

    return sliderWidget


custom_ren = vtkRenderer()
custom_ren.AddVolume(custom_volume)

custom_renWin = vtkRenderWindow()
custom_renWin.AddRenderer(custom_ren)

custom_iren = vtkRenderWindowInteractor()
custom_iren.SetRenderWindow(custom_renWin)

custom_iren.AddObserver("ExitEvent", OnCustomClose)

# Add all UI sliders for the custom volume rendering
sl_0_custom = AddCustomSlider(
    interactor=custom_iren,
    value_range=(0, 1),
    x=0.7,
    y=0.15,
    title="Custom Volume Opacity",
    default_value=0.1,
    callback=cb_opacity_custom,
)
sl_1_custom = AddCustomSlider(
    interactor=custom_iren,
    value_range=(0, 1),
    x=0.7,
    y=0.30,
    title="Custom Volume Mask Highlight",
    default_value=0.7,
    callback=cb_opacity_mask_custom,
)

sl_2_custom = AddCustomSlider(
    interactor=custom_iren,
    value_range=(0, 20),
    x=0.7,
    y=0.55,
    title="2. Custom NB Final Components",
    default_value=3,
    callback=cb_custom_morpho_filters(2),
    integer_steps=True,
)
sl_3_custom = AddCustomSlider(
    interactor=custom_iren,
    value_range=(1, 20),
    x=0.7,
    y=0.70,
    title="1. Custom NB Bumpiest",
    default_value=5,
    callback=cb_custom_morpho_filters(1),
    integer_steps=True,
)
sl_4_custom = AddCustomSlider(
    interactor=custom_iren,
    value_range=(1, 20),
    x=0.7,
    y=0.85,
    title="0. Custom NB Biggest Components",
    default_value=10,
    callback=cb_custom_morpho_filters(0),
    integer_steps=True,
)

# Launch the custom volume rendering app
custom_iren.Initialize()
custom_renWin.Render()
custom_iren.Start()
