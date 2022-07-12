# MarketPlace API

To declare which capabilities are supported by your application, a REST-API that complies with the MarketPlace specification must be set for your application.
The API should be expressed using the [OpenAPI specification](https://www.openapis.org/) standard and be sent to the MarketPlace platform upon [registration](registration.md).

You can browse the official specification with redoc <a href="api.html" target="_blank">here</a>.
The complete specification is hosted publicly on [GitHub](https://github.com/materials-marketplace/standard-app-api).

## OpenAPI specification

In this section we explain some of the non-trivial parts of the specification.

### Info

This top level section includes all the metadata related to the application, such as the name (`title`), description (`description`) or version (`version`).

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
