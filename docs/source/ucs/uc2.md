# Implementation of Use Case 2

This documentation explains how the workflow to simulate viscoelastic pastes, using OpenFOAM and the rheoTool lybrary, is incorporated within the MarketPlace. In detail, this manual provides an overview on most of the function having been created in this Use Case. This manual should serve as a detailed explanation on how to onboard your very own software in the MarketPlace.

Everything is organized within one folder and we will slowly go through each folder and file therein.

- [Folder] simulation_controller
- [Folder] static
- .gitmodules
- app.py
- deploy_heroku.sh
- docker-compose.yml
- Dockerfile
- openAPI.yml
- prepare_deployment.sh
- requirements.txt

## Create a singularity container

In order to insure the correct working of the workflow, we create a container which install all the software we need

Start from the image which already has mpi installed

```docker
FROM containers4hpc/base-mpich314:0.1.0
SHELL [ "/bin/bash", "-c" ]
```

Be sure to install all the basic software you need, after which we can install OpenFOAM, this worflow work with OpenFOAM 6.

```docker
RUN sh -c "wget -O - http://dl.openfoam.org/gpg.key | apt-key add -" ;\
    add-apt-repository http://dl.openfoam.org/ubuntu ;\
    apt-get update ;\
    apt-get install -y --no-install-recommends openfoam6 ;\
    rm -rf /var/lib/apt/lists/* ;\
    echo "source /opt/openfoam6/etc/bashrc" >> ~foam/.bashrc ;\
    echo "export OMPI_MCA_btl_vader_single_copy_mechanism=none" >> ~foam/.bashrc
```

After which we can install RheoTools

```docker
RUN git clone https://github.com/fppimenta/rheoTool.git;\
    cd rheoTool;\
    git checkout 56c2701636e6eb59dc51799fd0636805be23510d

RUN  source /opt/openfoam6/etc/bashrc;\
    cd rheoTool/of60;\
    ./downloadEigen;\
    echo "export EIGEN_RHEO=$WM_PROJECT_USER_DIR/ThirdParty/Eigen3.2.9" >> ~foam/.bashrc
```

and install all the python dependencies that the workflow needs

```python
#install python packages
RUN pip3 install numpy
RUN pip3 install --upgrade pillow
RUN pip3 install --upgrade matplotlib
RUN pip3 install scipy
RUN pip3 install vtk
```

Once the Dockerfile has all you need, you can create a docker image

```bash
 docker build -t uc2 .
```

after saving the image as a .tar file you can create a singularity container

```bash
singularity build (--sandbox) uc2 docker-archive://uc2.tar
singularity build uc2.sif uc2
```

This container can be run anywhere

## simulation controller

Now we are working on the folder "simulation_controller" which contains several files that provide the function to create, start and stop a simulation as well as retrieving the simulation results.

Let us have a look at the following files that are all found in the folder "simulation_controller"

- \_\_init\_\_.py
- config.py
- paste_files_creation.py
- post_processing.py
- simulation_manager.py
- simulation_base.py
- simulation_hpc.py

### \_\_init\_\_.py

The file "\_\_init\_\_.py" is an empty file and its only purpose is that python allows to include all function via the regular
package syntax as libraries. This means in all files, we can include classes and function of other files with simple commands. Usually, python has no problem importing a whole directory. But when it comes to importing a class from a file in a directory, this will raise an exception. But having such a "\_\_init\_\_.py" file allows to use the following notation

```python
from directory.filename import classname
```

when having a class "classname" in a file "filename" within the directoy "directory".

### config.py

In this file, we have defined two classes with names "SimulationStatus" and "SimulationConfig" and follows with the definition for the simulation states. Here, we define 5 different kinds of states that are

- created
- running
- completed
- stopped
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

By writing "Enum" into the bracket, this class inheriting from the Enum class which is a built-in class from python. This allows to use a more natural syntax to ask the script whether the simulation has been created or whether it is running. In fact, we can apply the following notation

```python
state = SimulationStatus.CREATED # which is equal to "CREATED"
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
        self.endTime: float = float(request_obj.get("endTime", 0.0002))
        self.writeInterval: float = float(request_obj.get("writeInterval", 1e-4))
        self.deltaT: float = float(request_obj.get("deltaT", 1e-8))
        self.initWide: float = float(request_obj.get("initial_wide", 300))
        self.UpVel: float = float(request_obj.get("upward_velocity", 0.003))
        self.rheometer: bool = bool(request_obj.get("rheometer", False))
        self.creation_time = time.time()

        if self.deltaT > self.endTime:
            err_msg += (
                "the simulation time step should be smaller than the total simulation time"
            )
            logging.error(err_msg)
            raise ValueError(err_msg)
```

