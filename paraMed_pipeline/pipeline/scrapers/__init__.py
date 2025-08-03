"""
Scraper subpackage.

Exports the `parapharma` and `univers` scraper modules for convenient
import.  For example::

    from paraMed_pipeline.pipeline.scrapers import parapharma
    products = parapharma.scrape_all(...)
"""

from . import parapharma  # noqa: F401
from . import univers  # noqa: F401

__all__ = ["parapharma", "univers"]