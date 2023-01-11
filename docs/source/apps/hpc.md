# HPC integration

## Interact with HPC through MarketPlace proxy using HPC gateway SDK

The HPC gateway SDK is provided for the app developers or the MarketPlace users to run the time consuming tasks over the computational clusters.

For details of how to use SDK to interact with HPC cluster deployed, read the section [here](../jupyter/hpc-sdk.ipynb)

The following methods are supported by the SDK to interact with cluster over MarketPlace proxy.

- Check the availability of system: `app.heartbeat()`
- Create a new user: `app.create_user()`. Only when user first time use the functionality.
- Create a new calculation: `app.create_job()`, the jobid will returned for further job preparation.
- Show job state (List files in job folder): `app.check_job_state(jobid=<jobid>)`, list files in remote job folder.
- Upload file: `app.upload_file(jobid=<jobid>, filename=<filename>, source_path=<local_file_path>`, upload file to remote folder from local path.
- Download file: `app.download_file(jobid=<jobid>, filename=<filename>`, download file from remote folder.
- Delete file: `app.delete_file(jobid=jobid, filename=<filename>)`, delete the file from remote folder.
- Launch job: `app.launch_job(jobid=<jobid>)`, launch/submit the job to cluster queue managed by slurm.
- Cancel the job: `app.cancel_job(jobid=jobid)`, cancel the job submitted.

## The architecture of user folder

The first time a user needs to call the `app.create_user()` function to create a user in the HPC gateway app's database and create a folder on the remote cluster to store calculations. 
The remote user folder is named based on the string of the user's Marketplace Email before the `@` symbol, with all non-letter characters converted to underscores. 
For example, the email materials `marketplace@gmail.com` would have a remote folder name of `materials_marketplace`. 
Each calculation creates an independent folder within the user's folder on the remote cluster.

For security considerations, the `app.create_job()` method is used to create a slurm job script named `run.sh`, with the new_transformation parameter. 
The script contains information for the calculation that is read from the `new_transformation` parameter.
Once the script is created, it cannot be modified. 
The calculation is run inside a container specified by the image key, using Singularity. 
The calculation folder is bind-mounted to the container and the calculation is run from inside the container. 
This prevents other users or calculations from maliciously exposing the contents, as the bind mount command is fixed in the job script and only the current folder is visible inside the container.
