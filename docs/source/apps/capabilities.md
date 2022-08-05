# Capabilities

In order to offer a unified form of communication, the MarketPlace has defined a list
of typical functionalities, which we call _capabilities_, that a user might expect and an application can choose to support.
Each capability will have a name and a definition of the expected parameters and errors it can generate.

A capability is associated with an operation ID (capability and operation ID should match) and a specification of a _unique_ REST-API endpoint + HTTP method.
For instance, there can only be one capability under the `/dataset` path for the `get` method.

Capabilities are case sensitive.

## Capability types

Different types of capabilities are clustered into groups based on their purpose.
Thus, we can define applications as:

1. **Data source:** Applications for online data repositories which store generic data that can be used in different use cases. Examples of such data repositories are databases within [Materials Cloud](https://www.materialscloud.org/) and [NOMAD](https://nomad-lab.eu/).
1. **Data sink:** Applications that offer persistent data storage services.
1. **Transformation:** Applications that manipulate data. A simulation tool that generates data is an example of such an application.
1. **Front page:** Applications that have a web page.
1. **System:** Capabilities related to operability of applications.

The MarketPlace will be able to automatically infer the type of the application to the users, while recognizing the functionalities that are supported by it.
This allows the MarketPlace to use the applications in workflows that require apps with specific capabilities.
However, the capabilities are not enforced, and an application may choose to implement a mixed subset of capabilities.

Since the API is uniform, it is easy for the user to switch one application with another in case it is favourable.

## Integration levels

The information returned by the applications (payload) is not restricted, and can be varied in format and readability.
To differentiate the degree of interoperability an application enables, the following levels have been defined.

### Level 1 integration

It is the default integration level, which is simply achieved by adhering to the capabilities defined by the platform.
Any application registered to the platform must (at least) comply to Level 1 integration.

### Level 2 integration

This level tries to enforce a higher degree of interoperability between applications by making sure the data sent is understandable, both by humans and machines.

Mappings between the data and ontology concepts should exist, and the corresponding mapping be sent out with the data in the headers, e.g.:

```
{
    'x-semantic-mappings': 'MappingA'
}
```

The id can then be used to query the semantic mapping capability for the specific mapping.

## List of supported capabilities

These are the currently supported capabilities:

```{include} capability_table.md

```