This is a class that contains only an init method. This is the function that is called whenever an instant of the
SimulationConfig class is created. Basically, this function receives the input parameters that are made available for
the Use Case tutorial. These were

- Total simulation time (s)
- How often does the simulation write data (s)
- Simulation time step (s)
- Initial paste width (mm)
- Upward velocity of the grid (m/s)
- Boolean value which allow to chose if the user want to run the rheometer step of the app. In case is false the app will run with default values for the paste parameters.
  and the corresponding parameters were fed into a dictionary. At the beginning, each of the keys from this
  dictionary is called and in the case that this key has not been defined, a default is being returned. For example the code line

```python
self.configuration: int = request_obj.get("configuration", 1)
```

asks if there is a key with the name "configuration" in the dictionary "request_obj". If the key is present, its value is returned (that is the value that the user has provided in the MarketPlace interface - to be explained later). If the key
has not been defined, we use the default value of "1". This value for the configuration is mapped to an integer
and stored in the variable "self.configuration" to make it available within the instant of the SimulationConfig
object.

The same procedure is done for the other parameters. Additionally, we applied some checks to make sure
the user input variables are in a physically valid range.

Additionally, the file also contains the following two lines of code

```python
# Global Constant to define the extension of zip files
ZIP_EXTENSION = "zip"

# Global constant to define the path of the folder where all the simulations are saved
SIMULATIONS_FOLDER_PATH = "/app/simulation_files"
```

Which could also occur somewhere else and define global constants which are the folder path in which
all simulation results are about to appear and the extension for the compression.

### paste_files_creation.py

This file contains two function need to create the simulation file.
The first is "defineInitfield" which will create the initial field that will be read by OpenFOAM during the simulation

```python
import os
import shutil
from distutils.dir_util import copy_tree
from simulation_controller.config import ( SIMULATIONS_FOLDER_PATH,SimulationConfig,)

def defineInitfield(wideIn,U_up,folderFSF):

```

The second is "create_input_files"

```python
def create_input_files(foldername: str, simulationConfig: SimulationConfig):
    """
    Function to create the start configuration for the MarketPlace simulation.

    simulationConfig : SimulationConfig
        instance with the specific configuration values for a run
    """

```

This function access the variables that have been defined in the SimulationConfig from above, and write out the necessary file for the simulation to run.

### post_processing.py

In this script we perform the post-processing of the data generated by the simulation.

We use the VTK library to read the data

```python
import numpy as np
import vtk
import matplotlib.pyplot as plt
...
def extractInterfaceInfo(directory,nameCase):
    VTK=directory+'/VTK/'+nameCase+'_'+str(f'{nameCa:.5g}')+'.vtk'

    reader = vtk.vtkUnstructuredGridReader()
    reader.SetFileName(VTK)
    reader.Update()
...
```

then we use the matplotlib library to plot the interface width evolution with time

```python
def interfaceTracing(directory,nameP):
    interfaceAll=[]
    broadAll=[]

    markers = ['-o', '-.', '-,', '-x', '-+', '-v', '-^', '-<', '>-', '-s', '-d']
    i=0
    fig2, ax2 = plt.subplots(figsize=(16, 9))
    fontdict={'fontsize': 20}
    [interfaceOut,broadOut]=extractInterfaceInfo(directory,nameP)
    interfaceAll.append(interfaceOut)
    broadAll.append(broadOut)
    plotInterf(interfaceOut,nameP,directory)
    plt.close()

    ax2.plot(broadOut[:,0],broadOut[:,1]/broadOut[0,1],markers[i], label=nameP)
    ax2.set_adjustable("box")
    ax2.set_title('Normalized paste broadening', fontdict)
    ax2.set_ylabel('Normalized Broadening', fontdict)
    ax2.set_xlabel('time [$s$]', fontdict)
    ax2.tick_params(axis='both', which='major', labelsize=20)
    ax2.tick_params(axis='both', which='minor', labelsize=20)
    #fig2.legend()
    fig2.savefig(directory+'/rheometerResults/paste_Broadening.png')
```

and the interface profile

