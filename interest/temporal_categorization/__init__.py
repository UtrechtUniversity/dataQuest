"""Mapping from string format descriptions to corresponding classes."""
from interest.temporal_categorization.timestamped_data \
    import (YearPeriodData, DecadePeriodData)

PERIOD_TYPES = {
    "decade": DecadePeriodData,
    "year": YearPeriodData
}
