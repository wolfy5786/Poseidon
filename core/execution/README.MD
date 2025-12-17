Execution folder is where the tests are run, all tests casses returned from LLM are stored and executed here, to ease out execution two Helper classes have been provided.

The use of Auth-Helper and credential source is optional

Auth-Helper its an abstract class with multiple implementations, each implementation define a way to authenticate each request.

Credential Source: its way to fetch and manage your secret keys required to access APIs and authenticate requests