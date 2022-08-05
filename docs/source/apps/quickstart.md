# Quickstart

The MarketPlace enables users to register their own applications onto the platform so that these are purchasable and accessible by other users.
This section provides a brief overview on the registration process and usage of MarketPlace applications.

1. **Setting up the MarketPlace interface layer.** The MarketPlace defines a standard application API that dictates the way your application can be communicated with via the MarketPlace. A preliminary step is therefore to set up a corresponding interface layer for your application. This entails the identification of the [capabilities](./capabilities) your application should support. A good starting point is the [get-started app](https://github.com/materials-marketplace/get-started-app).<br><br>

1. **Application registration.** Registering an application on the platform means telling the MarketPlace how to reach your application and the capabilities you have decided to implement. Check the [registration](./registration) page for a detailed description of the process.

   - **Firewall-protected applications.** In case the application is firewall-protected, the MarketPlace provides a built-in message broker to enable the commination in that case. Learn [here](./message_broker) more about it.
   - **App dependency.** Some applications require other applications in order to run. Read [here](./sub_apps.md) more about such cases.<br><br>

1. **Interacting with the application.** Apart from the swagger viewer presented in the application registration, the Marketplace also offers a Python library that can be used to communicate with registered applications. More information is available [here](../../jupyter/sdk).<br><br>

1. **Interacting with users.** Supporting resources related to applications, such as technical tutorials and scientific explanations, can be found and added in the [MarketPlace forum](https://forum.materials-marketplace.eu/). It is the recommended space for sharing more detailed information and interacting with potentials customers of your application.<br><br>

1. **Updating your application.** Read [here](./update.md) how to update an already existing application.<br><br>

1. **Get support.** See [here](../support.md) how to get support in case you encounter issues related to the above or have ideas or comments you would like to share with us.
