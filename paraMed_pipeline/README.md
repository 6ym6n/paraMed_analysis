# paraMed_pipeline

This package contains a refactored data pipeline for scraping,
cleaning and matching product information from the
**parapharma.ma** and **universparadiscount.ma** websites.  The
original repository had multiple standalone scripts for scraping,
post‑processing and matching; this new structure unifies the logic into
reusable modules, centralises configuration and cleaning and provides
an orchestration entry point.

## Architecture

The pipeline is organised into a few key modules:

| Module | Purpose |
|---|---|
| `config.py` | Centralises constants such as the embedding model name, similarity threshold, default category lists and brand lists. |
| `pipeline/scrapers/parapharma.py` | Scrapes paginated category pages from parapharma.ma.  Returns raw product dictionaries using a consistent schema. |
| `pipeline/scrapers/univers.py` | Scrapes paginated category pages from universparadiscount.ma. |
| `pipeline/utils/cleaning.py` | Provides functions to normalise product names, extract brands and sizes, parse prices, normalise availability codes and map categories. |
| `pipeline/utils/db.py` | Handles MongoDB connection using environment variables for configuration. |
| `pipeline/utils/category_mapping.py` | Contains a mapping of raw category strings to high‑level categories used in analysis. |
| `pipeline/transform.py` | Merges raw documents from both scrapers, applies cleaning and feature extraction (brand, size, category mapping, discount calculation) and deduplicates products by site and cleaned name. |
| `pipeline/matcher.py` | Implements an embedding‑based product matcher.  Groups Univers products by (brand, size), encodes products using a sentence transformer and finds matches above a similarity threshold. |
| `pipeline/main.py` | Orchestrates the pipeline: scrape sites, clean and merge data, write to MongoDB and perform matching.  Running `python -m paraMed_pipeline.pipeline.main` executes the full pipeline. |

## Usage

1. **Install dependencies** (e.g. inside a virtual environment):

   ```sh
   pip install -r requirements.txt
   ```

2. **Set up MongoDB**: ensure a MongoDB server is running and accessible.
   You can configure the connection via environment variables:

   - `MONGO_URI`: connection URI (default `mongodb://localhost:27017`)
   - `MONGO_DB_NAME`: database name (default `paraMedProducts`)

   Create a `.env` file in the project root to store these values.

3. **Run the pipeline**:

   ```sh
   python -m paraMed_pipeline.pipeline.main
   ```

   The script will scrape all categories defined in `config.PARAPHARMA_CATEGORIES` and `config.UNIVERS_CATEGORIES`, merge and clean the results, write them to the `para_univer_merged` collection and perform product matching.  Matches are written to the `matches` collection.

4. **Customisation**: you can limit pagination for testing by setting the `max_pages` argument when calling `run_pipeline` in your own script.  You can also extend the brand list or category mapping by modifying `config.py` and `utils/category_mapping.py`.

## Extending the pipeline

The modular design makes it straightforward to add new sources or
processing steps.  For a new e‑commerce site, implement a new scraper
module in `pipeline/scrapers`, returning raw dictionaries with the same
field names.  Then update `main.py` to call your scraper and include
its documents in the merge step.

To add new feature extraction (e.g. computing additional attributes
from product names), extend the `utils/cleaning.py` module and update
`transform.merge_and_clean` accordingly.

## License

This refactored pipeline is provided as an example and may require
adaptation for production use.  See the original repository for
licensing information on the underlying data and code.