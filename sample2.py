import sys
import vtk
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import Qt

from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import itk


"""
    The Qt MainWindow class
    A vtk widget and the ui controls will be added to this main window
"""


class MainWindow(Qt.QMainWindow):
    def __init__(self, parent=None):
        Qt.QMainWindow.__init__(self, parent)

        """ Step 1: Initialize the Qt window """
        self.setWindowTitle("Visualization")
        self.resize(1000, self.height())
        self.frame = Qt.QFrame()  # Create a main window frame to add ui widgets
        self.mainLayout = Qt.QHBoxLayout()  # Set layout - Lines up widgets horizontally
        self.frame.setLayout(self.mainLayout)
        self.setCentralWidget(self.frame)

        """ Step 2: Add a vtk widget to the central widget """
        # As we use QHBoxLayout, the vtk widget will be automatically moved to the left
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.mainLayout.addWidget(self.vtkWidget)

        # Initialize the vtk variables for the visualization tasks
        self.init_vtk_widget()

        # Add an object to the rendering window
        # self.add_vtk_object()

        """ Step 3: Add the control panel to the right hand side of the central widget """
        # Note: To add a widget, we first need to create a widget, then set the layout for it
        self.right_panel_widget = Qt.QWidget()  # create a widget
        self.right_panel_layout = (
            Qt.QVBoxLayout()
        )  # set layout - lines up the controls vertically
        self.right_panel_widget.setLayout(
            self.right_panel_layout
        )  # assign the layout to the widget
        self.mainLayout.addWidget(
            self.right_panel_widget
        )  # now, add it to the central frame

        # The controls will be added here
        self.add_controls()

    """
        Initialize the vtk variables for the visualization tasks
    """

    def init_vtk_widget(self):
        vtk.vtkObject.GlobalWarningDisplayOff()  # Disable vtkOutputWindow - Comment out this line if you want to see the warning/error messages from vtk

        # Create the graphics structure. The renderer renders into the render
        # window. The render window interactor captures mouse events and will
        # perform appropriate camera or actor manipulation depending on the
        # nature of the events.
        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        colors = vtk.vtkNamedColors()
        self.ren.SetBackground(
            0.8, 0.8, 0.8
        )  # you can change the background color here

        # Start by creating a black/white lookup table.
        self.bwLut = vtk.vtkLookupTable()
        # YOU need adjust the following range to address the dynamic range issue!
        self.bwLut.SetTableRange(0, 2)
        self.bwLut.SetSaturationRange(0, 0)
        self.bwLut.SetHueRange(0, 0)
        self.bwLut.SetValueRange(0, 1)
        self.bwLut.Build()  # effective built

        # Start the vtk screen
        self.ren.ResetCamera()
        self.show()
        self.iren.Initialize()
        self.iren.Start()

    """ 
        Show a popup message 
    """

    def show_popup_message(self, msg):
        alert = Qt.QMessageBox()
        alert.setText(msg)
        alert.exec_()

    def init_itk_reader(self):
        # File dialog to choose the brain image file
        dlg = Qt.QFileDialog()
        dlg.setFileMode(Qt.QFileDialog.AnyFile)
        dlg.setNameFilter("Image files (*.mha)")
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            brain_image_path = filenames[0]

            # Set up the ITK reader for the brain image
            self.reader_brain = itk.ImageFileReader[itk.Image[itk.UC, 3]].New()
            self.reader_brain.SetFileName(brain_image_path)
            self.reader_brain.Update()

    """
        Add QT controls to the control panel in the righ hand size
    """

    def add_controls(self):
        """Add a sample group box"""
        groupBox = Qt.QGroupBox(
            "3D Scalar Field Visualization"
        )  # Use a group box to group controls
        groupBox_layout = Qt.QVBoxLayout()  # lines up the controls vertically
        groupBox.setLayout(groupBox_layout)
        self.right_panel_layout.addWidget(groupBox)

        """ Add a textfield ( QLineEdit) to show the file path and the browser button """
        label = Qt.QLabel("Choose a file (e.g., vtk):")
        groupBox_layout.addWidget(label)
        hbox = Qt.QHBoxLayout()
        self.ui_file_name = Qt.QLineEdit()
        hbox.addWidget(self.ui_file_name)
        self.ui_browser_button = Qt.QPushButton("Browser")
        self.ui_browser_button.clicked.connect(self.on_file_browser_clicked)
        self.ui_browser_button.show()
        hbox.addWidget(self.ui_browser_button)
        file_widget = Qt.QWidget()
        file_widget.setLayout(hbox)
        groupBox_layout.addWidget(file_widget)

        """ Add the Open button """
        self.ui_open_button = Qt.QPushButton("Open")
        self.ui_open_button.clicked.connect(self.open_vtk_file)
        self.ui_open_button.show()
        groupBox_layout.addWidget(self.ui_open_button)

        """ Add the min, max scalar labels """
        self.ui_min_label = Qt.QLabel("Min Scalar: 0")
        self.ui_max_label = Qt.QLabel("Max Scalar: 0")
        groupBox_layout.addWidget(self.ui_min_label)
        groupBox_layout.addWidget(self.ui_max_label)

        # Add spin box for table range
        table_range_label = Qt.QLabel("Select the scalar range for color table")
        groupBox_layout.addWidget(table_range_label)
        hbox = Qt.QHBoxLayout()
        self.ui_min_range = Qt.QDoubleSpinBox()
        hbox.addWidget(self.ui_min_range)
        self.label_min_range = Qt.QLabel("Min Range")
        hbox.addWidget(self.label_min_range)
        self.ui_max_range = Qt.QDoubleSpinBox()
        hbox.addWidget(self.ui_max_range)
        self.label_max_range = Qt.QLabel("Max Range")
        hbox.addWidget(self.label_max_range)
        tablerange_hwidget = Qt.QWidget()
        tablerange_hwidget.setLayout(hbox)
        groupBox_layout.addWidget(tablerange_hwidget)

        """ Add spinbox for scalar threshold selection """
        hbox = Qt.QHBoxLayout()
        self.ui_isoSurf_checkbox = Qt.QCheckBox("Show iso-surface (select threshold)")
        hbox.addWidget(self.ui_isoSurf_checkbox)
        self.ui_isoSurf_checkbox.setChecked(False)
        self.ui_isoSurf_checkbox.toggled.connect(self.on_checkbox_change)
        self.ui_iso_threshold = Qt.QDoubleSpinBox()
        hbox.addWidget(self.ui_iso_threshold)

        import sys


