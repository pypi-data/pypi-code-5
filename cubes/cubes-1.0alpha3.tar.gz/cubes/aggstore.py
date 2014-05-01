# -*- coding: utf-8 -*-

from .browser import AggregationBrowser

class CachingBrowser(AggregationBrowser):
    def __init__(self, cube, store=None, locale=None, **options):
        super(CachedBrowser, self).__init__(cube, store, locale, **options)

        self.browser = browser

    def provide_aggregate(self, cell, aggregates, drilldown, split, order,
                          page, page_size, **options):

        if split:
            raise NotImplementedError("Split is not implemented in cache")

        # TODO: respect aggregates, order, page and pagesize
        cells = self.store.aggregate(browser, cell, drilldown)

        result = AggregationResult(cell=cell, aggregates=aggregates)
        result.cells = cells

    def cell_key(self, cell):
        """Returns a string key representing the `cell`."""

        # Key:
        # cut strings ordered by dimension and paths


class AggregateStore(AggregationBrowser):

    def __init__(self, cube, store=None, locale=None, metadata=None, **options):
        super(CachingAggregationBrowser, self).__init__(cube, store, locale, metadata, **options)

        # TODO check store or cube metadata if cache is enabled
        # TODO reuse an app-level cache with every browser instance

        this.cache = AggregationCache()

    def aggregate(self, cell=None, measures=None, aggregates=None, drilldown=None, split=None,
                  attributes=None, page=None, page_size=None, order=None,
                  include_summary=None, include_cell_count=None,
                  **options):

        """
        For first implementation...
        Cache is available for querying if all conditions true:
            1) time dimension is present in cube
            2) drilldown includes a time drilldown item
            3) cell has a single time cut in it
            4) No order= clause or page= or page_size=
            5) split= does not contain an *unelapsed* time cut
            6) both include_summary and include_cell_count must be off (i could support include_cell_count but don't want to right now)

            In future, we can check additivity of the desired aggregates/measures
            and exploit partial cache entries even if 2) is not true.

        Procedure:
        - check all the preconditions
        - assemble the cache key: cube, cell_minus_time_cut, sorted_aggregates, sorted_measures, sorted_drilldown, split 
        - find all time cut subkeys in the cache entry
        - determine the best "carveouts" from the cut's time span given the available subkeys. larger subkey spans
          trump smaller spans if they overlap. No need to optimize this. If a cache entry's start of span is earlier
          than cut's start of span, that's ok -- "closest to cut's start wins". For now, don't try to use small cache
          entries for small discontiguous spans inside the cut span. Look for a subkey whose span start is <= the cut's
          span start, then look for subkeys that are contiguous with that chosen subkey, disregarding all others.
        - for each time cut subkey found, fetch and validate results, slice that timespan from the cut's time range
        - with remaining timespan, slice into largest possible elapsed span and smallest possible unelapsed span
        - run aggregate() for the remaining elapsed and unelapsed timespan, in sequence OR run it all together
          and splice the results into those for elapsed span and those for unelapsed span (better)
        - persist the result set for the remaining elapsed timespan in the cache. would help to consolidate
          contiguous cache entries?
        - concatenate the results, left (earliest span) to right (latest). boy do i hate include_summary!
        """
        # prepare the measures.
        # prepare the aggregates.
        # prepare the drilldown and split.
        # attributes?
        # page, page_size, order

        # cache entry's key is
        # (cube, aggregates_sorted, measures_sorted, drilldown_sorted, split

