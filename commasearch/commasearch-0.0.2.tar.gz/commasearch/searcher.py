def search(db, search_url:str):
    'Search for table once you have indexed it.'

    # Index the file first.
    if search_url not in db.indices:
        raise ValueError('The table must be indexed before you can search it. (%s)' % search_url)

    # Then look up its indices.
    indices = db.indices[search_url]

    # Then look for things that have high overlap.
    for i in indices:
        search_values = db.values(i)[search_url]
        overlaps = [(len(search_values.intersection(search_values)), result_url) for (result_url, result_values) in db.values(i).items()]
        for overlap_count, url in sorted(overlaps)[:5]:
            yield i, url, overlap_count

