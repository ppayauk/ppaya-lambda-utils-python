
def normalise_key(val):
    """
    Normalise a string key to be case and white space insensitive.

    eg "Some  NaMe" > "somename"
    """
    return val.replace(' ', '').lower()
