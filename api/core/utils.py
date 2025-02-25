from itertools import groupby


def group_bike_positions(bikes):
    return {
        num: list(group)
        for num, group in groupby(
            sorted(bikes, key=lambda b: b.number), key=lambda b: b.number
        )
    }
