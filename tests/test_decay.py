"""Test methods contained in the ``decay.py`` submodule."""
import numpy as np

import pytest

from context import aceso


@pytest.mark.filterwarnings('ignore::RuntimeWarning')
class TestDecayFunctions():
    """Test decay functions used to model decreasing demand with increased distance."""

    def setup(self):
        """Initialize an array of distances for use in the test cases."""
        self.distance_array = np.asarray([[0.0, 1.0, 100.0, np.nan, float('inf')]])

    def test_parabolic_decay(self):
        output = aceso.decay.parabolic_decay(self.distance_array, scale=2.0)
        expected = np.array([[1.0, 0.75, 0., np.nan, 0.0]])
        np.testing.assert_equal(output, expected)

    def test_gaussian_decay(self):
        output = aceso.decay.gaussian_decay(self.distance_array, sigma=2.0)
        expected = np.array([[1.0, 0.88249690258459546, 0.0, np.nan, 0.0]])
        np.testing.assert_equal(output, expected)

    def test_raised_cosine(self):
        output = aceso.decay.raised_cosine_decay(self.distance_array, scale=2.0)
        expected = np.array([[1.0, 0.5, 0.0, np.nan, 0.0]])
        np.testing.assert_equal(output, expected)

    def test_uniform_decay(self):
        output = aceso.decay.uniform_decay(self.distance_array, scale=2.0)
        # FIXME: Leave np.nan unchanged.
        expected = np.array([[1.0, 1.0, 0.0, 0.0, 0.0]])
        np.testing.assert_equal(output, expected)
