import vtkmodules.all as vtk
import random


def generate_seed(height, width):
    x = random.randint(0, width - 1)
    y = random.randint(0, height - 1)
    return x, y


def region_growing(image_data, segmented_image_data, seed_x, seed_y):
    threshold = 100
    processed = set()
    stack = [(seed_x, seed_y)]

    while stack:
        x, y = stack.pop()
        if (x, y) not in processed:
            processed.add((x, y))
            if image_data.GetScalarComponentAsDouble(x, y, 0, 0) > threshold:
                # Mark pixel in segmented image
                segmented_image_data.SetScalarComponentFromDouble(
                    x, y, 0, 0, 255
                )  # Setting pixel to white
                # Add neighboring pixels to the stack
                neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
                stack.extend(
                    (nx, ny)
                    for nx, ny in neighbors
                    if 0 <= nx < image_data.GetDimensions()[0]
                    and 0 <= ny < image_data.GetDimensions()[1]
                )


def main():
    reader = vtk.vtkPNGReader()
    reader.SetFileName(
        "/Users/sachin_veera/Desktop/brain-tumor-segmentation-master-2/data/m_vm1125.t1.png"
    )  # Update the file path
    reader.Update()

    original_image_data = reader.GetOutput()

    # Create a blank image for the segmented output
    segmented_image_data = vtk.vtkImageData()
    segmented_image_data.SetDimensions(original_image_data.GetDimensions())
    segmented_image_data.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
    seed_x, seed_y = 173, 158
    region_growing(original_image_data, segmented_image_data, seed_x, seed_y)

    # Visualization setup
    render_window = vtk.vtkRenderWindow()
    renderer = vtk.vtkRenderer()
    render_window.AddRenderer(renderer)
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    # Create an image actor for the segmented image
    segmented_actor = vtk.vtkImageActor()
    segmented_actor.GetMapper().SetInputData(segmented_image_data)

    renderer.AddActor(segmented_actor)
    renderer.ResetCamera()
    render_window.Render()
    render_window_interactor.Start()


if __name__ == "__main__":
    main()
