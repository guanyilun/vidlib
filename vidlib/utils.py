def filter_by_lim(values, lim, return_mask=False):
    if not return_mask:
        return values[(values > lim[0]) * (values < lim[1])]
    else:
        mask = (values > lim[0]) * (values < lim[1])
        return values[mask], mask

def c2hex(c):
    import matplotlib as mpl
    return mpl.colors.to_hex(c)
