# Implementation of Use Case 1 into the MarketPlace framework

This documentation explains how the software SimPARTIX is incorporated within the MarketPlace. In detail, this manual provides an overview on most of the function having been created in this Use Case. This manual should serve as a detailed explanation on how to onboard your very own software in the MarketPlace.

Everything is organized within one folder and we will slowly go through each folder and file therein. In this Use Case, the software SimPARTIX is included. Please follow along each this guide and replace SimPARTIX mentally with your own software in mind and add the corresponding scripts and functions where necessary. 
In the end of this tutorial, you should have the following files and folder in your working directory

- [Folder] simpartix
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

optional, but available in our folder:
- .pre-commit-config.yaml
- .gitignore

## Including your own software

In a first step, the own software should be made available. In this case, we host SimPARTIX on Gitlab and thereby use Git as version control system. Using the [https://git-scm.com/book/en/v2/Git-Tools-Submodules][git submodule] commands, we added
our software to the folder. This procedure allows us to keep the own software up to date easily as frequent changes in the source code are expected in order to implement new routines for the communication in MarketPlace. 

The result of this procedure are 
- [Folder] simpartix
- .gitmodules


## simulation controller

Now we are working on the folder "simulation_controller" which contains several files that provide the function to create, start and stop a simulation as well as retrieving the simulation results. The converter function to convert the SimPARTIX results to MICRESS input files are also positioned here. 

Let us have a look at the following files that are all found in the folder "simulation_controller"
- \_\_init\_\_.py
- config.py
- propartix_files_creation.py
- simpartix_output.py
- SimPARTIXOutput.json
- simulation_manager.py
- simulation.py


### \_\_init\_\_.py

The file "\_\_init\_\_.py" is an empty file and its only purpose is that python allows to include all function via the regular 
package syntax as libraries. This means in all files, we can include classes and function of other files with simple commands. Usually, python has no problem to import a whole directory. But when it comes to importing a class from a file in a directory, this will raise an exception. But having such a "\_\_init\_\_.py" file allows to use the following notation

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
    def __str__(self):
        return str(self.value)
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    STOPPED = "STOPPED"
    ERROR = "ERROR"
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
        self.configuration: int = request_obj.get("configuration", 1)
        self.laserPower: float = request_obj.get("laserPower", 150)
        self.laserSpeed: float = request_obj.get("laserSpeed", 3.0)
        self.sphereDiameter: float = request_obj.get("sphereDiameter", 30e-6)
        if self.sphereDiameter <= 5e-6:
            err_msg += "Sphere diameter value too little."
            logging.error(err_msg)
            raise ValueError(err_msg)
        self.phi: float = request_obj.get("phi", 0.7)
        if self.phi >= 1 or self.phi < 0:
            err_msg += "Phi must be between 0 and 1."
            logging.error(err_msg)
            raise ValueError(err_msg)
        self.powderLayerHeight: float = request_obj.get(
            "powderLayerHeight", 60e-6
        )
        if self.powderLayerHeight < self.sphereDiameter:
            err_msg += (
                "Powder layer height must be at least the sphere diameter"
            )
            logging.error(err_msg)
            raise ValueError(err_msg)
```
This is a class that contains only an init method. This is the function that is called whenever an instant of the 
SimulationConfig class is created. Basically, this function receives the input parameters that are made available for
the Use Case tutorial. These were
- Laser power (W)
- Laser scan speed (m/s) with which the laser traverses the powder bed
- Powder volume fraction (-) to describe the initial filling density of the powder
- Powder layer thickness (m) which is the height of the powder layer.
- Particle diameter (m). In this tutorial, all particles will have the same diameter.
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
the user input variables are in a physically valid range. For example, the filling fraction "phi" cannot be smaller 
than 0 as there would be no powder to melt or higher as 1 as 1 means everything is filled with powder and we
cannot have a filling fraction higher than 100%. 


Additionaly, the file also contains the following two lines of code
```python
# Global Constant to define the extension of zip files
ZIP_EXTENSION = "zip"

# Global constant to define the path of the folder where all the simulations are saved
SIMULATIONS_FOLDER_PATH = "/app/simulation_files"
```
Which could also occur somewhere else and define global constants which are the folder path in which
all simulation results are about to appear and the extension for the compression. 


### propartix_files_creation.py

This file is pretty unique to SimPARTIX and uses the function that are provided by SimPARTIX to create
the start configurations. The python engine of SimPARTIX is called ProPARTIX which is the reason 
for the file name. This file has the following structure. 

```python
import os
import numpy as np
import propartix as px
from simulation_controller.config import SimulationConfig

def create_input_files(foldername: str, simulationConfig: SimulationConfig):
    """
    Function to create the start configuration for the MarketPlace simulation.

    simulationConfig : SimulationConfig
        instance with the specific configuration values for a run
    """
    # it follows a list of code lines specific to ProPARTIX to create the 
    # start configuration
```
This function "create_input_files" can access the variables that have been defined in the SimulationConfig
from above. For example, the sphere diameter can be accessed by
```python
simulationConfig.sphereDiameter
```
with a similar syntax for all other variables. 

Additionally, there are further ProPARTIX specific functions that are
- get_output_values
- create_micress_files
that are specific to this Use Case have been created while both were sitting together and figured out
how the output of the SimPARTIX simulation can be converted to a MICRESS input

### simpartix_output.py and SimPARTIXOutput.json

The information that need to be transferred between SimPARTIX and MICRESS are temperature, a quantity called group which is the ID of each powder element, and state of matter which describes whether this specific
part of the powder is still solid, liquid or vaporous. 

This file "simpartix_output.py" only contains a class with the following content
```python
class SimPARTIXOutput:
    def __init__(self, temperature, group, state_of_matter):
        self.temperature = temperature
        self.group = group
        self.state_of_matter = state_of_matter
```
this class definition goes in hand with the file "SimPARTIXOutput.json". 
At this stage, the mapping of the SimPARTIX quantities temperature, group and state_of_matter
to Ontologie concepts is realized. This mapping is done in the file "SimPARTIXOutput.json" and it 
has the following structure. 
```json
{
    "name": "SimPARTIXOutput",
    "version": "0.0.1",
    "namespace": "http://onto-ns.com/meta",
    "meta": "http://onto-ns.com/meta/0.3/EntitySchema",
    "description": "Output of a SimPARTIX melt pool simulation (MarketPlace UC1).",
    "dimensions": [
      {
        "name": "X",
        "description": "Number of cells in x direction."
      },
      {
        "name": "Z",
        "description": "Number of cells in z direction."
      }
    ],
    "properties": [
      {
        "_comment": "linked to ThermodynamicTemperature, http://emmo.info/emmo#EMMO_affe07e4_e9bc_4852_86c6_69e26182a17f",
        "name": "temperature",
        "type": "float",
        "unit": "Kelvin",
        "dims": ["X", "Z"],
        "description": "List of temperature cells."
      },
      {
        "_comment": "is linked to http://emmo.info/emmo#EMMO_0cd58641_824c_4851_907f_f4c3be76630c",
        "name": "group",
        "type": "int",
        "dims": ["X", "Z"],
        "description": "List of group (i.e. grain) cells."
      },
      {
        "_comment": "linked to StateOfMatter, http://emmo.info/emmo#EMMO_b9695e87_8261_412e_83cd_a86459426a28",
        "name": "state_of_matter",
        "type": "int",
        "dims": ["X", "Z"],
        "description": "List of state of matter (i.e. phase) cells."
      }
    ]
}
```
In detail, we define the type, the dimension, the name and the corresponding EMMO element. 
EMMO here is one concept of ontology, but other ontologies are equally applicable at this
stage. 

### simulation_manager.py

This script is designed as the interface between the MarketPlace and the simulation. 

The only individual part is the mapping to SimPARTIX quantities to EMMO ontology elements at the beginning 
```python
mappings = {
    "SimpartixOutput": {
        "name": "SimpartixOutput",
        "properties": {
            "temperature": "http://emmo.info/emmo#EMMO_affe07e4_e9bc_4852_86c6_69e26182a17f",
            "group": "http://emmo.info/emmo#EMMO_0cd58641_824c_4851_907f_f4c3be76630c",
            "state_of_matter": "http://emmo.info/emmo#EMMO_b9695e87_8261_412e_83cd_a86459426a28",
        },
    },
}
```

and the remaining part of the script can  be copied
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

### simulation.py

This is one of the more complex files and hence should be described more in detail. At the beginning, 
the necessary libraries are imported
```python
import logging
import os
import shutil
import subprocess
import uuid
from typing import Tuple
import dlite
```
for the following purpose
- logging -> for the error message
- os, shutil, subprocesses -> to create new directories, copy files and start the simulation software SimPARTIX
- uuid -> a useful library to assign unique IDs to the simulation 
- dlite is a C implementation of the SINTEF Open Framework and Tools (SOFT) which is a set of concepts and tools for using data models to efficiently describe and work with scientific data. 

We also further import the following classes and function from our previously created files
```python
from simulation_controller.config import (
    SIMULATIONS_FOLDER_PATH,
    SimulationConfig,
    SimulationStatus,
)
from simulation_controller.propartix_files_creation import (
    create_input_files,
    get_output_values,
)
from simulation_controller.simpartix_output import SimPARTIXOutput
```

It follows the Simulation class which is given in its completness first to the sake of simplified copy and paste
and afterwards each of its function is explained more in detail
```python
class Simulation:
    """Manage a single simulation."""

    def __init__(self, request_obj: dict):
        self.job_id: str = str(uuid.uuid4())
        self.simulationPath = os.path.join(
            SIMULATIONS_FOLDER_PATH, self.job_id
        )
        create_input_files(self.simulationPath, SimulationConfig(request_obj))
        self._status: SimulationStatus = SimulationStatus.CREATED
        self._process = None
        logging.info(
            f"Simulation '{self.job_id}' with "
            f"configuration {request_obj} created."
        )

    @property
    def status(self) -> SimulationStatus:
        """Getter for the status.

        If the simulation is running, the process is checked for completion.

        Returns:
            SimulationStatus: status of the simulation
        """
        if self._status == SimulationStatus.RUNNING:
            process_status = self.process.poll()
            if process_status is None:
                return SimulationStatus.RUNNING
            elif process_status == 0:
                logging.info(f"Simulation '{self.job_id}' is now completed.")
                self.status = SimulationStatus.COMPLETED
            else:
                logging.error(f"Error occured in simulation '{self.job_id}'.")
                self.status = SimulationStatus.ERROR
        return self._status

    @status.setter
    def status(self, value: SimulationStatus):
        self._status = value

    @property
    def process(self):
        return self._process

    @process.setter
    def process(self, value):
        self._process = value

    def run(self):
        """
        Start running a simulation.

        A new process that calls the SimPARTIX binary is spawned,
        and the output is stored in a separate directory

        Raises:
            RuntimeError: when the simulation is already in progress
        """
        if self.status == SimulationStatus.RUNNING:
            msg = f"Simulation '{self.job_id}' already in progress."
            logging.error(msg)
            raise RuntimeError(msg)
        outputPath = os.path.join(self.simulationPath, "output")
        if not os.path.isdir(outputPath):
            os.mkdir(outputPath)
        os.chdir(self.simulationPath)
        self.process = subprocess.Popen(["SimPARTIX"], stdout=subprocess.PIPE)
        self.status = SimulationStatus.RUNNING
        logging.info(f"Simulation '{self.job_id}' started successfully.")

    def stop(self):
        """Stop a running process.

        Raises:
            RuntimeError: if the simulation is not running
        """
        if self.process is None:
            msg = f"No process to stop. Is simulation '{self.job_id}' running?"

            logging.error(msg)
            raise RuntimeError(msg)
        self.process.terminate()
        self.status = SimulationStatus.STOPPED
        self.process = None
        logging.info(f"Simulation '{self.job_id}' stopped successfully.")

    def get_output(self) -> Tuple[str]:
        """Get the output of a simulation

        Raises:
            RuntimeError: If the simulation has not run

        Returns:
            Tuple[str]: data in json format
                        semantic mapping for the data
                        mimetype of the data
        """
        result = get_output_values(self.simulationPath)

        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "SimPARTIXOutput.json"
        )
        DLiteSimPARTIXOutput = dlite.classfactory(
            SimPARTIXOutput, url=f"json://{path}"
        )
        if self.status in (
            SimulationStatus.RUNNING,
            SimulationStatus.CREATED,
        ):
            msg = (
                f"Cannot download, simulation '{self.job_id}' "
                f"has status '{self.status.name}'."
            )
            logging.error(msg)
            raise RuntimeError(msg)
        simpartix_output = DLiteSimPARTIXOutput(
            temperature=result["Temperature_SPH"],
            group=result["Group"],
            state_of_matter=result["StateOfMatter_SPH"],
        )
        # Store the output as a file for posterity
        file_path = os.path.join(self.simulationPath, self.job_id)
        simpartix_output.dlite_inst.save(f"json://{file_path}.json?mode=w")
        return simpartix_output.dlite_inst.asjson()

    def delete(self):
        """
        Delete all the simulation folders and files.

        Raises:
            RuntimeError: if deleting a running simulation
        """
        if self.status == SimulationStatus.RUNNING:
            msg = f"Simulation '{self.job_id}' is running."
            logging.error(msg)
            raise RuntimeError(msg)
        shutil.rmtree(self.simulationPath)
        logging.info(f"Simulation '{self.job_id}' and related files deleted.")
