# Implementation of Use Case 4 into the MarketPlace framework

This documentation explains how the workflow to simulate ceramic injection moulding for medical applications, using Aspherix, Lammps and MoldFlow, is incorporated within the MarketPlace. In detail, this manual provides an overview on most of the function having been created in this Use Case. This manual should serve as a detailed explanation on how to onboard your very own software in the MarketPlace.

Everything is organized within one folder and we will slowly go through each folder and file therein.

- [Folder] simulation_controller
- [Folder] static
- .gitmodules
- app.py
- docker-compose.yml
- Dockerfile
- openAPI.yml
- prepare_deployment.sh
- aspherix_no_license_mpich314.def

## Create a singularity container

To run Aspherix or Lammps on the HPC resources an singularity container is required.
Therefore, we use an singularity definition file. For the first version of the 
HPC App that is doing the resource management in the background Mpich 3.1.4 was
required. Below the definition file for Aspherix is shown. Basically the container
is an Ubuntu 20.04 system with Mpich 3.1.4 and Aspherix 5.4.1 installed without
any license information. (The license is provided by the running case.)

```
Bootstrap: library
From: ubuntu:20.04
Stage: build

%files
    ./Installer-Aspherix_Linux_5.4.1 /opt
    ./AspherixInstallScript_5.4.1.sh /opt

%post
    # from the example
    NOW=`date`
    echo "export NOW=\"${NOW}\"" >> $SINGULARITY_ENVIRONMENT

    # Install mpich
    echo "Installing required packages..."
    apt-get update && apt-get install -y wget git bash gcc gfortran g++ make file bzip2

    echo "Install Mpich"
    wget -q http://www.mpich.org/static/downloads/3.1.4/mpich-3.1.4.tar.gz
    tar xf mpich-3.1.4.tar.gz
    cd mpich-3.1.4
    ./configure --enable-fast=all,O3 --prefix=/usr
    make -j$(nproc)
    make install
    ldconfig

    # run the installer
    apt-get update && apt-get install -y libxkbcommon0 libx11-6 libx11-xcb1 libfreetype6 libdbus-1-3 libfontconfig1 libgomp1
    cd /opt
    ldd Installer-Aspherix_Linux_5.4.1
    # create dummy license file to trick the installer
    touch /opt/dummy.lic
    /opt/AspherixInstallScript_5.4.1.sh -l /opt/dummy.lic -d /opt/DCS-Computing/Aspherix-5.4.1/ -P
    # remove any license file
    rm /opt/DCS-Computing/Aspherix-5.4.1/share/aspherix/*.lic
    # clean system
    rm /opt/AspherixInstallScript_5.4.1.sh /opt/Installer-Aspherix_Linux_5.4.1
    
%runscript
    echo "Container was created $NOW"
    echo "Arguments received: $*"
    exec echo "$@"

```

Once the Singularity definition file has all you need, you can create a container
```bash
  $ sudo singularity build aspherix_no_license_mpich314.sif aspherix_no_license_mpich314.def
```

This container can be run anywhere with a valid Singularity installation.

## simulation controller

Now we are working on the folder "simulation_controller" which contains several files that provide the function to create, start and stop a simulation as well as retrieving the simulation results. 

Let us have a look at the following files that are all found in the folder "simulation_controller"
- \_\_init\_\_.py
- config.py
- aspherix_files_creation.py
- create_input_files.py
- simulation_manager.py
- simulation_base.py
- simulation_hpc.py
- (simulation_local.py) - just for local development and testing


### \_\_init\_\_.py

The file "\_\_init\_\_.py" is an empty file and its only purpose is that python allows to include all function via the regular 
package syntax as libraries. This means in all files, we can include classes and function of other files with simple commands. Usually, python has no problem to import a whole directory. But when it comes to importing a class from a file in a directory, this will raise an exception. But having such a "\_\_init\_\_.py" file allows to use the following notation

```python
from directory.filename import classname
```

when having a class "classname" in a file "filename" within the directoy "directory".


### config.py

In this file, we have defined two classes with names "SimulationStatus" and "SimulationConfig" and follows with the definition for the simulation states. Here, we define 6 different kinds of states that are
- created
- running
- completed
- stopped
- downloaded
- error

the class structure looks as follow
```python
import logging
from enum import Enum
class SimulationStatus(Enum):
    CREATED = 1
    INPROGRESS = 2
    COMPLETED = 3
    STOPPED = 4
    DOWNLOADED = 5
    ERROR = 6
```
By writing "Enum" into the bracket, this class in heriting from the Enum class which is a built-in class from python. This allows to use a more natural syntax to ask the script whether the simulation has been created or whether it is running. In fact, we can apply the following notation
```python
state = SimulationStatus.CREATED # which is equal to "CREAETD"
# and then ask for that state by
if state == SimulationStatus.CREATED:
    print('simulation has been created')
```
which is a readable syntax to ask for the state of a simulation. The logging module at the beginning of the snippet 
is a python in-built library that simplifies to write log files in which error messages are written to. This allows for example to write error messages