```python
def plotInterf(interface,name,directory):
    #lb=['coarse','medium','fine']
    fig3, ax3 = plt.subplots(figsize=(16, 9))
    fontdict={'fontsize': 20}

    y = abs(1e3-interface[0][:,0]*1e6)
    z = interface[0][:,1]*1e6
    plt.plot(y,z,label='init')

    y = abs(1e3-interface[-1][:,0]*1e6)
    z = interface[-1][:,1]*1e6
    plt.plot(y,z,label='end')

    #fig3.tight_layout()
    ax3.axis('equal')
    ax3.set_adjustable("box")
    ax3.set_ybound(lower=0.0, upper=9e-5*1e6)
    ax3.set_xbound(lower=0, upper=335)
    ax3.set_ylabel('z [$\mu m$]', fontdict)
    ax3.set_xlabel('y [$\mu m$]', fontdict)
    #fig3.legend()
    fig3.legend(bbox_to_anchor=(0.78, 0.75), loc='upper left', fontsize=20)
    ax3.set_title('Interface comparison', fontdict)
    ax3.tick_params(axis='both', which='major', labelsize=20)
    ax3.tick_params(axis='both', which='minor', labelsize=20)

    nf=directory+'/rheometerResults/interfaceComparison.png'
    plt.savefig(nf)
```

### simulation_manager.py

This script is designed as the interface between the MarketPlace and the simulation.

```python
class SimulationManager:
    def __init__(self):
        self.simulations: dict = {}

    def _get_simulation(self, job_id: str) -> Simulation:
        """
        Get the simulation corresponding to the job_id.

        Args:
            job_id (str): unique id of he simulation

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

    def _add_simulation(self, simulation: Simulation) -> str:
        """Append a simulation to the internal datastructure.

        Args:
            simulation (Simulation): Object to add

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
        return self._add_simulation(Simulation(request_obj))

    def run_simulation(self, job_id: str):
        """Execute a simulation.

        Args:
            job_id (str): unique simulation id
        """
        self._get_simulation(job_id).run()

    def get_simulation_output(self, job_id: str) -> str:
        """Get the output a simulation.

        Args:
            job_id (str): unique simulation id

        Returns:
            str: json representation of the dlite object
        """
        mapping = "SimpartixOutput"
        mimetype = "vnd.sintef.dlite+json"
        simulation = self._get_simulation(job_id)
        return simulation.get_output(), mapping, mimetype

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
It provides methods for starting a simulation, stopping it, zipping the output files, and deleting the simulation.
The class also has a property for retrieving the status of the simulation.

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

### simulation.py

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
                                                                    "job_name": "uc2_demo",
                                                                    "ntasks_per_node": 2,
                                                                    "partition": "debug",
                                                                    "image": "path-to-simgularity-container/uc2.sif",
                                                                    "executable_cmd": "bash runJob.sh",
                                                                    })
        self._hpc_job_info = None
        logging.info(
            f"Simulation '{self.job_id}' with " f"configuration {request_obj} created."
        )
```

in the "hpc.create_job" we indicate the path where the singularity container we have created in the first section is stored, together with the "runJob.sh" which is a bash script that execute all the workflow step.

Inside the "run" method of the "SimulationHPC" class we find

```python
    self._hpc.upload_file(self.job_id,filename='simulation.zip', source_path=os.path.join(SIMULATIONS_FOLDER_PATH,'simulation.zip'))
    self._hpc.upload_file(self.job_id, filename='runJob.sh',source_path=os.path.join(templateDirPath,'runJob.sh'))
    # start simulation
    rsp = self._hpc.launch_job(self.job_id)
    self.status = SimulationStatus.INPROGRESS
    logging.info(f"Simulation '{self.job_id}' started successfully.")
```

which shows how to upload file on the server and launch a job.

Inside the "postprocess_output" there is a example of how to download file created by the simulation.

```python
    img_list=['paste_Broadening.png','interfaceComparison.png']#,'modulus_results.png','viscosity_results.png']
    for imag in img_list:
        file='simulation/caseBase/rheometerResults/'+imag
        resp = self._hpc.download_file(self.job_id, filename=file)
        with open(os.path.join(imagPath,imag), 'wb') as csr:
            for chunk in resp.iter_content(chunk_size=1024):
                if chunk:
                    csr.write(chunk)
```

Here for example we download the two images computed by the functions in "post_process.py".