```

It follows the detailed explanation

```python
def __init__(self, request_obj: dict):
    self.job_id: str = str(uuid.uuid4())
    self.simulationPath = os.path.join(
        SIMULATIONS_FOLDER_PATH, self.job_id
    )
    create_input_files(self.simulationPath, SimulationConfig(request_obj))
    self._status: SimulationStatus = SimulationStatus.CREATED
    self._process = None
    logging.info(
        f"Simulation '{self.job_id}' with "
        f"configuration {request_obj} created."
    )
```
In the init method, the unique ID is created ("uuid.uuid4()") and stored as internal variable "job_id"
Based on this ID, a unique simulation folder path is created based on the parent folder PATH that was 
defined in the file "config.py". 
Next, the function "create_input_files" from the file "propartix_files_creation" is called. This was again 
a function unique to SimPARTIX in which the start configuration is created and hence that must 
be written individually for each new simulation software. 
Last but not least, the status of the simulation is set to "created" and the corresponding
pieces of information are written to the log file. 


```python
@property
def status(self) -> SimulationStatus:
    """Getter for the status.

    If the simulation is running, the process is checked for completion.

    Returns:
        SimulationStatus: status of the simulation
    """
    if self._status == SimulationStatus.RUNNING:
        process_status = self.process.poll()
        if process_status is None:
            return SimulationStatus.RUNNING
        elif process_status == 0:
            logging.info(f"Simulation '{self.job_id}' is now completed.")
            self.status = SimulationStatus.COMPLETED
        else:
            logging.error(f"Error occured in simulation '{self.job_id}'.")
            self.status = SimulationStatus.ERROR
    return self._status
