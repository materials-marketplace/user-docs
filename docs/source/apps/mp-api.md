# Standard API

The MarketPlace defines a standard API through which the registered application can be communicated with and monitored via the platform.
The API defines a set of of endpoints or _capabilities_ to specify actions which MarketPlace applications may perform.
An application provider may choose to support any subset of these capabilities, depending on the relevant functionalities.

The complete specification is hosted publicly on GitHub:<br>
[https://github.com/materials-marketplace/standard-app-api](https://github.com/materials-marketplace/standard-app-api).<br>
You can also browse the official specification with Redoc <a href="api.html" target="_blank">here</a>.

Below is more information about the API specification. Read [here](./capabilities) more about app capabilities. Once completed, the application can be registered to the platform, as explained in [this page](registration.md) page.

## OpenAPI specification

The application API is compliant with the [OpenAPI specification](https://www.openapis.org/) standard.
In the following sub-sections we explain some of the possibly non-trivial parts of the specification.

### Info

This top level section includes all the metadata related to the application, such as the name (`title`), description (`description`) or versions. The version of the application corresponds to the `version` field, while `x-api-version` indicates which version of the standard app API the application conforms to.

#### Products

The list of products in `x-products` represents the different options a user can purchase in the platform.
In order to use an application, a product must be purchased.

- `name` corresponds to the name of the product.
- `description` corresponds to the description of the product.
- `product-id` uniquely identifies each product.
  It should be omitted/empty for new product registrations.

### Servers

This list includes the `url` values by which your application might be reach

### Paths

The different `paths` in the application, with their HTTP Methods and the corresponding capability (`operationId`), as well as parameters and responses.
Refer to the snippets in the next section to see examples of the different fields.
