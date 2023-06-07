# App dependency

MarketPlace supports the registration of one or more applications contained within another platform, such as JupyterHub-based [AiiDalab](https://aiidalab.readthedocs.io/) and [SimPhony remote](https://simphony-remote.readthedocs.io/).
This requires the registration of one main application for the platform (host), and one for each of the applications contained (resident).

- Host application:

  - Represents a platform containing resident applications.
  - Is in charge of the authentication, as it is shared among all the resident apps.
    This means that when the platform is launched, the client ID and secret used are the ones returned by the MarketPlace for this application.
  - Has a limited amount of endpoints, mainly front page/system ones.

- Resident application:

  - Represents an application in the platform of the corresponding host application.
  - Does not need any authentication information, since it is handled centrally by the platform (and thus is common to all resident applications).
  - Implements all the endpoints specific to the application in the platform.

```{toctree}
:hidden: true

aiidalab
```
