# pages/__init__.py
from .summary import layout as summary_layout, register_callbacks as summary_callbacks
from .missing import layout as missing_layout, register_callbacks as missing_callbacks
from .univariate import layout as univariate_layout, register_callbacks as univariate_callbacks
from .bivariate import layout as bivariate_layout, register_callbacks as bivariate_callbacks
from .timeseries import layout as timeseries_layout, register_callbacks as timeseries_callbacks
from .conclusions import layout as conclusions_layout, register_callbacks as conclusions_callbacks

__all__ = [
    'summary_layout', 'summary_callbacks',
    'missing_layout', 'missing_callbacks', 
    'univariate_layout', 'univariate_callbacks',
    'bivariate_layout', 'bivariate_callbacks',
    'timeseries_layout', 'timeseries_callbacks',
    'conclusions_layout', 'conclusions_callbacks'
]