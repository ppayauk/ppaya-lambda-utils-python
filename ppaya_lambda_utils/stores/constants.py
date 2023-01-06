from datetime import date, datetime, timezone


# When calling to_update_item_kwargs using these values for an input field will
# update the database field to null.
NULL_STRING: str = ''
NULL_DATE: date = date(1, 1, 1)
NULL_DATETIME: datetime = datetime(1, 1, 1, tzinfo=timezone.utc)