```python
logging.error("This is my error message")
```
or info messages
```python
logging.info("This is my info message")
```

It follows the simulation configuration
```python
class SimulationConfig:
    def __init__(self, request_obj: dict):
        err_msg = f"Error creating simulation: {str(request_obj)}. "
        self.configuration: int = int(request_obj.get("configuration", 1))
        self.radius1: float = float(request_obj.get("radius1", 0.004))
        self.radius2: float = float(request_obj.get("radius2", 0.003))
        if self.radius1 <= 0 or self.radius2 <= 0:
            err_msg += "Sphere radii must be positive."
            logging.error(err_msg)
            raise ValueError(err_msg)

        self.period: float = float(request_obj.get("period", 1.0))
        if self.period <= 0:
            err_msg += "Mixer rotation period must be positive."
            logging.error(err_msg)
            raise ValueError(err_msg)
        self.nRotation: int = int(request_obj.get("nRotation", 1))
        if self.nRotation < 1:
            err_msg += "Number of mixer rotations must be at least 1."
            logging.error(err_msg)
            raise ValueError(err_msg)
        self.creation_time = time.time()
```
This is a class that contains only an init method. This is the function that is
called whenever an instant of the SimulationConfig class is created. Basically,
this function receives the input parameters that are made available for the Use 
Case tutorial. These were
- Radius of particle type "1" (m) 
- Radius of particle type "2" (m) 
- Period of one mixer rotation (s)
- Number of rotations (-)

At the beginning, each of the keys from this dictionary is called and in the 
case that this key has not been defined, a default is being returned. For 
example the code line
```python
self.configuration: int = request_obj.get("configuration", 1)
```
asks if there is a key with the name "configuration" in the dictionary "request_obj".
If the key is present, its value is returned (that is the value that the user 
has provided in the MarketPlace interface - to be explained later). If the key
has not been defined, we use the default value of "1". This value for the 
configuration is mapped to an integer and stored in the variable "self.configuration"
to make it available within the instant of the SimulationConfig object. 

The same procedure is done for the other parameters. Additionally, we applied 
some checks to make sure the user input variables are in a physically valid range. 

Additionaly, the file also contains the following two lines of code
```python
# Global Constant to define the extension of zip files
ZIP_EXTENSION = "zip"

# Global constant to define the path of the folder where all the simulations are saved
SIMULATIONS_FOLDER_PATH = "/app/simulation_files"
```
Which could also occur somewhere else and define global constants which are the 
folder path in which all simulation results are about to appear and the extension 
for the compression. 


### aspherix_files_creation.py

This file contains one function needed to create the simulation file, namely
"create_input_files". This function copies Aspherix (or Lammps) input files
(from the sub-diretory "templates") and replaces the placeholder with the 
user-defined values. Additionally all required mesh files, submit files and 
license files are copied into the simulation directory in order to prepare a 
complete simulation setup.


### simulation_manager.py

This script is designed as the interface between the MarketPlace and the simulation. 

```python
class SimulationManager:
    def __init__(self):
        self.simulations: dict = {}

    def _get_simulation(self, job_id: str) -> SimulationBase:
        """
        Get the simulation corresponding to the job_id.

        Args:
            job_id (str): unique id of the simulation

        Raises:
            KeyError: if there is no simulation matching the id

        Returns:
            Simulation instance
        """
        try:
            simulation = self.simulations[job_id]
            return simulation
        except KeyError as ke:
            message = f"Simulation with id '{job_id}' not found"
            logging.error(message)
            raise KeyError(message) from ke

    def _add_simulation(self, simulation: SimulationBase) -> str:
        """Append a simulation to the internal datastructure.

        Args:
            simulation (SimulationBase): Object to add

        Returns:
            str: ID of the added object
        """
        job_id: str = simulation.job_id
        self.simulations[job_id] = simulation
        return job_id

    def _delete_simulation(self, job_id: str):
        """Remove a simulation from the internal datastructure.

        Args:
            job_id (str): id of the simulation to remove
        """
        del self.simulations[job_id]

    def create_simulation(self, request_obj: dict) -> str:
        """Create a new simulation given the arguments.

        Args:
           requestObj: dictionary containing input configuration

        Returns:
            str: unique job id
        """
        # here you may use SimulationLocal for local development
        return self._add_simulation(SimulationHPC(request_obj))

    def run_simulation(self, job_id: str):
        """Execute a simulation.

        Args:
            job_id (str): unique simulation id
        """
        self._get_simulation(job_id).run()

   def download_simulation(self, job_id: str) -> str:
        """Download a simulation.

        Args:
            job_id (str): unique simulation id

        Returns:
            str: path to the zipped file to download
        """
        simulation = self._get_simulation(job_id)
        return simulation.zip_output()

    def stop_simulation(self, job_id: str) -> dict:
        """Force termination of a simulation.

        Args:
            job_id (str): unique id of the simulation
        """
        self._get_simulation(job_id).stop()

    def delete_simulation(self, job_id: str) -> dict:
        """Delete all the simulation information.

        Args:
            job_id (str): unique id of simulation
        """
        self._get_simulation(job_id).delete()
        self._delete_simulation(job_id)

    def get_simulation_state(self, job_id: str) -> SimulationStatus:
        """Return the status of a particular simulation.

        Args:
            job_id (str): id of the simulation

        Returns:
            SimulationStatus: status of the simulation
        """
        return self._get_simulation(job_id).status

    def get_simulation_list(self) -> list:
        """Return unique ids of all the simulations.

        Returns:
            list: list of simulation ids
        """
        return list(self.simulations.keys())
```