```
This piece of code checks if the simulation is still running. The idea behind this function is that 
first we check for the flag "SimulationStatus.RUNNING" as the simulation
cannot be running otherwise. If the simulation was declared as running the last time, 
we check again. This is done by self.process.poll(). This function does not work on all 
operating system, but on Linux it can be used to screen for I/O events that would occur during 
the simulation. 


It follows a list of setter and getter to set the simulation or process status.
```python
@status.setter
def status(self, value: SimulationStatus):
    self._status = value

@property
def process(self):
    return self._process

@process.setter
def process(self, value):
    self._process = value
```

The simulation itself is staretd by the following function
```python
def run(self):
    """
    Start running a simulation.

    A new process that calls the SimPARTIX binary is spawned,
    and the output is stored in a separate directory

    Raises:
        RuntimeError: when the simulation is already in progress
    """
    if self.status == SimulationStatus.RUNNING:
        msg = f"Simulation '{self.job_id}' already in progress."
        logging.error(msg)
        raise RuntimeError(msg)
    outputPath = os.path.join(self.simulationPath, "output")
    if not os.path.isdir(outputPath):
        os.mkdir(outputPath)
    os.chdir(self.simulationPath)
    self.process = subprocess.Popen(["SimPARTIX"], stdout=subprocess.PIPE)
    self.status = SimulationStatus.RUNNING
    logging.info(f"Simulation '{self.job_id}' started successfully.")
