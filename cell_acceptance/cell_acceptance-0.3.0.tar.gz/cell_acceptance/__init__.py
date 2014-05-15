from cell_acceptance.oosheet import OOSheet as S

def calc(filename, inputs, outputs):
    S().open(filename)

    for location, data in inputs.items():
        selector = S(location)
        if ':' in location:
            selector.data_array = data
        else:
            if not isinstance(data, list) and not isinstance(data, tuple):
                selector.value = data
            else:
                for row in data:
                    for column in row:
                        selector.value = column
                        selector = selector.shift_right()
                    selector = selector.shift_left(len(row))
                    selector = selector.shift_down()
    results = []
    for location in outputs:
        data = S(location).data_array
        if len(data) == 1 and len(data[0]) == 1:
            results.append(data[0][0])
        else:
            results.append(data)

    return results


