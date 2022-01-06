import trimesh
from select_vertices import *
from Mesh_lap_defom import lapDeform
from utilities import *

# --------------------------------- Load Mesh -------------------------------- #
path = "meshes/"
# meshes = multi_load("meshes/")
mesh = trimesh.load('./meshes/dragon.ply', process=False)
# ---------------------------- Editing Parameters ---------------------------- #
handle_idx = 12080
boundary_idx = [16969, 33501, 33761, 4303, 19255, 6885]

handle_ind = handle_edit(mesh.vertices, handle_idx)
print("New handle position = ", handle_ind.final_pos)

# --------------------------- create deform object --------------------------- #
current_mesh_deform = lapDeform(mesh, handle_idx, handle_ind.final_pos, boundary_idx)
current_mesh_deform.deform()
current_mesh_deform.update()
view_model(current_mesh_deform.deformed_mesh)