```
This function first checks if a simulation with that ID is already running like in the case that
the user clicks multiple times on the "run" button. 
Next, the output path is defined and created which in this case simply is called "output"
Then, the change into that directory in which the simulation is to be exectued and then 
start calling "SimPARTIX" as subprocess. This is like having a terminal and typing 
"SimPARTIX" into that terminal. Finally, the state of the simulation is set to 
"running" and the corresponding info message is written to the log file. 
If you script has to be called via another command, the corresponding 
command has to be written where "SimPARTIX" is written in third last line. 

Stopping of a simulation is realized via
```python
def stop(self):
    """Stop a running process.

    Raises:
        RuntimeError: if the simulation is not running
    """
    if self.process is None:
        msg = f"No process to stop. Is simulation '{self.job_id}' running?"

        logging.error(msg)
        raise RuntimeError(msg)
    self.process.terminate()
    self.status = SimulationStatus.STOPPED
    self.process = None
    logging.info(f"Simulation '{self.job_id}' stopped successfully.")
```
This function first checks if the processes to be stopped is actually running and raises 
an error message if not. 
If the process is running, it is stopped by "self.process.terminate()"
and the accompagning flags "self.status" and "self.process" are set. 

It follows the function to retrieve the simulation results. 
```python
def get_output(self) -> Tuple[str]:
    """Get the output of a simulation

    Raises:
        RuntimeError: If the simulation has not run

    Returns:
        Tuple[str]: data in json format
                    semantic mapping for the data
                    mimetype of the data
    """
    result = get_output_values(self.simulationPath)

    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "SimPARTIXOutput.json"
    )
    DLiteSimPARTIXOutput = dlite.classfactory(
        SimPARTIXOutput, url=f"json://{path}"
    )
    if self.status in (
        SimulationStatus.RUNNING,
        SimulationStatus.CREATED,
    ):
        msg = (
            f"Cannot download, simulation '{self.job_id}' "
            f"has status '{self.status.name}'."
        )
        logging.error(msg)
        raise RuntimeError(msg)
    simpartix_output = DLiteSimPARTIXOutput(
        temperature=result["Temperature_SPH"],
        group=result["Group"],
        state_of_matter=result["StateOfMatter_SPH"],
    )
    # Store the output as a file for posterity
    file_path = os.path.join(self.simulationPath, self.job_id)
    simpartix_output.dlite_inst.save(f"json://{file_path}.json?mode=w")
    return simpartix_output.dlite_inst.asjson()
```

Finally, the data of a simulation can be deleted by the following function
```python
def delete(self):
    """
    Delete all the simulation folders and files.

    Raises:
        RuntimeError: if deleting a running simulation
    """
    if self.status == SimulationStatus.RUNNING:
        msg = f"Simulation '{self.job_id}' is running."
        logging.error(msg)
        raise RuntimeError(msg)
    shutil.rmtree(self.simulationPath)
    logging.info(f"Simulation '{self.job_id}' and related files deleted.")
```
This function first checks if a simulation has stoped running. If it not running, the data is 
simply deleted using the "rmtree" function of the shutil library. This library is a built-in-library
of python that can be used to delete folders. 

## Explanation of the optional files

### pre config

There is a tool called "pre-commit" that allows to perform checks on the source code prior to pushing them to the repository. If you are interested in such a tool, follow the explanation on [https://pre-commit.com][ this website]. The result of 
this procedure is file called "pre-commit-config.yaml".


### gitignore file ###

One best element practice when using coding is to apply version control to keep track of your changes in the source code. One such version control system is git. A gitignore file allows to have files in your working directory that 
should not be tracked by git. For more information, please follow the [https://git-scm.com/docs/gitignore][ official documentation]. 