import vtk
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import Qt

from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import itk


"""
    The Qt MainWindow class
    A vtk widget and the ui controls will be added to this main window
"""


class MainWindow(Qt.QMainWindow):
    def __init__(self, parent=None):
        Qt.QMainWindow.__init__(self, parent)

        """ Step 1: Initialize the Qt window """
        self.setWindowTitle("Visualization ")
        self.resize(1000, self.height())
        self.frame = Qt.QFrame()  # Create a main window frame to add ui widgets
        self.mainLayout = Qt.QHBoxLayout()  # Set layout - Lines up widgets horizontally
        self.frame.setLayout(self.mainLayout)
        self.setCentralWidget(self.frame)

        """ Step 2: Add a vtk widget to the central widget """
        # As we use QHBoxLayout, the vtk widget will be automatically moved to the left
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.mainLayout.addWidget(self.vtkWidget)

        # Initialize the vtk variables for the visualization tasks
        self.init_vtk_widget()

        # Add an object to the rendering window
        # self.add_vtk_object()

        """ Step 3: Add the control panel to the right hand side of the central widget """
        # Note: To add a widget, we first need to create a widget, then set the layout for it
        self.right_panel_widget = Qt.QWidget()  # create a widget
        self.right_panel_layout = (
            Qt.QVBoxLayout()
        )  # set layout - lines up the controls vertically
        self.right_panel_widget.setLayout(
            self.right_panel_layout
        )  # assign the layout to the widget
        self.mainLayout.addWidget(
            self.right_panel_widget
        )  # now, add it to the central frame

        # The controls will be added here
        self.add_controls()

    """
        Initialize the vtk variables for the visualization tasks
    """

    def init_vtk_widget(self):
        vtk.vtkObject.GlobalWarningDisplayOff()  # Disable vtkOutputWindow - Comment out this line if you want to see the warning/error messages from vtk

        # Create the graphics structure. The renderer renders into the render
        # window. The render window interactor captures mouse events and will
        # perform appropriate camera or actor manipulation depending on the
        # nature of the events.
        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        colors = vtk.vtkNamedColors()
        self.ren.SetBackground(
            0.8, 0.8, 0.8
        )  # you can change the background color here

        # Start by creating a black/white lookup table.
        self.bwLut = vtk.vtkLookupTable()
        # YOU need adjust the following range to address the dynamic range issue!
        self.bwLut.SetTableRange(0, 2)
        self.bwLut.SetSaturationRange(0, 0)
        self.bwLut.SetHueRange(0, 0)
        self.bwLut.SetValueRange(0, 1)
        self.bwLut.Build()  # effective built

        # Start the vtk screen
        self.ren.ResetCamera()
        self.show()
        self.iren.Initialize()
        self.iren.Start()

    """ 
        Show a popup message 
    """

    def show_popup_message(self, msg):
        alert = Qt.QMessageBox()
        alert.setText(msg)
        alert.exec_()

    def init_itk_reader(self):
        # File dialog to choose the brain image file
        dlg = Qt.QFileDialog()
        dlg.setFileMode(Qt.QFileDialog.AnyFile)
        dlg.setNameFilter("Image files (*.mha)")
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            brain_image_path = filenames[0]

            # Set up the ITK reader for the brain image
            self.reader_brain = itk.ImageFileReader[itk.Image[itk.UC, 3]].New()
            self.reader_brain.SetFileName(brain_image_path)
            self.reader_brain.Update()

    """
        Add QT controls to the control panel in the righ hand size
    """

    def add_controls(self):
        """Add a sample group box"""
        groupBox = Qt.QGroupBox(
            "3D Scalar Field Visualization"
        )  # Use a group box to group controls
        groupBox_layout = Qt.QVBoxLayout()  # lines up the controls vertically
        groupBox.setLayout(groupBox_layout)
        self.right_panel_layout.addWidget(groupBox)

        """ Add a textfield ( QLineEdit) to show the file path and the browser button """
        label = Qt.QLabel("Choose a file (e.g., vtk):")
        groupBox_layout.addWidget(label)
        hbox = Qt.QHBoxLayout()
        self.ui_file_name = Qt.QLineEdit()
        hbox.addWidget(self.ui_file_name)
        self.ui_browser_button = Qt.QPushButton("Browser")
        self.ui_browser_button.clicked.connect(self.on_file_browser_clicked)
        self.ui_browser_button.show()
        hbox.addWidget(self.ui_browser_button)
        file_widget = Qt.QWidget()
        file_widget.setLayout(hbox)
        groupBox_layout.addWidget(file_widget)

        """ Add the Open button """
        self.ui_open_button = Qt.QPushButton("Open")
        self.ui_open_button.clicked.connect(self.open_vtk_file)
        self.ui_open_button.show()
        groupBox_layout.addWidget(self.ui_open_button)

        """ Add the min, max scalar labels """
        self.ui_min_label = Qt.QLabel("Min Scalar: 0")
        self.ui_max_label = Qt.QLabel("Max Scalar: 0")
        groupBox_layout.addWidget(self.ui_min_label)
        groupBox_layout.addWidget(self.ui_max_label)

        # Add spin box for table range
        table_range_label = Qt.QLabel("Select the scalar range for color table")
        groupBox_layout.addWidget(table_range_label)
        hbox = Qt.QHBoxLayout()
        self.ui_min_range = Qt.QDoubleSpinBox()
        hbox.addWidget(self.ui_min_range)
        self.label_min_range = Qt.QLabel("Min Range")
        hbox.addWidget(self.label_min_range)
        self.ui_max_range = Qt.QDoubleSpinBox()
        hbox.addWidget(self.ui_max_range)
        self.label_max_range = Qt.QLabel("Max Range")
        hbox.addWidget(self.label_max_range)
        tablerange_hwidget = Qt.QWidget()
        tablerange_hwidget.setLayout(hbox)
        groupBox_layout.addWidget(tablerange_hwidget)

        """ Add spinbox for scalar threshold selection """
        hbox = Qt.QHBoxLayout()
        self.ui_isoSurf_checkbox = Qt.QCheckBox("Show iso-surface (select threshold)")
        hbox.addWidget(self.ui_isoSurf_checkbox)
        self.ui_isoSurf_checkbox.setChecked(False)
        self.ui_isoSurf_checkbox.toggled.connect(self.on_checkbox_change)
        self.ui_iso_threshold = Qt.QDoubleSpinBox()
        hbox.addWidget(self.ui_iso_threshold)

        # self.ui_region_growing_button = Qt.QPushButton('Apply Region Growing')
        # self.ui_region_growing_button.clicked.connect(self.apply_region_growing)
        # self.ui_region_growing_button.show()
        # groupBox_layout.addWidget(self.ui_region_growing_button)

        groupBox_layout.addWidget(Qt.QLabel("3D cut planes:"))
        """ Add a slider bar for XY slicing plane """
        hbox = Qt.QHBoxLayout()
        self.ui_xy_plane_checkbox = Qt.QCheckBox("Show XY Cut Plane")
        self.ui_xy_plane_checkbox.setChecked(False)
        self.ui_xy_plane_checkbox.toggled.connect(self.on_checkbox_change)
        hbox.addWidget(self.ui_xy_plane_checkbox)
        self.ui_zslider = Qt.QSlider(QtCore.Qt.Horizontal)
        self.ui_zslider.valueChanged.connect(self.on_zslider_change)
        hbox.addWidget(self.ui_zslider)
        self.label_zslider = Qt.QLabel()
        hbox.addWidget(self.label_zslider)
        self.label_zslider.setText("Z index:" + str(self.ui_zslider.value()))
        z_slider_widget = Qt.QWidget()
        z_slider_widget.setLayout(hbox)
        groupBox_layout.addWidget(z_slider_widget)

        """ Add the sliders for the other two cut planes """
        # ''' Add a slider bar for XZ slicing plane '''
        hbox = Qt.QHBoxLayout()
        self.ui_xz_plane_checkbox = Qt.QCheckBox("Show XZ Cut Plane")
        self.ui_xz_plane_checkbox.setChecked(False)
        self.ui_xz_plane_checkbox.toggled.connect(self.on_checkbox_change)
        hbox.addWidget(self.ui_xz_plane_checkbox)
        self.ui_yslider = Qt.QSlider(QtCore.Qt.Horizontal)
        self.ui_yslider.valueChanged.connect(self.on_yslider_change)
        hbox.addWidget(self.ui_yslider)
        self.label_yslider = Qt.QLabel()
        hbox.addWidget(self.label_yslider)
        self.label_yslider.setText("Y index:" + str(self.ui_yslider.value()))
        y_slider_widget = Qt.QWidget()
        y_slider_widget.setLayout(hbox)
        groupBox_layout.addWidget(y_slider_widget)

        # ''' Add a slider bar for YZ slicing plane '''
        hbox = Qt.QHBoxLayout()
        self.ui_yz_plane_checkbox = Qt.QCheckBox("Show YZ Cut Plane")
        self.ui_yz_plane_checkbox.setChecked(False)
        self.ui_yz_plane_checkbox.toggled.connect(self.on_checkbox_change)
        hbox.addWidget(self.ui_yz_plane_checkbox)
        self.ui_xslider = Qt.QSlider(QtCore.Qt.Horizontal)
        self.ui_xslider.valueChanged.connect(self.on_xslider_change)
        hbox.addWidget(self.ui_xslider)
        self.label_xslider = Qt.QLabel()
        hbox.addWidget(self.label_xslider)
        self.label_xslider.setText("X index:" + str(self.ui_xslider.value()))
        x_slider_widget = Qt.QWidget()
        x_slider_widget.setLayout(hbox)
        groupBox_layout.addWidget(x_slider_widget)

    def on_file_browser_clicked(self):
        dlg = Qt.QFileDialog()
        dlg.setFileMode(Qt.QFileDialog.AnyFile)
        dlg.setNameFilter("loadable files (*.vtk *.mha)")

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            self.ui_file_name.setText(filenames[0])

    def open_vtk_file(self):
        """Read and verify the vtk input file"""
        input_file_name = self.ui_file_name.text()

        if ".mha" in input_file_name:  # The input file is MetaImageData
            self.input_type = "mha"
            self.reader = vtk.vtkMetaImageReader()
            self.reader.SetFileName(input_file_name)
            self.reader.Update()
        elif ".vtk" in input_file_name:  # The input file is VTK
            self.input_type = "vtk"
            self.reader = vtk.vtkDataSetReader()
            self.reader.SetFileName(input_file_name)
            self.reader.Update()
            self.reader.GetOutput().GetPointData().SetActiveScalars("s")

        # Some initialization to remove actors that are created previously
        if hasattr(self, "isoSurf_actor"):
            self.ren.RemoveActor(self.isoSurf_actor)

        if hasattr(self, "outline"):
            self.ren.RemoveActor(self.outline)

        if hasattr(self, "xy_plane"):
            self.ren.RemoveActor(self.xy_plane)

        if hasattr(self, "xz_plane"):
            self.ren.RemoveActor(self.yz_plane)

        if hasattr(self, "yz_plane"):
            self.ren.RemoveActor(self.xz_plane)

        # You probably need to remove additional actors below...

        self.scalar_range = [
            self.reader.GetOutput().GetScalarRange()[0],
            self.reader.GetOutput().GetScalarRange()[1],
        ]
        self.ui_min_label.setText("Min Scalar:" + str(self.scalar_range[0]))
        self.ui_max_label.setText("Max Scalar:" + str(self.scalar_range[1]))

        self.ui_min_range.setMinimum(self.scalar_range[0])
        self.ui_min_range.setValue(self.scalar_range[0])
        self.ui_max_range.setValue(self.scalar_range[1])
        self.ui_max_range.setMaximum(self.scalar_range[1])

        self.ui_iso_threshold.setValue(
            (self.scalar_range[0] + self.scalar_range[1]) / 2
        )

        # Update the lookup table
        # YOU NEED TO UPDATE THE FOLLOWING RANGE BASED ON THE LOADED DATA!!!!
        self.bwLut.SetTableRange(self.scalar_range[0], self.scalar_range[1] / 2)
        # self.bwLut.SetTableRange(-1, 0)
        self.bwLut.SetSaturationRange(0, 0)
        self.bwLut.SetHueRange(0, 0)
        self.bwLut.SetValueRange(0, 1)
        self.bwLut.Build()  # effective built

        self.dim = self.reader.GetOutput().GetDimensions()

        # set the range for the iso-surface spinner
        self.ui_iso_threshold.setRange(self.scalar_range[0], self.scalar_range[1])

        # set the range for the XY cut plane range
        self.ui_zslider.setRange(0, self.dim[2] - 1)
        self.ui_yslider.setRange(0, self.dim[1] - 1)  ## Test
        self.ui_xslider.setRange(0, self.dim[0] - 1)

        # Get the data outline
        outlineData = vtk.vtkOutlineFilter()
        outlineData.SetInputConnection(self.reader.GetOutputPort())
        outlineData.Update()

        mapOutline = vtk.vtkPolyDataMapper()
        mapOutline.SetInputConnection(outlineData.GetOutputPort())

        self.outline = vtk.vtkActor()
        self.outline.SetMapper(mapOutline)
        colors = vtk.vtkNamedColors()
        self.outline.GetProperty().SetColor(colors.GetColor3d("Black"))
        self.outline.GetProperty().SetLineWidth(2.0)

        self.ren.AddActor(self.outline)
        self.ren.ResetCamera()
        self.vtkWidget.GetRenderWindow().Render()

    # def apply_region_growing(self):
    #     if hasattr(self, 'reader_brain'):
    #         seed_point = [100, 100, 100]  # Adjust the seed point based on your image dimensions
    #         lower_threshold = 100  # Adjust the lower intensity threshold
    #         upper_threshold = 200  # Adjust the upper intensity threshold

    #         # Example: Applying a simple region growing filter
    #         segmentation_filter = itk.ConnectedThresholdImageFilter[
    #             itk.Image[itk.UC, 3],
    #             itk.Image[itk.UC, 3]
    #         ].New()

    #         segmentation_filter.SetInput(self.reader_brain.GetOutput())
    #         segmentation_filter.SetSeed(seed_point)  # Set seed point
    #         segmentation_filter.SetLower(lower_threshold)  # Set lower intensity threshold
    #         segmentation_filter.SetUpper(upper_threshold)  # Set upper intensity threshold

    #         # Update the segmentation filter
    #         segmentation_filter.Update()

    #         # Get the segmented image
    #         segmented_image = segmentation_filter.GetOutput()

    #         # Add actors for visualization
    #         self.add_image_actor(self.reader_brain.GetOutput(), 'Original Image')
    #         self.add_point_actor(seed_point, 'Seed Point', color=(1, 0, 0))  # Red seed point
    #         self.update_visualization(segmented_image, 'Segmented Image')

    # def update_visualization(self, image, actor_name):
    #     # Convert the ITK image to a VTK image
    #     itk_to_vtk_filter = itk.ImageToVTKImageFilter[itk.Image[itk.UC, 3]].New()
    #     itk_to_vtk_filter.SetInput(image)
    #     itk_to_vtk_filter.Update()

    #     vtk_image = itk_to_vtk_filter.GetOutput()

    #     # Create a vtkImageActor for the image
    #     image_actor = vtk.vtkImageActor()
    #     image_actor.GetMapper().SetInputData(vtk_image)

    #     # Set display extent to match the original image
    #     image_actor.SetDisplayExtent(
    #         0, vtk_image.GetDimensions()[0] - 1,
    #         0, vtk_image.GetDimensions()[1] - 1,
    #         0, vtk_image.GetDimensions()[2] - 1
    #     )

    #     # Add the image actor to the renderer
    #     self.ren.AddActor(image_actor)

    #     # Reset the camera and render the window
    #     self.ren.ResetCamera()
    #     self.vtkWidget.GetRenderWindow().Render()

    # You can add additional actors as needed, e.g., for seed point or segmented image

    def add_point_actor(self, point, actor_name, color=(1, 1, 1)):
        # Create a vtkPoints object
        points = vtk.vtkPoints()
        points.InsertNextPoint(point)

        # Create a vtkPolyData object
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)

        # Create a vtkGlyph3D object to represent the seed point
        sphere = vtk.vtkSphereSource()
        sphere.SetRadius(5)  # Adjust the radius as needed

        glyph = vtk.vtkGlyph3D()
        glyph.SetInputData(polydata)
        glyph.SetSourceConnection(sphere.GetOutputPort())

        # Create a vtkPolyDataMapper and vtkActor for the seed point
        mapper = vtk.vtkPolyDataMapper()
        actor = vtk.vtkActor()

        mapper.SetInputConnection(glyph.GetOutputPort())
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)

        # Add the actor to the renderer
        self.ren.AddActor(actor)

        # Set actor name (optional)
        actor.SetName(actor_name)

        # Reset the camera and render the window
        self.ren.ResetCamera()
        self.vtkWidget.GetRenderWindow().Render()

        # Print information for debugging
        print(f"{actor_name}: {point}")

    def on_zslider_change(self, value):
        self.label_zslider.setText("Z index:" + str(self.ui_zslider.value()))
        current_zID = int(self.ui_zslider.value())

        if self.ui_xy_plane_checkbox.isChecked() == True:
            xy_plane_Colors = vtk.vtkImageMapToColors()
            xy_plane_Colors.SetInputConnection(self.reader.GetOutputPort())
            xy_plane_Colors.SetLookupTable(self.bwLut)
            xy_plane_Colors.Update()

            if hasattr(self, "xy_plane"):
                self.ren.RemoveActor(self.xy_plane)

            self.xy_plane = vtk.vtkImageActor()
            self.xy_plane.GetMapper().SetInputConnection(
                xy_plane_Colors.GetOutputPort()
            )
            self.xy_plane.SetDisplayExtent(
                0, self.dim[0], 0, self.dim[1], current_zID, current_zID
            )  # Z

            self.ren.AddActor(self.xy_plane)

            # Re-render the screen
            self.vtkWidget.GetRenderWindow().Render()

    def on_yslider_change(self, value):
        self.label_yslider.setText("Y index: " + str(self.ui_yslider.value()))
        current_yID = int(self.ui_yslider.value())

        if self.ui_xz_plane_checkbox.isChecked() == True:
            xz_plane_Colors = vtk.vtkImageMapToColors()
            xz_plane_Colors.SetInputConnection(self.reader.GetOutputPort())
            xz_plane_Colors.SetLookupTable(self.bwLut)
            xz_plane_Colors.Update()

            if hasattr(self, "xz_plane"):
                self.ren.RemoveActor(self.xz_plane)

            self.xz_plane = vtk.vtkImageActor()
            self.xz_plane.GetMapper().SetInputConnection(
                xz_plane_Colors.GetOutputPort()
            )
            self.xz_plane.SetDisplayExtent(
                0, self.dim[0], current_yID, current_yID, 0, self.dim[2]
            )  # Y-Z plane

            self.ren.AddActor(self.xz_plane)

            # Re-render the screen
            self.vtkWidget.GetRenderWindow().Render()

    def on_xslider_change(self, value):
        self.label_xslider.setText("X index: " + str(self.ui_xslider.value()))
        current_xID = int(self.ui_xslider.value())

        if self.ui_yz_plane_checkbox.isChecked() == True:
            yz_plane_Colors = vtk.vtkImageMapToColors()
            yz_plane_Colors.SetInputConnection(self.reader.GetOutputPort())
            yz_plane_Colors.SetLookupTable(self.bwLut)
            yz_plane_Colors.Update()

            if hasattr(self, "yz_plane"):
                self.ren.RemoveActor(self.yz_plane)

            self.yz_plane = vtk.vtkImageActor()
            self.yz_plane.GetMapper().SetInputConnection(
                yz_plane_Colors.GetOutputPort()
            )
            self.yz_plane.SetDisplayExtent(
                current_xID, current_xID, 0, self.dim[1], 0, self.dim[2]
            )  # X-Z plane

            self.ren.AddActor(self.yz_plane)

            # Re-render the screen
            self.vtkWidget.GetRenderWindow().Render()

    """ Handle the click event for the submit button  """

    def on_submit_clicked(self):
        self.show_popup_message(self.ui_textfield.text())

    """ Handle the spinbox event """

    def on_spinbox_change(self, value):
        self.label_spinbox.setText("Spin Box Value:" + str(value))

    """ Handle the checkbox button event """

    def on_checkbox_change(self):
        if self.ui_xy_plane_checkbox.isChecked() == False:
            if hasattr(self, "xy_plane"):
                self.ren.RemoveActor(self.xy_plane)
            # Re-render the screen
            self.vtkWidget.GetRenderWindow().Render()

        if self.ui_yz_plane_checkbox.isChecked() == False:
            if hasattr(self, "yz_plane"):
                self.ren.RemoveActor(self.yz_plane)
            # Re-render the screen
            self.vtkWidget.GetRenderWindow().Render()

        if self.ui_xz_plane_checkbox.isChecked() == False:
            if hasattr(self, "xz_plane"):
                self.ren.RemoveActor(self.xz_plane)
            # Re-render the screen
            self.vtkWidget.GetRenderWindow().Render()

        if self.ui_isoSurf_checkbox.isChecked() == False:
            if hasattr(self, "isoSurf_actor"):
                self.ren.RemoveActor(self.isoSurf_actor)
            # Re-render the screen
            self.vtkWidget.GetRenderWindow().Render()

        else:
            if hasattr(self, "volume"):
                self.ren.RemoveViewProp(self.volume)
            self.comp_raycasting()
            # Re-render the screen
            self.vtkWidget.GetRenderWindow().Render()


if __name__ == "__main__":
    app = Qt.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
