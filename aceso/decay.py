"""A suite of decay functions to simulate demand dropoff as distance increases."""
# TODO: Add the standard gravity decay function d**(-beta)
import math

import numpy as np


def parabolic_decay(distance_array, scale):
    """
    Transform a measurement array using the Epanechnikov (parabolic) kernel.

    Some sample values (in multiples of scale):
        measurement   |   decay value
        -----------------------------
            0.0       |         1.0 (full value)
            0.25      |         0.9375
            0.5       |         0.75
            0.75      |         0.4375
            1.0       |         0.0
    """
    return np.maximum(
        (scale**2 - distance_array**2) / scale**2,
        np.zeros(shape=distance_array.shape)
    )


def gaussian_decay(distance_array, sigma):
    """
    Transform a measurement array using a normal (Gaussian) distribution.

    Some sample values (in multiples of sigma):
        measurement   |   decay value
        -----------------------------
            0.0       |         1.0 (full value)
            0.7582    |         0.75
            1.0       |         0.60647
            1.17      |         0.5
            2.0       |         0.13531
            2.14597   |         0.1
    """
    return np.exp(-(distance_array**2 / (2.0 * sigma**2)))


def raised_cosine_decay(distance_array, scale):
    """
    Transform a measurement array using a raised cosine distribution.

    Some sample values (in multiples of the scale parameter):
        measurement   |   decay value
        -----------------------------
            0.0       |         1.0 (full value)
            0.25      |         0.853553
            0.5       |         0.5
            0.75      |         0.146447
            1.0       |         0.0
    """
    masked_array = np.clip(a=distance_array, a_min=0.0, a_max=scale)
    return (1.0 + np.cos((masked_array / scale) * math.pi)) / 2.0


def uniform_decay(distance_array, scale):
    """
    Transform a measurement array using a uniform distribution.

    The output is 1 below the scale parameter and 0 above it.

    Using this decay function results in the standard 2SFCA method.
    """
    return (distance_array <= scale).astype(np.float64)


def get_decay_function(name):
    """Return the decay function with the given name."""
    return NAME_TO_FUNCTION_MAP[name.lower()]


NAME_TO_FUNCTION_MAP = {
    'uniform': uniform_decay,
    'raised_cosine': raised_cosine_decay,
    'gaussian': gaussian_decay,
    'parabolic': parabolic_decay,
    'epanechnikov': parabolic_decay
}
