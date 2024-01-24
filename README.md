# 3D Visualization for Brain Imaging

1 Led the development of a cutting-edge brain tumor segmentation method, employing a two-step process involving binary mask generation and Connected Component analysis for accurate and   efficient results.

2 Developed a user-friendly interface with customizable parameters, facilitating intuitive control over connected component filters, tumor mask color intensity, 
  and brain volume opacity for enhanced visualization and user interaction.

3 Optimized the segmentation process through sophisticated filtering mechanisms, including size and roundness criteria, addressing complex anatomical variations, and contributing to      the improvement of automated brain tumor segmentation techniques

# EXECUTION OF THE PROJECT

Before running the files, we are required to install few dependencies.

Create new env

conda create --name newenv python=3.10

conda activate newenv

pip install vtk pyqt5 pyvista itkwidgets spyder notebook

The path is pre-declared in the file for sample.py

To run sample.py: 
Python sample.py

We need to browse files for sample2.py from data folder.

For 3d Slicing browse BRATS_HG0015T1c.mha

Python sample2.py

For 2d Slicing browse braintumor_image.mha
Python sample2.py

The path is pre-declared in the file region_highlight.py

To run region_highlight.py
Python region_highlight.py

