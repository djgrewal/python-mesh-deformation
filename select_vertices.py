import numpy as np

from matplotlib.widgets import LassoSelector
from matplotlib.path import Path
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

class handle_edit:
    def __init__(self, vertices, handle):
        self.final_pos = [0,0,0]
        self.x = 0
        self.y = 0
        self.z = 0
        handle_pos = vertices[handle]
        self.fig, ax = plt.subplots()
        ax.scatter(vertices[:, 0], vertices[:, 1], s=2)
        pt = ax.plot([handle_pos[0]], [handle_pos[1]], 'ro')
        plt.subplots_adjust(left=0.25, bottom=0.25)
        axcolor = 'lightgoldenrodyellow'
        ax.margins(x=0)
        axx = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)
        x_slider = Slider(
        ax=axx,
        label='left/right',
        valmin=min(vertices[:, 0]),
        valmax=max(vertices[:, 0]),
        valinit=handle_pos[0])


        axy = plt.axes([0.1, 0.25, 0.0225, 0.63], facecolor=axcolor)
        y_slider = Slider(
            ax=axy,
            label='up/down',
            valmin=min(vertices[:, 1]),
            valmax=max(vertices[:, 1]),
            valinit=handle_pos[1],
            orientation="vertical"
        )

        def update(val):
            pt[0].set_data(x_slider.val, y_slider.val)
            self.fig.canvas.draw_idle()

        x_slider.on_changed(update)
        y_slider.on_changed(update)

        resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
        button = Button(resetax, 'Accept', color=axcolor, hovercolor='0.975')

        def reset(event):
            self.x = x_slider.val
            self.y = y_slider.val
            plt.close()

        button.on_clicked(reset)
        plt.show()

        self.final_pos[0:2] = [self.x, self.y]
        self.fig, ax = plt.subplots()
        ax.scatter(vertices[:, 1], vertices[:, 2], s=2)
        pt = ax.plot(self.y, handle_pos[2], 'ro')
        plt.subplots_adjust(left=0.25, bottom=0.25)
        axcolor = 'lightgoldenrodyellow'
        ax.margins(x=0)

        axz = plt.axes([0.1, 0.25, 0.0225, 0.63], facecolor=axcolor)
        z_slider = Slider(
            ax=axz,
            label='up/down',
            valmin=min(vertices[:, 2]),
            valmax=max(vertices[:, 2]),
            valinit=handle_pos[2],
            orientation="vertical"
        )

        def update2(val):
            pt[0].set_data(self.y, z_slider.val)
            self.fig.canvas.draw_idle()

        z_slider.on_changed(update2)

        resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
        button = Button(resetax, 'Accept', color=axcolor, hovercolor='0.975')

        def reset(event):
            self.z = z_slider.val
            plt.close()

        button.on_clicked(reset)
        plt.show()

        self.final_pos[2] = self.z