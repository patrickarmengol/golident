import hashlib
import math
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from matplotlib.colors import LinearSegmentedColormap
from scipy.signal import convolve2d


def get_seed(seed_string: str) -> bytes:
    return hashlib.sha256(seed_string.encode()).digest()


def init_board(hash_length: int, seed: bytes):
    dim_x = int(math.sqrt(hash_length))
    dim_y = dim_x

    hash_bytes = seed
    hash_bits = np.empty(len(hash_bytes) * 8, dtype=np.bool_)
    for i, b in enumerate(hash_bytes):
        for j in range(8):
            hash_bits[i * 8 + j] = (b & (1 << (7 - j))) != 0
    return hash_bits.reshape((dim_x, dim_y))


def step(board: npt.NDArray[np.bool_]) -> npt.NDArray[np.bool_]:
    neighbors = count_neighbors(board)
    birth_rule = (board == 0) & (np.isin(neighbors, [3]))
    survival_rule = (board == 1) & (np.isin(neighbors, [2, 3]))
    return birth_rule | survival_rule


def run(board: npt.NDArray[np.bool_], iterations: int):
    # NOTE: more efficient to just store the last iteration where True in a 2d array than track history
    history = np.zeros((iterations + 1, board.shape[0], board.shape[1]), dtype=np.bool_)
    history[0] = board
    for i in range(1, iterations + 1):
        board = step(board)
        history[i] = board
    return history


def count_neighbors(board: npt.NDArray[np.bool_]) -> npt.NDArray[np.bool_]:
    return convolve2d(board, np.ones((3, 3)), mode="same", boundary="wrap") - board


def draw_hist(history: npt.NDArray[np.bool_]) -> None:
    ax = plt.figure().add_subplot(projection='3d')
    ax.voxels(history)
    plt.show()


def draw_ident(ident: npt.NDArray[np.bool_], cmap: LinearSegmentedColormap):
    plt.imshow(ident, cmap=cmap)
    plt.axis('off')
    plt.show()


def ident_array(history: npt.NDArray[np.bool_]) -> npt.NDArray[np.bool_]:
    # flat = np.sum(history, axis=0)
    flat = history.shape[0] - 1 - np.flip(np.argmax(np.flip(history, axis=0), axis=0), axis=0)
    print(flat)
    min_val = flat.min()
    max_val = flat.max()
    # min_val = 0
    # max_val = history.shape[0] - 1
    norm = (flat - min_val) * (255.0 / (max_val - min_val))
    tiled = np.concatenate(
        (
            np.concatenate((np.flip(norm, axis=1), norm), axis=1),
            np.concatenate((np.flip(norm, axis=0), np.flip(np.flip(norm, axis=0), axis=1)), axis=1),
        ),
        axis=0,
    )
    return tiled


def main():
    # Convert a string to a hash value
    my_string = "Hello, world!"
    hash_object = hashlib.sha256(my_string.encode())
    hash_value = int.from_bytes(hash_object.digest(), byteorder='big')

    # Use the hash value as a seed
    rng = np.random.default_rng(hash_value)

    # Generate a random 16x16 NumPy array
    board = rng.choice([True, False], size=(16, 16))

    # generate cmap
    num_colors = 5
    colors = rng.random((num_colors, 3))
    positions = np.linspace(0, 1, num_colors)
    my_cmap = LinearSegmentedColormap.from_list('my_cmap', list(zip(positions, colors)), N=256)

    history = run(board, 50)
    # print(history)
    ident = ident_array(history)
    # draw_ident(ident, 'viridis')
    draw_ident(ident, my_cmap)


if __name__ == "__main__":
    main()