### simulation_base.py
This file contains the base class SimulationBase for managing a single simulation. 
It provides methods for starting a simulation, stopping it, zipping the output 
files, and deleting the simulation. The class also has a property for retrieving the status of the simulation. This is the base for "SimulationHPC" and "SimulationLocal", where
later is designed only for local development purposes.

```python
import os
import uuid
from simulation_controller.config import (
    SimulationStatus,
    ZIP_EXTENSION,
    SIMULATIONS_FOLDER_PATH,
    SimulationConfig,
)

import logging

class SimulationBase:
    """Manage a single simulation."""

    def __init__(self, request_obj: dict = {}):
        """
        Initialize a SimulationBase object.

        Args:
            request_obj (dict, optional): A dictionary containing the simulation request details.
                                          Defaults to an empty dictionary.
        """
        self.job_id: str = str(uuid.uuid4())
        self.simulationPath = os.path.join(SIMULATIONS_FOLDER_PATH, self.job_id)
        self.simulation_config: SimulationConfig = SimulationConfig(request_obj)
        self._status = None

        def status(self, value: SimulationStatus):
        """
        Set the status of the simulation.

        Args:
            value (SimulationStatus): The status value to set.
        """
        self._status = value

    def run(self):
        ...

    def stop(self):
        ...

    def zip_output(self) -> str:
        ...

    def delete(self):
        ...
```
### simulation_hpc.py

This file define a class "SimulationHPC" that inherit from the "SimulationBase" and uses the Marketplace hpc app to set up a calculation on a remote server.
```python
from simulation_controller.simulation_base import SimulationBase
from simulation_controller.config import (
    SimulationStatus,
    ZIP_EXTENSION,
    SIMULATIONS_FOLDER_PATH,
    SimulationConfig,
)
from simulation_controller.paste_files_creation import (
    create_input_files
)

import logging
from hpc_gateway_sdk import get_app
import json
from distutils.file_util import copy_file


MP_ACCESS_TOKEN=''
class SimulationHPC(SimulationBase):
    """Manage a HPC simulation."""

    def __init__(self, request_obj: dict = {}):
        super().__init__(request_obj)
        create_input_files(self.simulationPath, SimulationConfig(request_obj))
        self._status: SimulationStatus = SimulationStatus.CREATED
        self._hpc: HPCApp = get_app(name="mc",access_token=MP_ACCESS_TOKEN)
        self._resource_id = self._hpc.create_user()
        self.job_id = self._hpc.create_job(new_transformation={
                                                                    "job_name": "uc4_demo",
                                                                    "ntasks_per_node": 2,
                                                                    "partition": "debug",
                                                                    "image": "path-to-simgularity-container/aspherix_no_license_mpich314.sif",
                                                                    "executable_cmd": "bash submit.sh",
                                                                    })
        self._hpc_job_info = None
        logging.info(
            f"Simulation '{self.job_id}' with " f"configuration {request_obj} created."
        )
```
in the "hpc.create_job" we indicate the path where the singularity container we have created in the first section is stored, together with the "submit.sh" which is a bash script thet execute all the simulation step.

Inside the "run" method of the "SimulationHPC" class we find

```python
    self._hpc.upload_file(self.job_id,filename='simulation.zip', source_path=os.path.join(SIMULATIONS_FOLDER_PATH,'simulation.zip'))
    self._hpc.upload_file(self.job_id, filename='submit.sh',source_path=os.path.join(templateDirPath,'submit.sh'))
    # start simulation
    rsp = self._hpc.launch_job(self.job_id)
    self.status = SimulationStatus.INPROGRESS
    logging.info(f"Simulation '{self.job_id}' started successfully.")
```
which shows how to upload file on the server and launch a job.

Inside the "zip_output" there is a example of how to download file created by the simulation.
```python
   
   # download what we need
   with open(os.path.join(outputPath,"log_aspherix.txt"), mode="w") as file:
       content = self._hpc.download(resourceid=self._resource_id, filename='log_aspherix.txt')
       file.write(content)

```
Here for example we download the Aspherix logfile computed of the mixer simulation.
