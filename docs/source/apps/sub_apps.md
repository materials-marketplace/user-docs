# Primary and dependent applications

MarketPlace supports the registration of one or more applications contained within another platform, such as JupyterHub-based [AiiDalab](https://aiidalab.readthedocs.io/) and [SimPhony remote](https://simphony-remote.readthedocs.io/).
This requires the registration of one main application for the platform (primary), and one for each of the applications contained (dependent).

- Primary application:

  - Represents a platform containing dependent applications.
  - Is in charge of the authentication, as it is shared among all the dependent apps.
    This means that when the platform is launched, the client ID and secret used are the ones returned by the MarketPlace for this application.
  - Has a limited amount of endpoints, mainly front page/system ones.

- Dependent application:

  - Represents an application in the platform of the corresponding primary application.
  - Does not need any authentication information, since it is handled centrally by the platform (and thus is common to all dependent applications).
  - Implements all the endpoints specific to the application in the platform.
