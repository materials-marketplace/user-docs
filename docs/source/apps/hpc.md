# HPC integration

## Interact with HPC through MarketPlace proxy using SDK

This repository provide SDK for using or integrating the HPC gateway app into other MarketPlace app.

First, create a `hpc` instance with:

python
```
from marketplace_hpc import HpcGatewayApp

hpc = HpcGatewayApp(
    client_id=<app_id>, # This is the HPC gateway app.
    access_token=<your_access_token>,
)
```

The following capabilities are supported and can be called by using the SDK.

- Check the availability of system: `hpc.heartbeat()`
- Create a new calculation: `hpc.new_job()`, the resourceid will returned to list files on remote workdir, upload/downlead/delete files and the launch/delete job.
- Upload file: `hpc.upload_file(resourceid=<resourceid>, source_path=<file_local_path>`.
- Download file: `hpc.download_file(resourceid=<resourceid>, filename=<filename>`.
- Delete file: `hpc.delete_file(resourceid=resourceid, filename=<filename>)`
- List jobs (only CSCS deployment): `hpc.list_jobs()`.
- Launch job: `hpc.run_job(resourceid=<resourceid>)`
- Delete job: `hpc.delete_job(resourceid=resourceid)`

You can find example at https://github.com/materials-marketplace/hpc-sdk/blob/main/hpc_api.ipynb

### Materials Cloud (CSCS) deployment

The correspond HPC-Gateway app is https://www.materials-marketplace.eu/app/hpc-app (ID: `5fd66c68-50e9-474a-b55d-148777ae3efd`) deployed on production server.

Since it deployed using Materials Cloud CSCS resources provided by EPFL, it is only for test purpose and MarketPlace users who what to use it need to contact Jusong Yu @unkpcz (jusong.yu@epfl.ch) to add your MarketPlace account to the whitelist and then register your account by:

```
curl -X POST \
   -H "Authorization:Bearer <put_your_token_here>" \
   'https://mp-hpc.herokuapp.com/user'
```

### IWM deployment

The correspond HPC-Gateway app is [HPC gateway (broker)](https://staging.materials-marketplace.eu/app/hpc-gateway-broker) (ID: `dc67d85e-7945-49fa-bf85-3159a8358f85`) deployed on staging server since RPC broker server needed.


## Development and run locally for testing

- Create a virtual environment, activate it and install the dependencies.
- `pip install -U ".[dev]"`
- Run `python app.py` to start the development server.
- Navigate to http://localhost:5005/. The app will automatically reload if you change any of the source files.

## Registry the app to MarketPlace

https://materials-marketplace.readthedocs.io/en/latest/apps/registration.html

## How to deploy app to heroku (for Materials Cloud deployment)

Set all the ENV variables in heroku dashbooard (https://devcenter.heroku.com/articles/config-vars). Check `cscs.env.template` for all variables needed.

Install the Heroku CLI
Download and install the Heroku CLI.

If you haven't already, log in to your Heroku account and follow the prompts to create a new SSH public key.

```
$ heroku login --interactive
```

Clone the repository
Use Git to clone mp-hpc's source code to your local machine.

```
$ heroku git:clone -a mp-hpc
$ cd mp-hpc
```

or in the repo add heroku remote repo to push

```
$ git remote add heroku https://git.heroku.com/mp-hpc.git
```

Deploy your changes
Make some changes to the code you just cloned and deploy them to Heroku using Git.

```
$ git add .
$ git commit -am "make it better"
$ git push heroku master
```

## How to deploy the infracstructures and run hpc-app on IWM HPC.

### Firecrest deployment
The firecrest on MarketPlace firecrest server need to be started.
Go to `firecrest/` folder of `hpc-fire` server and run `docker-compose up -d`.
The changes of firecrest deployment that needed on MarketPlace HPC can be found on https://github.com/unkcpz/firecrest/pull/1

### HPC-GW app and rpc-broker server
[.deploy/docker-compose.yml]
Then need to start the hpc-gateway-app to communicate to the firecrest.
Since the hpc-app is in the private internal network, we use MarketPlace broker to talk to public network.
Go to the hpc-app repo and run `python app.py` (WIP: using docker-compose to start so the dependencies are not needed).
This will start the hpc-app and the `rpc-brocker` (should be optinonal for the hpc-app accessable deployed on public network).