Usage
=====

The diverse and ever-growing ecosystem of measures of potential spatial accessibility is too complicated for this short document or its inexpert author to do justice. Each model has strengths, peculiarities, and shortcomings. Aceso was designed to make it easy to experiment with different choices of model and model parameters.

Accordingly, this documentation assumes that users have already selected a model from the menagerie when they arrive at Aceso. That said, experience shows that the default gravity model with raised cosine decay is often a good starting point.

Model initialization
--------------------

All model classes should specify a decay function that operates on 1d-arrays and parameters for that function in dictionary format. Certain functions can be specified by name, including ``'uniform'``, ``'raised_cosine'``, ``'gaussian'``, and ``'parabolic'``. Other functions can be passed directly as callables.

For concreteness: 2SFCA uses the uniform decay function. Enhanced Two-Step Floating Catchment Area (E2SFCA) models would define a piecewise function over different distance ranges.

Where relevant, decay parameters should be measured in the same units as the travel impedances (kilometers, miles, minutes, etc.).

Model usage
-----------

All model classes support the method ``calculate_accessibility_scores(distance_matrix, demand_array, supply_array)``. Here, the entry of ``distance_matrix`` in row i and column j corresponds to the distance (or time) between demand location i and supply location j. Both ``demand_array`` and ``supply_array`` will default to arrays of ones of the correct length if not provided explicitly.

In one standard use pattern, demand locations are stored in a `GeoPandas <http://geopandas.org/>`_ GeoDataFrame object. Access scores can then be calculated and added to the dataframe as a new column: ::

    model = aceso.TwoStepFCA(radius=60.0)
    gdf['access_score'] = model.calculate_accessibility_scores(
        distance_matrix=distance_matrix,
        demand_array=gdf['population'].values
    )

Notes
-----
* Aceso is agnostic about the source of ``distance_matrix`` and does not currently implement any methods to calculate it. Great-circle distance can be calculated efficiently using the `haversine formula <https://en.wikipedia.org/wiki/Haversine_formula>`_, which has a very fast implementation in the `cHaversine <https://github.com/doublemap/cHaversine>`_ package. Retrieving matrices of driving times is more complicated and may involve calls to external routing APIs.
* See :ref:`Contributing` if there are other models you'd like to see supported.
