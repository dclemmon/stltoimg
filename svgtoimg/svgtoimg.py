import trimesh
import numpy as np
import click

from PIL import Image, ImageChops


def load_mesh(filename):
    """Load a mesh from a file

    Args:
        filename (str): file name and path for the mesh

    Returns:
        mesh: loaded mesh object
    """
    mesh = trimesh.load_mesh(filename)
    return mesh


def slice_mesh(mesh, steps=256, bottom_offset=0, top_offset=0):
    """Slice a mesh into n steps

    Args:
        mesh (mesh): mesh object to slice
        steps (int): number of steps to slice
        bottom_offset: Floor offset
        top_offset: Celing offset

    Returns:
        np.array: array of secitons or slices of the mesh
    """
    print("Mesh size:\n" + str(mesh.bounds))
    z_extents = mesh.bounds[:,2]
    if (bottom_offset + top_offset) < z_extents.max():
        z_extents = np.array([z_extents[0] + bottom_offset, z_extents[1] - top_offset])
    step = (z_extents[1] - z_extents[0]) / steps
    z_levels = np.arange(*z_extents, step=step)

    # Slice the mesh
    sections = mesh.section_multiplane(
        plane_origin=mesh.bounds[0],
        plane_normal=[0,0,1],
        heights=z_levels,
    )
    # Remove anything that is falsy
    sections = [x for x in sections if x]
    return sections


def replace_color(img, value, target=255):
    """Replace a target color/value with another. Useful for removing solid
       black backgrounds, and replacing them with white

    Args:
        img (PIL.Image): The image object to replace a color in
        value (int): the replacement value
        target (int, optional): The target value. Defaults to 255.

    Returns:
        PIL.Image: The new, updated Image
    """
    im = img.convert("RGBA")
    data = np.array(im)
    red, green, blue, alpha = data.T
    white_areas = (red==target) & (green==target) & (blue==target)
    data[..., :-1][white_areas.T] = (value, value, value)
    return Image.fromarray(data)


def create_depthmap(mesh, slices):
    """Create the depthmap from the mesh

    Args:
        mesh (mesh): The mesh to slice
        slices (int): The number of slices to create

    Returns:
        PIL.Image: The Image
    """
    mesh.rezero()  # rezero the mesh because the slices are already
    pitch = mesh.extents[:2].max() / 2048  # Get only the x and y extents
    origin = mesh.bounds[:,:2][0] - (pitch * 2)
    span = np.vstack((mesh.bounds[:,:2], origin)).ptp(axis=0)
    resolution = np.ceil(span /pitch) + 2
    images = (s.rasterize(resolution=resolution, origin=origin, pitch=pitch) for s in slices)
    layers = [replace_color(img, i) for i, img in enumerate(images)]
    depthmap = layers[0]
    for layer in layers:
        depthmap = ImageChops.lighter(depthmap, layer)
    return depthmap


@click.command
@click.option("--bottom-offset", default=0, help="Raise the bottom floor by offset")
@click.option("--top-offset", default=0, help="Lower the celing by offset")
@click.option("--steps", default=255, help="Number of steps/values to slice the stl into")
@click.option("--output", help="Output file name", type=click.Path())
@click.option("--show", is_flag=True, help="Show the created depthmap")
@click.option("--replace", type=(int, int), help="Replace a target value with another.")
@click.argument("mesh")
def main(bottom_offset, top_offset, steps, output, show, replace, mesh):
    click.echo("Loading mesh...")
    stl = load_mesh(mesh)
    click.echo("Slicing mesh...")
    slices = slice_mesh(stl, steps=steps, bottom_offset=bottom_offset, top_offset=top_offset)
    click.echo("Creating DepthMap...")
    depthmap = create_depthmap(stl, slices)
    if output is None:
        output = mesh.split('/')[-1].split('.')[0]
    if replace:
        depthmap = replace_color(depthmap, replace[0], replace[1])
    if show:
        depthmap.show()
    else:
        depthmap.save(f"{output}.png")


if __name__ == '__main__':
    main()