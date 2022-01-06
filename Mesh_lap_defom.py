import numpy as np
import trimesh
import robust_laplacian as RL
import scipy.sparse
from utilities import *
import scipy.sparse

class lapDeform:
    def __init__(self, mesh, handle_idx,  handle_pos, boundary_idx, skip_path=False):
        self.mesh = mesh
        self.deformed_mesh = mesh.copy()

        self.handle_IDX = handle_idx
        self.handle_pos = handle_pos
        self.boundary_idx = boundary_idx

        self.skip = skip_path
        self.A = []
        self.b = []

        # Produce submesh based on input indices
        if skip_path:
            self.ring_IDX = self.boundary_idx
            self.submesh = submesh(self.mesh, self.ring_IDX, self.handle_IDX)
        else:
            self.ring_IDX = ring_points(self.mesh, self.boundary_idx)
            self.submesh = submesh(self.mesh, self.ring_IDX, self.handle_IDX)

    def deform(self):
        # First find the laplacian operator
        lap, _ = RL.point_cloud_laplacian(np.array(self.submesh.vertices))
        lap = lap.todense()

        # Then find laplacian coordinates of the submesh vertices
        d = lap @ self.submesh.vertices
        n = self.submesh.n

        # Constructing LHS of LS system
        A = np.vstack([np.hstack([lap, np.zeros([n, n]), np.zeros([n, n])]), np.hstack([np.zeros([n, n]), lap, np.zeros([n, n])]), np.hstack([np.zeros([n, n]), np.zeros([n, n]), lap])])

        for i in range(n):
            vert = self.submesh.IDX[i]
            ring = [vert]

            # Find neighbours in immediate ring. Only includes neighbours that are in the submesh.
            for idx in self.mesh.vertex_neighbors[self.submesh.IDX[i]]:
                if idx in self.submesh.IDX:
                    ring.append(idx)

            ring_degree = len(ring)  # Number of vertices in the ring
            ring_pos = self.mesh.vertices[ring]  # Positions of vertices in the ring

            # Find submesh based indices for vertices in ring
            sub_ring = []
            for IDX in ring:
                if IDX in self.submesh.IDX:
                    sub_ring.append(self.submesh.new_IDX[IDX])

            sub_ring = np.array(sub_ring)

            # Construct A matrix (eq 10 from paper)
            C = np.zeros([ring_degree * 3, 7])

            for j in range(ring_degree):
                C[j, :] = np.array([ring_pos[j, 0], 0, ring_pos[j, 2], -ring_pos[j, 1], 1, 0, 0])
                C[j + ring_degree, :] = np.array([ring_pos[j, 1], -ring_pos[j, 2], 0, ring_pos[j, 0], 0, 1, 0])
                C[j + 2 * ring_degree, :] = np.array([ring_pos[j, 2], ring_pos[j, 1], -ring_pos[j, 0], 0, 0, 0, 1])

            # Retrieve the relevant coefficients found in transformation matrix
            Cinv = np.linalg.pinv(C)
            s = Cinv[0]
            h1 = Cinv[1]
            h2 = Cinv[2]
            h3 = Cinv[3]

            # Produce transformation matrix and T(V')d term from paper
            T = np.array([[s, -h3, h2], [h3, s, -h1], [-h2, h1, s]])
            TVd = d[i] @ T

            p = np.hstack([sub_ring, sub_ring + n, sub_ring + 2 * n])

            A[i, p] += -TVd[0]
            A[i + n, p] += -TVd[1]
            A[i + 2 * n, p] += -TVd[2]

        IDX = [self.submesh.new_IDX[i] for i in self.ring_IDX]

        # Define RHS of LS equations (Ax = b)
        b = np.zeros(3 * n)

        # Add pinned ring vertices to LS equations
        for i in IDX:
            A = np.vstack([A, (np.arange(3 * n) == i), ((np.arange(3 * n)) == i + n), ((np.arange(3 * n)) == i + 2 * n)])
            b = np.hstack([b, self.submesh.vertices[i, 0], self.submesh.vertices[i, 1], self.submesh.vertices[i, 2]])

        # Add pinned handle at defined position to LS equations
        A = np.vstack([A, (np.arange(3 * n) == self.submesh.new_IDX[self.handle_IDX]),
                       ((np.arange(3 * n)) == self.submesh.new_IDX[self.handle_IDX] + n),
                       ((np.arange(3 * n)) == self.submesh.new_IDX[self.handle_IDX] + 2 * n)])

        self.A = scipy.sparse.csc_matrix(A)
        self.b = np.hstack([b, self.handle_pos[0], self.handle_pos[1], self.handle_pos[2]])

    def update(self):
        # Solve linear system
        new_positions = scipy.sparse.linalg.lsqr(self.A, self.b)[0]

        # Update positions of vertices on output mesh
        for i in range(self.submesh.n):
            self.deformed_mesh.vertices[self.submesh.IDX[i]] = np.array([[new_positions[i], new_positions[i + self.submesh.n], new_positions[i + 2 * self.submesh.n]]])

    def export_mesh(self, export_path):
        self.deformed_mesh.export(export_path)