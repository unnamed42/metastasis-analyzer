from skimage.measure import marching_cubes_lewiner as marching_cubes

def makeMesh(image, thres, step):
    #trans = image.transpose(2, 1, 0)
    verts, faces, _, _ = marching_cubes(image, thres, step_size=step,
                                        allow_degenerate=True)
    return verts, faces

def _plotly3d(verts, faces):
    from plotly.offline import init_notebook_mode, iplot
    from plotly.figure_factory import create_trisurf

    init_notebook_mode()

    x, y, z = zip(*verts)
    cmap = ["rgb(236, 236, 212)", "rgb(236, 236, 212)"]
    fig = create_trisurf(x=x, y=y, z=z,
                         plot_edges=False, simplices=faces,
                         backgroundcolor="rgb(64, 64, 64)",
                         colormap=cmap,
                         title="Interactive Visualization")
    iplot(fig)

def plotly3d(images, thres=350, step_size=2):
    verts, faces = makeMesh(images, thres, step_size)
    _plotly3d(verts, faces)

def _matplot3d(verts, faces):
    from matplotlib import pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    x, y, z = zip(*verts)
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection="3d")

    mesh = Poly3DCollection(verts[faces], linewidth=0.05, alpha=1)
    mesh.set_facecolor([1, 1, 0.9])
    ax.add_collection3d(mesh)

    ax.set_xlim(0, max(x))
    ax.set_ylim(0, max(y))
    ax.set_zlim(0, max(z))
    ax.set_facecolor((0.7, 0.7, 0.7))
    plt.show()

def matplot3d(images, thres=-300, step_size=1):
    verts, faces = makeMesh(images, thres, step_size)
    _matplot3d(verts, faces)
