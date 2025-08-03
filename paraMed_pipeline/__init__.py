"""
paraMed_pipeline
================

This package contains a refactored pipeline for scraping, cleaning and
matching product data from the parapharma.ma and universparadiscount.ma
websites.  The top‑level modules are organised as follows:

* :mod:`config` – configuration constants used throughout the pipeline.
* :mod:`pipeline.scrapers` – site‑specific scrapers that produce raw
  product dictionaries.
* :mod:`pipeline.utils` – shared utilities for database access,
  cleaning and category mapping.
* :mod:`pipeline.transform` – functions to merge and normalise raw
  documents into a unified schema.
* :mod:`pipeline.matcher` – embedding‑based product matching engine.
* :mod:`pipeline.main` – orchestration entry point for running the
  entire pipeline.

The package can be executed as a script to run the full pipeline::

    python -m paraMed_pipeline.pipeline.main
"""

from . import config  # re-export config at package level

__all__ = ["config"]