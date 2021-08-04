**********
Change Log
**********

0.0.10
=====
- Add dynamodb paginator helper function
- Update aws-lambda-powertools to 1.18.1

0.0.9
=====
- Use aws-lambda-powertools JSON encoder to handle decimals.

0.0.8
=====
- Add helper function for invoking lambda functions.
- Add helper function for deleting a dynamodb item.

0.0.7
=====
- Inputs handle nested data classes and graphql structures

0.0.6
=====
- Parsing of enums, dates and datetimes between GraphQL, Python and DynamoDB

0.0.5
=====
- More flexible type-checking for graphql_payload_to_input kwargs
- Convert floats to decimals when integrating with DynamoDB

0.0.4
=====
- Add input data classes for dynamodb for put_item and update_item

0.0.3
=====
- Add DynamoDBStore to reduce some boilerplate code in lambda functions
- Add pytest coverage
- Update aws-lambda-powertools to 1.14.0

0.0.2
=====
- Update aws-lambda-powertools to 1.13.0

0.0.1
=====
- Initial commit of utilities currently in existing services.
