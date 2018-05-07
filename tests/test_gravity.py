"""Test methods contained in the ``gravity.py`` submodule."""
import warnings

import numpy as np

import pytest

from context import aceso


@pytest.mark.filterwarnings('ignore::RuntimeWarning')
class TestGravityModel():
    """Test methods related to calculations of spatial accessibility."""

    def setup(self):
        """Initialize a distance matrix to use in the tests."""
        self.distance_matrix = np.array([
            [5.0, 5.0],
            [10., 0.0],
            [15., 15.]
        ])

    def test_init_str(self):
        """Test initialization when passed a string as the decay function."""
        aceso.gravity.GravityModel(
            decay_function='gaussian',
            decay_params={'sigma': 1.0}
        )

    def test_init_callable(self):
        """Test initialization when passed a callable as the decay function."""
        aceso.gravity.GravityModel(
            decay_function=aceso.decay.gaussian_decay,
            decay_params={'sigma': 1.0}
        )

    def test_init_missing_parameters(self):
        """Test initialization raises an ValueError when a required parameter is missing."""
        with pytest.raises(ValueError):
            aceso.gravity.GravityModel(decay_function=aceso.decay.gaussian_decay)

    def test_init_extra_parameters(self):
        """Test initialization raises a warning when extra arguments are passed."""
        with warnings.catch_warnings(record=True) as w:
            aceso.gravity.GravityModel(
                decay_function=aceso.decay.gaussian_decay,
                decay_params={'sigma': 1.0, 'extra_param': 1.0}
            )
            assert 'extra_param' in str(w[-1].message)

    def test_calculate_demand_potentials(self):
        """Test that _calculate_demand_potentials returns the expected value."""
        model = aceso.gravity.TwoStepFCA(radius=6.0)
        output = model._calculate_demand_potentials(
            distance_matrix=self.distance_matrix,
            demand_array=np.ones(self.distance_matrix.shape[0])
        )
        # The first supply location is accessible by one demand location,
        # whereas the second supply location is accessible by two.
        expected = np.array([1.0, 2.0])
        assert (output == expected).all()

    def test_calculate_accessibility_scores(self):
        """Test calculate_accessibility_scores for the sample distance matrix."""
        model = aceso.gravity.TwoStepFCA(radius=6.0)
        output = model.calculate_accessibility_scores(self.distance_matrix)
        expected = np.array([
            [1.5, 0.5, 0.0]
        ])
        assert (output == expected).all()
