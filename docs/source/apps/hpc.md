# HPC integration

## Interact with HPC through MarketPlace proxy using HPC gateway SDK

The HPC gateway SDK is provide for the app developers or the MarketPlace user to run the time consuming tasks over the clusters.

For details of how to use sdk to interact with HPC cluster deployed, read the section [here](../jupyter/hpc-sdk.ipynb)

The following capabilities are supported and can be called by using the SDK.

- Check the availability of system: `app.heartbeat()`
- Create a new user: `app.create_user()`. Only when user first time use the functionality.
- Create a new calculation: `app.create_job()`, the jobid will returned for further job preparation.
- Show job state (List files in job folder): `app.check_job_state(jobid=<jobid>)`, list files in remote job folder.
- Upload file: `app.upload_file(jobid=<jobid>, filename=<filename>, source_path=<local_file_path>`, upload file to remote folder from local path.
- Download file: `app.download_file(jobid=<jobid>, filename=<filename>`, download file from remote folder.
- Delete file: `app.delete_file(jobid=jobid, filename=<filename>)`, delete the file from remote folder.
- Launch job: `app.launch_job(jobid=<jobid>)`, launch/submit the job to cluster queue managed by slurm.
- Cancel the job: `app.cancel_job(jobid=jobid)`, cancel the job submitted.
