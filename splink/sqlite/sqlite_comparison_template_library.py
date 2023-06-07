import warnings

from .comparison_template_library import *  # noqa: F403

warnings.warn(
    "Importing directly from `splink.sqlite.sqlite_comparison_template_library` "
    "is deprecated and will be removed in Splink v4. "
    "Please import from `splink.sqlite.comparison_template_library` going forward.",
    DeprecationWarning,
    stacklevel=2,
)
