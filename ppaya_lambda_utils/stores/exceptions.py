
class ItemNotFoundException(Exception):
    """ Raised when item not found """


class MultipleItemsFoundException(Exception):
    """ Raised when too many items were found """


class ItemAlreadyExistsException(Exception):
    """ Raised when an item already exists """
