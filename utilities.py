import numpy as np
import trimesh
import os
import networkx as nx
import scipy.sparse
import scipy as sp
import pyrender as py


def multi_load(path):
    # Load multiple meshes at once
    all_model_paths = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    print(all_model_paths)
    return [trimesh.load(i, process=False) for i in all_model_paths]


def model_to_pyrender(t_mesh):
    return py.Mesh.from_trimesh(t_mesh)


def view_model(mesh):
    # Function to view models using pyrender
    mesh.visual.vertex_colors = (np.random.rand(),np.random.rand(),np.random.rand())
    try:
        scene = py.Scene(ambient_light=0.7)
        scene.add(mesh)
        py.Viewer(scene, use_raymond_lighting=True)
    except:
        conv_mesh = model_to_pyrender(mesh)
        scene = py.Scene(ambient_light=0.7)
        scene.add(conv_mesh)
        py.Viewer(scene, use_raymond_lighting=True)


def ring_points(mesh, ROI_IDX):
    # Function to fully define a region of interest given a small number of points about the ROI
    edges = mesh.edges_unique
    length = mesh.edges_unique_length
    g = nx.Graph()

    for edge, L in zip(edges, length):
        g.add_edge(*edge, length=L)

    overall_path = []
    for i in range(len(ROI_IDX)):
        if i == len(ROI_IDX) - 1:
            path = nx.shortest_path(g, source=ROI_IDX[i], target=ROI_IDX[0], weight='length')

        else:
            path = nx.shortest_path(g, source=ROI_IDX[i], target=ROI_IDX[i + 1], weight='length')

        overall_path.append(path[0:-1])

    overall_path = [item for sublist in overall_path for item in sublist]

    return overall_path


class submesh:
    # Class to find a submesh given the ROI and handle indices
    def __init__(self, mesh, ring_IDX, handle_IDX):
        self.mesh = mesh
        self.ring_IDX = ring_IDX
        self.handle_IDX = handle_IDX
        graph = nx.Graph()

        for i in range(len(mesh.vertices)):
            graph.add_node(i, pos=mesh.vertices[i])

        for j in range(len(mesh.edges_unique)):
            graph.add_edge(*mesh.edges_unique[j])

        graph.remove_nodes_from(ring_IDX)

        new_verts = list(nx.node_connected_component(graph, handle_IDX))
        new_verts.extend(ring_IDX)

        self.IDX = new_verts
        self.vertices = mesh.vertices[new_verts]
        self.n = len(new_verts)

        # Dictionary to switch between mesh indices and submesh indices
        self.new_IDX = {}
        for i in range(len(self.IDX)):
            self.new_IDX[self.IDX[i]] = i