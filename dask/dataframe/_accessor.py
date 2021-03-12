import warnings


# Ported from pandas
# https://github.com/pandas-dev/pandas/blob/master/pandas/core/accessor.py


class CachedAccessor:
    """
    Custom property-like object (descriptor) for caching accessors.

    Parameters
    ----------
    name : str
        The namespace this will be accessed under, e.g. ``df.foo``
    accessor : cls
        The class with the extension methods. The class' __init__ method
        should expect one of a ``Series``, ``DataFrame`` or ``Index`` as
        the single argument ``data``
    """

    def __init__(self, name, accessor):
        self._name = name
        self._accessor = accessor

    def __get__(self, obj, cls):
        if obj is None:
            # we're accessing the attribute of the class, i.e., Dataset.geo
            return self._accessor
        accessor_obj = self._accessor(obj)
        # Replace the property with the accessor object. Inspired by:
        # http://www.pydanny.com/cached-property.html
        # We need to use object.__setattr__ because we overwrite __setattr__ on
        # NDFrame
        object.__setattr__(obj, self._name, accessor_obj)
        return accessor_obj


def _register_accessor(name, cls):
    def decorator(accessor):
        if hasattr(cls, name):
            warnings.warn(
                "registration of accessor {!r} under name {!r} for type "
                "{!r} is overriding a preexisting attribute with the same "
                "name.".format(accessor, name, cls),
                UserWarning,
                stacklevel=2,
            )
        setattr(cls, name, CachedAccessor(name, accessor))
        cls._accessors.add(name)
        return accessor

    return decorator


def register_dataframe_accessor(name):
    """
    Register a custom accessor on :class:`dask.dataframe.DataFrame`.

    See :func:`pandas.api.extensions.register_dataframe_accessor` for more.
    """
    from dask.dataframe import DataFrame

    return _register_accessor(name, DataFrame)


def register_series_accessor(name):
    """
    Register a custom accessor on :class:`dask.dataframe.Series`.

    See :func:`pandas.api.extensions.register_series_accessor` for more.
    """
    from dask.dataframe import Series

    return _register_accessor(name, Series)


def register_index_accessor(name):
    """
    Register a custom accessor on :class:`dask.dataframe.Index`.

    See :func:`pandas.api.extensions.register_index_accessor` for more.
    """
    from dask.dataframe import Index

    return _register_accessor(name, Index)
