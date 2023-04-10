__version__ = "0.1.1"

import hashlib

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import LinearSegmentedColormap
from scipy.signal import convolve2d


def _normalize(arr: npt.NDArray[np.int_]):
    """normalize values of a numpy array to be between 0 and 255"""
    min_val = arr.min()
    max_val = arr.max()
    # check if the range is zero
    if max_val - min_val == 0:
        arr_norm = arr.copy()
    else:
        # normalize the values to be between 0 and 255
        arr_norm = (arr - min_val) * (255.0 / (max_val - min_val))
    return arr_norm


def _animate_history(
    hist: npt.NDArray[np.bool_ | np.int_],
    normeach: bool,
    cmap: str | LinearSegmentedColormap,
):
    """creates a matplotlib animation to show generation history"""

    def animate(i: int):
        plt.clf()

        # plot the i-th slice along axis 0
        if cmap == "gray":
            plt.imshow(_tile_symmetrically(hist[i]), cmap=cmap)
        else:
            plt.imshow(
                _tile_symmetrically(_normalize(hist[i])) if normeach else hist[i],
                cmap=cmap,
                vmin=0.0,
                vmax=255.0,
            )

        # title and labels
        plt.title(f"slice {i}")
        # plt.xlabel('X')
        # plt.ylabel('Y')
        plt.axis("off")

    # create the animation object
    anim = FuncAnimation(plt.gcf(), animate, frames=hist.shape[0], interval=50)

    # show the animation
    plt.show()


def _tile_symmetrically(arr: npt.NDArray[np.int_]):
    """tile a 2d numpy array symmetrically by flipping it"""
    return np.concatenate(
        (
            np.concatenate((np.flip(arr, axis=1), arr), axis=1),
            np.concatenate(
                (np.flip(np.flip(arr, axis=1), axis=0), np.flip(arr, axis=0)), axis=1
            ),
        ),
        axis=0,
    )


class Golident:
    def __init__(
        self,
        seed_string: str,
        size: int = 64,
        iterations: int = 320,
        num_colors: int = 5,
    ):
        # convert seed_string to hash, then to int seed
        hash_object = hashlib.sha256(seed_string.encode())
        hash_value = int.from_bytes(hash_object.digest(), byteorder="big")

        # expose friendly seed info
        self.seed_string = seed_string
        self.seed_hash = hash_object.hexdigest()

        # use seed for numpy rng
        rng = np.random.default_rng(hash_value)

        # generate random board
        self.board = rng.choice([True, False], size=(size, size))

        # generate random cmap
        colors = rng.random((num_colors, 3))
        positions = np.linspace(0, 1, num_colors)
        self.cmap = LinearSegmentedColormap.from_list(
            "my_cmap", list(zip(positions, colors)), N=256
        )

        # iterations scale with size
        self.iterations = iterations
        # initialize history
        self.history = np.empty(
            (self.iterations + 1, self.board.shape[0], self.board.shape[1]),
            dtype=np.bool_,
        )
        # initialize identicon array
        self.identicon_array = np.empty((size, size))
        # run simulation to populate history
        self._run(self.iterations)
        # calculate new ident_array
        self._calc_ident()

    def _run(self, iterations: int) -> None:
        """run a simulation for Conway's Game of Life and return all iterations"""

        def step(board: npt.NDArray[np.bool_]) -> npt.NDArray[np.bool_]:
            neighbors = (
                convolve2d(board, np.ones((3, 3)), mode="same", boundary="wrap") - board
            )
            birth_rule = (board == 0) & (np.isin(neighbors, [3]))
            survival_rule = (board == 1) & (np.isin(neighbors, [2, 3]))
            return birth_rule | survival_rule

        # 3d integer boolean array that tracks state of each cell for each step in sim
        self.history = np.empty(
            (iterations + 1, self.board.shape[0], self.board.shape[1]), dtype=np.bool_
        )
        self.history[0] = self.board

        # avoid modifying self.board
        layout = self.board.copy()

        # step and fill in history for each iteration
        for i in range(1, iterations + 1):
            layout = step(layout)
            self.history[i] = layout

        # 3d integer nparray that tracks last index along axis 0 where true
        self.ihistory = np.zeros_like(self.history, dtype=int)
        for i in range(self.history.shape[0]):
            # for each slice along axis 0, if cell value is True, use index
            # else, take previous or 0
            self.ihistory[i] = np.where(
                self.history[i], i, self.ihistory[i - 1] if i > 0 else 0
            )

    def _calc_ident(self):
        """calculates the identicon array with with normalized grayscale luminosity"""
        # use the final iteration for the indenticon
        last = self.ihistory[-1]

        # normalize values to 0-255
        norm = _normalize(last)

        # symmetrically tile vertically and horizontally; new array is 4x
        tiled = _tile_symmetrically(norm)
        self.identicon_array = tiled

    def show_identicon(self):
        """use matplotlib.pyplot to draw identicon"""
        plt.axis("off")
        plt.imshow(self.identicon_array, cmap=self.cmap, vmin=0.0, vmax=255.0)
        plt.show()

    def show_history(self):
        """use matplotlib.pyplot to animate identicon color history"""
        _animate_history(self.ihistory, normeach=True, cmap=self.cmap)

    def show_alt_history(self):
        """use matplotlib.pyplot to animate identicon color history differently"""
        _animate_history(_normalize(self.ihistory), normeach=False, cmap=self.cmap)

    def show_sim(self):
        """use matplotlib.pyplot to animate simulation history"""
        _animate_history(self.history, normeach=False, cmap="gray")

    def save_identicon(self, path: str):
        """save identicon image to specified path"""
        plt.imsave(path, self.identicon_array, cmap=self.cmap, vmin=0.0, vmax=255.0)
