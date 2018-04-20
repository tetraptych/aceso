"""
Methods to calculate gravity-based measures of potential spatial accessibility.

These measures assign accessibility scores to demand locations based on their proximity to supply
locations. The main method used here is a gravitational model using non-standard decay functions.

References:
    Luo, W. and Qi, Y. (2009) An enhanced two-step floating catchment area (E2SFCA) method for
    measuring spatial accessibility to primary care physicians. Health and Place 15, 11001107.

    Luo, W. and Wang, F. (2003) Measures of spatial accessibility to health care in a GIS
    environment: synthesis and a case study in the Chicago region. Environment and Planning B:
    Planning and Design 30, 865884.

    Wang, F. (2012) Measurement, optimization, and impact of health care accessibility:
    a methodological review. Annals of the Association of American Geographers 102, 11041112.
"""
import inspect
import functools
import warnings
import sys

import numpy as np

from aceso import decay


class GravityModel(object):
    """Represents an instance of a gravitational model of spatial interaction.

    Different choices of decay function lead to the following models:
        - Standard gravity model
        - Two-Step Floating Catchment (2SFCA) model
        - Enhanced 2SFCA (E2SFCA) models
        - Kernel Density 2SFCA (KD2SFCA) models
    """

    def __init__(self, decay_function, **params):
        """"Initialize a gravitational model of spatial accessibility.

        Parameters
        ----------
        decay_function : callable or str
            If str, the name of a decay function in the ``decay`` module.
            Some available names are 'uniform', 'raised_cosine', and 'gaussian_decay'.

            If callable, a vectorized numpy function returning demand dropoffs by distance.
        kwargs :
            Parameter=value mapping for each argument of the specified decay function.
            These parameters are bound to the decay function to create a one-argument callable.
        """
        self.decay_function = self._bind_decay_function_parameters(decay_function, **params)

    @staticmethod
    def _bind_decay_function_parameters(decay_function, **params):
        """Bind the given parameters for the decay function.

        Returns
        -------
        callable
            A one-argument callable that accepts one-dimensional numpy arrays.
        """
        # If a name was passed, get the callable corresponding to that name.
        if isinstance(decay_function, str):
            decay_function = decay.get_decay_function(decay_function)

        passed_params = dict(**params)
        if sys.version_info[0] >= 3:
            missing_params = {
                k for k in list(inspect.signature(decay_function).parameters)[1:]
                if (k not in passed_params)
            }
            valid_params = {
                k: v for k, v in passed_params.items()
                if k in inspect.signature(decay_function).parameters
            }
        elif sys.version_info[0] == 2:
            missing_params = {
                k for k in inspect.getargspec(decay_function).args[1:]
                if (k not in passed_params)
            }
            valid_params = {
                k: v for k, v in passed_params.items()
                if k in inspect.getargspec(decay_function).args
            }

        # If any required parameters are missing, raise an error.
        if missing_params:
            raise ValueError(
                'Parameter(s) "{}" must be specified!'.format(', '.join(missing_params)))

        # Warn users if a parameter was passed that the specified function does not accept.
        for param in passed_params:
            if param not in valid_params:
                warnings.warn('Invalid parameter {param} was passed to {func}!'.format(
                    param=param,
                    func=decay_function
                ))
        # If any valid parameters are present, bind their values.
        if valid_params:
            decay_function = functools.partial(decay_function, **valid_params)

        return decay_function

    def calculate_accessibility_scores(
        self,
        distance_matrix,
        demand_array=None,
        supply_array=None
    ):
        """Calculate accessibility scores from a 2D distance matrix.

        Parameters
        ----------
        distance_matrix : np.ndarray(float)
            A matrix whose entry in row i, column j is the distance between demand point i
            and supply point j.
        demand_array : np.array(float) or None
            A one-dimensional array containing demand multipliers for each demand location.
            The length of the array must match the number of rows in distance_matrix.
        supply_array : np.array(float) or None
            A one-dimensional array containing supply multipliers for each supply location.
            The length of the array must match the number of columns in distance_matrix.

        Returns
        -------
        array
            An array of access scores at each demand location.
        """
        if demand_array is None:
            demand_array = np.ones(distance_matrix.shape[0])
        if supply_array is None:
            supply_array = np.ones(distance_matrix.shape[1])

        demand_potentials = self._calculate_demand_potentials(
            distance_matrix=distance_matrix,
            demand_array=demand_array,
        )

        access_by_point = np.zeros(distance_matrix.shape[0])
        for point_index, _ in enumerate(access_by_point):
            matrix = self.decay_function(distance_matrix[point_index, :])
            matrix *= 1.0 / demand_potentials
            matrix[matrix == np.inf] = 0.0
            access_by_point[point_index] = np.nansum(matrix)

        return access_by_point

    def _calculate_demand_potentials(self, distance_matrix, demand_array):
        """Calculate the demand potential at each input location.

        Returns
        -------
        array
            An array of demand at each supply location.
        """
        demand_by_location = np.zeros(distance_matrix.shape[1])
        for location_index, _ in enumerate(demand_by_location):
            matrix = demand_array * self.decay_function(distance_matrix[:, location_index])
            matrix[matrix == np.inf] = 0.0
            demand_by_location[location_index] = np.nansum(matrix)

        return demand_by_location


class TwoStepFCA(GravityModel):
    """Represents an instance of the standard Two-Step Floating Catchment Area (2SFCA) model."""

    def __init__(self, radius):
        """Initialize a 2SFCA model with the specified radius.

        Parameters
        ----------
        radius : float
            The radius of each floating catchment.
            Pairs of points further than this distance apart are deemed mutually inaccessible.
            Points within this radius contribute the full demand amount (with no decay).
        """
        super(TwoStepFCA, self).__init__(decay_function='uniform', scale=radius)
