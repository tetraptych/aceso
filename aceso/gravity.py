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

    Wan, Neng & Zou, Bin & Sternberg, Troy. (2012). A 3-step floating catchment area method for
    analyzing spatial access to health services. International Journal of Geographical Information
    Science. 26. 1073-1089. 10.1080/13658816.2011.624987.
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
        - Standard gravity models
        - Two-Step Floating Catchment Area (2SFCA) models
        - Enhanced 2SFCA (E2SFCA) models
        - Three-Step FCA (3SFCA) models
        - Modified 2SFCA (M2SFCA) models
        - Kernel Density 2SFCA (KD2SFCA) models
    """

    def __init__(
        self, decay_function, decay_params={}, huff_normalization=False, suboptimality_exponent=1.0
    ):
        """"Initialize a gravitational model of spatial accessibility.

        Parameters
        ----------
        decay_function : callable or str
            If str, the name of a decay function in the ``decay`` module.
            Some available names are 'uniform', 'raised_cosine', and 'gaussian_decay'.

            If callable, a vectorized numpy function returning demand dropoffs by distance.
        decay_params : mapping
            Parameter: value mapping for each argument of the specified decay function.
            These parameters are bound to the decay function to create a one-argument callable.
        huff_normalization: bool
            Indicates whether to normalize demand through the use of Huff-like interaction
            probabilities.

            Used in 3SFCA to curtail demand over-estimation.
        suboptimality_exponent: float
            Used in M2SFCA to indicate the extent to account for network suboptimality in access.
            This parameter allows for the differentiation between two scenarios:
                1. Three demand locations each at a distance of 1.0 mile from the sole provider;
                2. Three demand locations each at a distance of 2.0 miles from the sole provider.

            Values greater than 1.0 for this parameter will result in accessibility scores
            whose weighted average is less than the overall supply.
        """
        self.decay_function = self._bind_decay_function_parameters(decay_function, decay_params)
        self.huff_normalization = huff_normalization
        self.suboptimality_exponent = suboptimality_exponent

    @staticmethod
    def _bind_decay_function_parameters(decay_function, decay_params):
        """Bind the given parameters for the decay function.

        Returns
        -------
        callable
            A one-argument callable that accepts one-dimensional numpy arrays.
        """
        # If a name was passed, get the callable corresponding to that name.
        if isinstance(decay_function, str):
            decay_function = decay.get_decay_function(decay_function)

        if sys.version_info[0] >= 3:
            missing_params = {
                k for k in list(inspect.signature(decay_function).parameters)[1:]
                if (k not in decay_params)
            }
            valid_params = {
                k: v for k, v in decay_params.items()
                if k in inspect.signature(decay_function).parameters
            }
        elif sys.version_info[0] == 2:
            missing_params = {
                k for k in inspect.getargspec(decay_function).args[1:]
                if (k not in decay_params)
            }
            valid_params = {
                k: v for k, v in decay_params.items()
                if k in inspect.getargspec(decay_function).args
            }

        # If any required parameters are missing, raise an error.
        if missing_params:
            raise ValueError(
                'Parameter(s) "{}" must be specified!'.format(', '.join(missing_params)))

        # Warn users if a parameter was passed that the specified function does not accept.
        for param in decay_params:
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
        inverse_demands = np.reciprocal(demand_potentials)
        inverse_demands[np.isinf(inverse_demands)] = 0.0
        access_ratio_matrix = supply_array * inverse_demands
        access_ratio_matrix = access_ratio_matrix * np.power(
            self.decay_function(distance_matrix),
            self.suboptimality_exponent
        )
        if self.huff_normalization:
            access_ratio_matrix *= self._calculate_interaction_probabilities(distance_matrix)
        return np.nansum(access_ratio_matrix, axis=1)

    def _calculate_demand_potentials(self, distance_matrix, demand_array):
        """Calculate the demand potential at each input location.

        Returns
        -------
        array
            An array of demand at each supply location.
        """
        demand_matrix = demand_array.reshape(-1, 1) * self.decay_function(distance_matrix)
        if self.huff_normalization:
            demand_matrix *= self._calculate_interaction_probabilities(distance_matrix)
        return np.nansum(demand_matrix, axis=0)

    def _calculate_interaction_probabilities(self, distance_matrix):
        """Calculate the demand potential at each input location.

        Parameters
        ----------
        distance_matrix : np.ndarray(float)
            A matrix whose entry in row i, column j is the distance between demand point i
            and supply point j.

        Returns
        -------
        array
            A 2D-array of the interaction probabilities between each demand point and supply point.
        """
        # FIXME: Use alternative decay function to capture the Huff model of spatial interaction.
        weights = np.power(distance_matrix, -1)
        # FIXME: Handle the case of 0 distance more intelligently.
        weights[np.isinf(weights)] = 10**8
        return weights / np.nansum(weights, axis=1)[:, np.newaxis]


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
        super(TwoStepFCA, self).__init__(decay_function='uniform', decay_params={'scale': radius})


class ThreeStepFCA(GravityModel):
    """Represents an instance of the Three-Step Floating Catchment Area (3SFCA) model.

    In 3SFCA, the presence of nearby options influences the amount of demand pressure each demand
    location places on other supply locations. A demand location with many nearby options will not
    exert the same demand on faraway supply locations as a demand location at the same distance
    that has no nearby alternatives.

    This model is designed to account for this observation and reduce the demand over-estimation
    that may take place with ordinary 2SFCA.

    References
    ----------
    Wan, Neng & Zou, Bin & Sternberg, Troy. (2012). A 3-step floating catchment area method for
    analyzing spatial access to health services. International Journal of Geographical Information
    Science. 26. 1073-1089. 10.1080/13658816.2011.624987.
    """

    def __init__(self, decay_function, decay_params):
        """"Initialize a gravitational model of spatial accessibility using Huff-like normalization.

        Parameters
        ----------
        decay_function : callable or str
            If str, the name of a decay function in the ``decay`` module.
            Some available names are 'uniform', 'raised_cosine', and 'gaussian_decay'.

            If callable, a vectorized numpy function returning demand dropoffs by distance.
        decay_params : mapping
            Parameter: value mapping for each argument of the specified decay function.
            These parameters are bound to the decay function to create a one-argument callable.
        """
        super(ThreeStepFCA, self).__init__(
            decay_function=decay_function,
            decay_params=decay_params,
            huff_normalization=True,
        )
