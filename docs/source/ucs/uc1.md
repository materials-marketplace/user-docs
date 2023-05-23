# Implementation of Use Case 1 into the MarketPlace framework

This documentation explains how the software SimPARTIX is incorporated within the MarketPlace. In detail, this manual provides an overview on most of the function having been created in this Use Case and the manual should serve as a detailed explanation on how to onboard your very own software in the MarketPlace. In the end, we aim at having the "SimPARTIX app". 

Everything is organized within one folder (the parent folder) and we will slowly go through each folder and file therein. In this Use Case, the software SimPARTIX is included. Please follow along each this guide and replace SimPARTIX mentally with your own software in mind and add the corresponding scripts and functions where necessary. 
In the end of this tutorial, you should have the following files and folder in your working directory

- [Folder] [simpartix](#including-your-own-software)
- [Folder] [simulation_controller](#the-simulation-controller-folder)
- [.gitmodules](#including-your-own-software)
- [app.py](#apppy)
- [docker-compose.yml](#docker-composeyml)
- [Dockerfile](#dockerfile)
- [openAPI.yml](#openapiyml)
- [requirements.txt](#requirementstxt)

Furthermore, optionally to you, we also have the following two files in the folder. 
- [.pre-commit-config.yaml](#pre-config)
- [.gitignore](#gitignore-file)

We will first start with including the own software and then gradually move on to understanding how to provide the software on the MarketPlace. 

## Including your own software

In a first step, the own software should be made available in the folder. In our case, we host SimPARTIX on Gitlab and thereby use Git as version control system. Using the [git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules) commands, we added
our software to the folder. This procedure allows us to keep the own software up to date easily as frequent changes in the source code are expected in order to implement new routines for the communication in MarketPlace. 

The result of this procedure are 
- [Folder] simpartix
- .gitmodules

Please read through the git submodule documentation if you are not familiar with it. 

## The simulation controller folder

Now we are working on the folder "simulation_controller" which contains several files that provide the functions to create, start and stop a simulation as well as retrieving the simulation results. The converter function to convert the SimPARTIX results to MICRESS input files are also placed here. 

Let us have a look at the following list of files that are all found in the folder "simulation_controller"
- \_\_init\_\_.py
- config.py
- propartix_files_creation.py
- simpartix_output.py
- SimPARTIXOutput.json
- simulation_manager.py
- simulation.py


### \_\_init\_\_.py

The file "\_\_init\_\_.py" is an empty file and its only purpose is that python allows to include all functions via the regular package syntax as libraries. Hence in all files, we can include classes and functions of other files with simple commands. Usually, python has no problem to import a whole directory. But when it comes to importing a specific class from a file in a directory, this will raise an exception. But having such a "\_\_init\_\_.py" file allows to use the following notation

```python
from directory.filename import classname
```

when having a class "classname" in a file "filename" within the directory "directory". We will use this commands 
to a great extend in the following files. 


### config.py

In this file, we have defined two classes, "SimulationStatus" and "SimulationConfig", and additionally we provide a definition for the simulation states. Here, we define 5 different kinds of simulation states that are
- created
- running
- completed
- stopped
- error
These 5 states were found to cover all situation. 

The corresponding class structure looks as follow
```python
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
By writing "Enum" into the bracket, this class is inheriting from the Enum class which is a built-in class from python. The aim of using this class is to ask whether a simulation is still running or whether an error occurred. 
In fact, we can apply the following notation
```python
state = SimulationStatus.CREATED # which is equal to "CREATED"
# and then ask for that state by
if state == SimulationStatus.CREATED:
    print('simulation has been created')
```
which is a readable syntax to ask for the state of a simulation. It follows the simulation configuration. 
This class structure serves as holding the input parameter that the user
provided to the SimPARTIX app. 

```python
import logging
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
This is a class that contains only an init method. This is the function that is called whenever an instance of the 
SimulationConfig class is created. Basically, this function receives the input parameters that are made available for
the Use Case 1 tutorial. These were
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
asks if there is a key with the name "configuration" in the dictionary "request_obj". If the key is present, its value is returned (that is the value that the user has provided in the MarketPlace interface - to be explained later). If the key has not been defined, we use the default value of "1". This value for the configuration is mapped to an integer
and stored in the variable "self.configuration" to make it available within the instant of the SimulationConfig
object. 

The same procedure is done for the other parameters. Additionally, we applied some checks to make sure
the user input variables are in a physically valid range. For example, the filling fraction "phi" cannot be smaller 
than 0 as there would be no powder to melt or higher as 1 as 1 means everything is filled with powder and we
cannot have a filling fraction higher than 100%. 

Furthermore, we added the logging module at the beginning of the snippet. This is a python in-built library that simplifies to write log files in which error messages are written to. This allows for example to write error messages

```python
logging.error("This is my error message")
```
or info messages
```python
logging.info("This is my info message")
```

Additionally, the file also contains the following two lines of code

```python
# Global Constant to define the extension of zip files
ZIP_EXTENSION = "zip"

# Global constant to define the path of the folder where all the simulations are saved
SIMULATIONS_FOLDER_PATH = "/app/simulation_files"
```
Which could also occur somewhere else and defines global constants which are the folder path in which
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

    foldername : string
        The folder name in which die input file should be created

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
how the output of the SimPARTIX simulation can be converted to a MICRESS input. 

The function "get_output_values" gathers all necessary information that MICRESS needs and 
puts all of them into a dictionary so that the results can be called by using keys. The function "create_micress_files" actually creates the file itself which in this case is a vtk file. 

All functions in this file have to be tailored to the specific use case. 


### simpartix_output.py and SimPARTIXOutput.json

The pieces of information that need to be transferred between SimPARTIX and MICRESS are temperature, a quantity called group which is the ID of each powder element, and state of matter which describes whether this specific
part of the powder is still solid, liquid or vaporous. 

This file "simpartix_output.py" only contains a class with the following content
```python
class SimPARTIXOutput:
    def __init__(self, temperature, group, state_of_matter):
        self.temperature = temperature
        self.group = group
        self.state_of_matter = state_of_matter
```
This class is hence able to hold the data of interest of the simulation result. 
The class definition goes hand in hand with the file "SimPARTIXOutput.json" that is explained next. 
At this stage, the mapping of the SimPARTIX quantities temperature, group and state_of_matter
to ontology concepts is started. In order to make the data of an SimPARTIX output available to other programs, it needs a description of the data that we provide in the file "SimPARTIXOutput.json". In this case, we apply a json file to provide this description. For each of the properties of interest (temperature, group and state of matter), we apply a "properties" field in which we provide the corresponding names of the field, the unit and the dimensions as well as a description. 

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
        "name": "temperature",
        "type": "float",
        "unit": "Kelvin",
        "dims": ["X", "Z"],
        "description": "List of temperature cells."
      },
      {
        "name": "group",
        "type": "int",
        "dims": ["X", "Z"],
        "description": "List of group (i.e. grain) cells."
      },
      {
        "name": "state_of_matter",
        "type": "int",
        "dims": ["X", "Z"],
        "description": "List of state of matter (i.e. phase) cells."
      }
    ]
}
```


### simulation_manager.py

We continue with the file "simulation_manager.py" where we directly continue with linking the quantities of the simulation to the ontology. In this Use Case we apply the [EMMO](https://emmc.eu/news/emmo-new-name-and-logo/) ontology, but other ontologies are equally applicable at this
stage. This is realized by simple dictionary. 

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
Obviously, we apply a nested dictionary. Please note at this point, that we have provided a name to our mapping that we called "SimpartixOutput". If you want to provide further options for mapping, this can easily be done by another dictionary within the mappings dictionary. 

The remaining part of the script can be copied directly and needs only few adoptions.
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

Most of the functions are self-explanatory. One function, the get_simulation_output function, will need some adoptions however. This function should return the simulation results, but additionally it should also provide the _mapping_ to map the result names to the ontology and the _mimetype_ that is the file type (dlite in your case).


### simulation.py

This is one of the more complex files and hence will be described more in detail. At the beginning, the necessary libraries are imported
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
- Tuple from tying is imported. In the function declaration, the return type of the data is also provided. Tuple is a built-in data type of python, but in the current version of python, this data type must be imported in order to be provided as return type. 
- _dlite_ is a C implementation of the SINTEF Open Framework and Tools which is a set of concepts and tools for using data models to efficiently describe and work with scientific data. 

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

It follows the Simulation class which is given in its completeness first to the sake of simplified copy and paste and afterwards each of its functions is explained more in detail
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
In the init method, the unique ID is created ("uuid.uuid4()") and stored as internal variable "job_id". Based on this ID, a unique simulation folder path is created based on the parent folder PATH that was defined in the file "config.py". 
Next, the function "create_input_files" from the file "propartix_files_creation" is called. This was again a function unique to SimPARTIX in which the start configuration is created and hence that must be written individually for each new simulation software. 
Last but not least, the status of the simulation is set to "created" and the corresponding
pieces of information are written to the log file. 


The simulation itself is started by the following function
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
the user accidentally clicks multiple times on the "run" button. 
Next, the output path is defined and created which in this case simply is called "output"
Then, the change into that directory in which the simulation is to be executed and then 
start calling "SimPARTIX" as subprocess. This is like having a terminal and typing 
"SimPARTIX" into that terminal. Finally, the state of the simulation is set to 
"running" and the corresponding info message is written to the log file. 
If you script has to be called via another command, the corresponding 
command has to be written where "SimPARTIX" is written in third last line. 


```python
@property #dea
def status(self) -> SimulationStatus:
    """Getter for the status.

    If the simulation is running, the process is checked for completion.

    Returns:
        SimulationStatus: status of the simulation
    """
    if self._status == SimulationStatus.RUNNING:
        process_status = self.process.poll() #dea
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
This piece of code checks if the simulation is still running. The idea behind this function is that first we check for the flag "SimulationStatus.RUNNING" as the simulation
cannot be running otherwise. If the simulation was declared as running the last time, 
we check again. We remember that the simulation resource when starting the simulation
was stored in the variable _self.process_. This allows us to check if there is still a running
resources behind _self.process_.
This is done by self.process.poll(). This function does not work on all 
operating system, but on Linux it can be used to screen for I/O events that would occur during 
the simulation. 

This function is realized via a property decorator in the first line. Usually, the function needs to be called via 
```python
Simulation.status()
```
with opening and closing bracket. Adding '@property' allows to use the following notation
```python
Simulation.status
```
without the opening and closing bracket. This allows to use a notation in which it seems that we directly access the attribute _status_ but actually we call the getter function _status()_ instead. 


It follows a list of further setter and getter to set the simulation or process status.
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
Similarly to the _@property_ decorator, _@status.setter_ is another decorator that serves the same purpose like _@property_ but just to realize a setter function. Here, the first word in _@status.setter_ is the function name, followed by a period, followed by the key word _setter_. 


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
    self.process.terminate() #dea how does this work
    self.status = SimulationStatus.STOPPED
    self.process = None
    logging.info(f"Simulation '{self.job_id}' stopped successfully.")
```
This function first checks if the processes to be stopped is actually running as it cannot be stopped otherwise and raises an error message if it is not running. 
If the process is running, it is stopped by _self.process.terminate()_
and the accompanying flags _self.status_ and _self.process_ are set. 

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

This function first checks if a simulation has stopped running. If it not running, the data is 
simply deleted using the "rmtree" function of the shutil library. This library is a built-in-library
of python that can be used to delete folders. 

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

This function works as follows. First, 
```python
result = get_output_values(self.simulationPath)
```
get the dictionary _result_ so that each piece of result can be called by using keys. Now, an empty dlite object is created. In the init method of that class we provide the object _SimPARTIXOutput_ the content of which is displayed here again
```python
class SimPARTIXOutput:
    def __init__(self, temperature, group, state_of_matter):
        self.temperature = temperature
        self.group = group
        self.state_of_matter = state_of_matter
```
This class can hold the data for each attribute (temperature, group and state of matter). 

After a check that the simulation has actually finished, the data in the _result_ dictionary is fed into the dlite simpartix output object. One instance of the dlite object is saved to a file and another one is returned back by the function. 





## app.py

This is a function that is actually called. 

```python
import json
import logging
import mimetypes #dea file type
import os
from pathlib import Path

from flask import Flask, Response, request

from simulation_controller.simulation_manager import (
    SimulationManager,
    mappings,
)
```

In a first step, we load the main libraries. 
mimetype
flask 
pathlib -> Path




xxx

```python
app = Flask(__name__) #dea
app.secret_key = FLASK_SECRET_KEY

simulation_manager = SimulationManager()
```


It follows the "heartbeat" function. 
```python
@app.route("/heartbeat") #dea
def heartbeat():
    return Response(
        "SimPARTIX-App : application running.",
        status=200,
        mimetype="text/plain",
    )
```

This function can be used by the MarketPlace server in order to check if the SimPARTIX app is still running
or whether it got stopped. This function returns a flask response object with a string "SimPARTIX-App : application running"
as text that will be displayed, a status of 200 which is the commonly accepted value that everyting is okay. 

xxx
```python
@app.route("/initialize", methods=["POST"])
def new_simulation() -> str:
    try:
        request_obj = request.get_json()
        job_id = simulation_manager.create_simulation(request_obj)
        payload = {"id": job_id}
        return Response(json.dumps(payload), status=200, mimetype="application/json")
    except ValueError as ve:
        return Response(str(ve), status=400)
    except Exception as e:
        msg = (
            "Unexpected error while creating simulation "
            f"with config: {request_obj}. Error message: {e}"
        )
        logging.error(msg)
        return Response(str(msg), status=400, mimetype="text/plain")
```

xxx
```python
@app.route("/update/<transformation_id>", methods=["PATCH"])
def update_simulation_state(transformation_id: str):
    state = json.loads(request.get_json()).get('state')
    try:
        if state == "RUNNING":
            simulation_manager.run_simulation(transformation_id)
        elif state == "STOPPED":
            simulation_manager.stop_simulation(transformation_id)
        else:
            msg = f"{state} is not a supported state."
            return Response(msg, 400, mimetype="text/plain")
        response = {"id": transformation_id, "state": state}
        return Response(
            json.dumps(response),
            status=200,
            mimetype="application/json",
        )
    except KeyError as ke:
        return Response(str(ke), status=404)
    except RuntimeError as re:
        return Response(str(re), status=400)
    except Exception as e:
        msg = (
            "Unexpected error while changing state of simulation "
            f"{transformation_id}. Error message: {e}"
        )
        logging.error(msg)
        return Response(msg, status=400)
```

xxx

```python
@app.route("/<transformation_id>/state", methods=["GET"])
def get_simulation_state(transformation_id: str):
    try:
        state = simulation_manager.get_simulation_state(transformation_id)
        response = {"id": transformation_id, "state": str(state)}
        return Response(
            json.dumps(response),
            status=200,
            mimetype="application/json",
        )
    except KeyError as ke:
        return Response(str(ke), status=404)
    except Exception as e:
        msg = (
            "Unexpected error while querying for the status of simulation "
            f"{transformation_id}. Error message: {e}"
        )
        logging.error(msg)
        return Response(msg, status=400)
```


xx
```python
@app.route("/", methods=["GET"])
def get_simulation_list():
    try:
        simulation_list: list = simulation_manager.get_simulation_list()
        logging.info(f"simulation list: {simulation_list}")
        return Response(
            response=json.dumps(simulation_list),
            status=200,
            mimetype="application/json",
        )
    except Exception as e:
        msg = (
            "Unexpected error while fetching the list of simulations. "
            f"Error message: {e}"
        )
        logging.error(msg)
        return Response(msg, status=400)
```


xxx
```python
@app.route("/<transformation_id>", methods=["DELETE"])
def delete_simulation(transformation_id: str):
    try:
        simulation_manager.delete_simulation(transformation_id)
        return Response(
            f"Simulation '{transformation_id}' deleted successfully!",
            status=200,
            mimetype="text/plain",
        )
    except KeyError as ke:
        return Response(str(ke), status=404)
    except RuntimeError as re:
        return Response(str(re), status=400)
    except Exception as e:
        msg = (
            "Unexpected error while deleting simulation "
            f"{transformation_id}. Error message: {e}"
        )
        logging.error(msg)
        return Response(msg, status=400)
```

xxx

```python
@app.route("/datasets", methods=["GET"])
def get_results():
    dataset_name = request.args.get("dataset_name")
    json_payload, mapping, mimetype = simulation_manager.get_simulation_output(
        dataset_name
    )
    headers = {"x-semantic-mappings": mapping}
    return Response(
        response=json_payload,
        status=200,
        mimetype=mimetype,
        headers=headers,
    )
```

xxx

```python
@app.route("/mappings", methods=["GET"])
def list_mappings():
    return Response(
        response=json.dumps(list(mappings.keys())),
        status=200,
        mimetype="application/json",
    )
```

xxx

```python
@app.route("/mappings/<semantic_mapping_id>", methods=["GET"])
def get_mapping(semantic_mapping_id: str):
    mapping = json.dumps(mappings.get(semantic_mapping_id))
    if not mapping:
        return Response("Mapping not found", status=404)
    return Response(
        response=mapping,
        status=200,
        mimetype="application/json",
    )

```

The file ends with the following line of code

```python
if __name__ == "__main__":
    app.run()
```

This piece of code is a kind of safety check that the function "app.run()" is only called when this scrip "app.py" is actually being called. It is also possible to load this script from somewhere else via "import app" if one of the functions should be use elsewhere and in this case, the function "run()" should not be called. 


## requirements.txt

The requirements file is an ordinary ascii file that contains those python libraries that are necessary somewhere in our python scripts. Some libraries are already installed elsewhere (explained [here](#dockerfile)), but several further libraries are necessary for the web communication. These libraries and more specific also the version of this library is defined in following manner

```
flask == 2.1.2
requests-oauthlib == 1.3.1
DLite-Python == 0.3.9
```

"Flask" is necessary for the web communication, "requests-oauthlib" handles the authorization and "DLite-Python" is a file format provided by Sintef to facilitate the communication of data between the software modules. 


## openAPI.yml

```yml
---
openapi: 3.0.0

info:
    title: SimPARTIX
    description: MarketPlace app for the SimPARTIX simulation software
    version: 1.0.5
    x-api-version: 0.3.0
    x-products:
        - name: Monthly
          productId:
servers:
    - url: https://simpartix.materials-data.space

paths:
# Administrative paths
    /heartbeat:
        get:
            security:
                - bearerAuth: []
            description: Returns a heartbeat
            operationId: heartbeat
            responses:
                '200':
                    description: Success

# Transformation app paths
    /initialize:
        post:
            security:
                - bearerAuth: []
            description: Initialize a Transformation
            operationId: newTransformation
            requestBody:
                required: true
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/TransformationConfig'
            responses:
                '200':
                    description: Success
                    content:
                        resourceId:
                            schema:
                                type: string
                                example: 3e22541c-a95e-4443-8cdc-0866171d343b
                '400':
                    description: Bad Request
                    content:
                        resourceId:
                            schema:
                                type: string
                                example: Wrong configuration input

    /{transformation_id}/state:
        get:
            security:
                - bearerAuth: []
            description: Get the state of a Transformation
            operationId: getTransformationState
            parameters:
                - in: path
                  name: transformation_id
                  schema:
                      type: string
                  required: true
            responses:
                '200':
                    description: Success
                    content:
                        state:
                            schema:
                                type: string
                                example: running
                '404':
                    description: Not found
                    content:
                        resourceId:
                            schema:
                                type: string
                                example: Simulation Not found
                '400':
                    description: Bad Request
                    content:
                        resourceId:
                            schema:
                                type: string
                                example: Unexpected error

    /{transformation_id}:
        delete:
            security:
                - bearerAuth: []
            description: Delete the transformation
            operationId: deleteTransformation
            parameters:
                - in: path
                  name: transformation_id
                  schema:
                      type: string
                  required: true
            responses:
                '200':
                    description: Success
                    content:
                        status:
                            schema:
                                type: string
                                example: Deleted successfully
                '404':
                    description: Not found
                    content:
                        resourceId:
                            schema:
                                type: string
                                example: Simulation Not found
                '400':
                    description: Bad Request
                    content:
                        resourceId:
                            schema:
                                type: string
                                example: Simulation is in progress
    /update/{transformation_id}:
        patch:
            security:
                - bearerAuth: []
            description: Update the transformation state
            operationId: updateTransformation
            parameters:
                - in: path
                  name: transformation_id
                  schema:
                      type: string
                  required: true
            requestBody:
                required: true
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/TransformationUpdate'
            responses:
                '200':
                    description: Success
                    content:
                        status:
                            schema:
                                type: string
                                example: Stopped successfully
    /:
        get:
            security:
                - bearerAuth: []
            description: Get the List of Simulations
            operationId: getTransformationList
            responses:
                '200':
                    description: Success
                    content:
                        application/json:
                            schema:
                                type: array
                                items:
                                    type: string
                                    example: [SimulationID-1, Simulation-2, '...']

    # dataSource endpoints
    /datasets:
        get:
            security:
                - bearerAuth: []
            description: Get the simulation results (DLite json)
            operationId: getDataset
            parameters:
                - in: query
                  name: dataset_name
                  schema:
                      type: string
                  required: true
            responses:
                '200':
                    description: Success
                    content:
                        '*/*':
                            schema:
                                type: object
                '404':
                    description: Not found
                    content:
                        resourceId:
                            schema:
                                type: string
                                example: Simulation not found
                '400':
                    description: Bad Request
                    content:
                        resourceId:
                            schema:
                                type: string
                                example: Simulation is in progress

    /mappings:
        get:
            security:
                - bearerAuth: []
            description: Get the list semantic mappings
            operationId: listSemanticMappings
            responses:
                '200':
                    description: Success
                    content:
                        '*/*':
                            schema:
                                type: object

    /mappings/{semantic_mapping_id}:
        get:
            security:
                - bearerAuth: []
            description: Get a specific semantic mapping set
            operationId: getSemanticMapping
            parameters:
                - in: path
                  name: semantic_mapping_id
                  schema:
                      type: string
            responses:
                '200':
                    description: Success
                    content:
                        '*/*':
                            schema:
                                type: object
                '404':
                    description: Not found
                    content:
                        resourceId:
                            schema:
                                type: string
                                example: Semantic mapping Not found

components:
    securitySchemes:
        bearerAuth:
            type: http
            scheme: bearer
            bearerFormat: JWT
    schemas:
        TransformationConfig:
            title: TransformationConfig
            required:
                - Configuration
            type: object
            properties:
                laserStrength:
                    title: laserStrength
                    type: integer
                laserSpeed:
                    title: laserSpeed
                    type: number
                configuration:
                    title: Configuration
                    type: integer
                sphereDiameter:
                    title: sphereDiameter
                    type: number
                phi:
                    title: phi
                    type: number
                powderLayerHeight:
                    title: powderLayerHeight
                    type: number
            description: Transformation data model
        TransformationUpdate:
            title: TransformationUpdate
            required:
                - state
            type: object
            properties:
                state:
                    title: state
                    type: string
            description: Transformation update model
```





## Dockerfile

The SimPARTIX app is actually running within a docker container. [Docker](https://www.docker.com/) is a powerful tool to provide a well defined architecture with all necessary libraries. The docker file provided below is the instruction to build up a so called image in which all programs (such as python) and libraries (such as the python libraries) are defined. We build up this image based on a already present image that exist for SimPARTIX and which is hosted on the Fraunhofer own [docker image repository](ub.cc-asp.fraunhofer.de). 
In this image, the libraries for SimPARTIX and ProPARTIX are already included such as numpy, pandas etc while applying the very same strategy as explained in this section. This is the reason for which they have not to be included again in the file [requirements.txt](#requirementstxt) again. If you are unfamiliar with docker, continue first with one of the vast options for docker tutorial. Docker has a steep learning curve though. 

We provide the content of our docker file and describe its content afterwards


```dockerfile
FROM hub.cc-asp.fraunhofer.de/simpartixpublic/simpartix:03

# add source code from the repository that includes all source files
ADD simpartix /source
WORKDIR /source/code
RUN make -j 4
WORKDIR /source/ProPARTIX/code
RUN make
ENV PATH="${PATH}:/source/code/"
ENV PYTHONPATH "${PYTHONPATH}:/source/ProPARTIX/code"
ENV PROPARTIXPATH "/source/ProPARTIX/code"
WORKDIR /app #dea
# To store the files from the simulations
RUN mkdir simulation_files
ENV FLASK_APP=app.py #dea
ENV PORT=5000
ADD simpartix ./simpartix #dea
ADD simulation_controller ./simulation_controller
ADD static ./static
ADD requirements.txt .
ADD app.py .
RUN pip install -r requirements.txt

CMD flask run --host=0.0.0.0 --port=${PORT}
```

In a first step, we load the SimPARTIX image from the Fraunhofer repository to have a base with all functionalities available that are required by SimPARTIX and ProPARTIX. This however does not include the software itself, but only the libraries.
In the following, we add the "simpartix" folder to the image (see again [here](#including-your-own-software)) as a git submodule. In the image, the simpartix folder is however called "source". We change into that directory and there into a "code" folder where we put out files with which the SimPARTIX binary is compiled. Calling "RUN make -j 4" compiles the SimPARTIX binary. Similarly, we change into the ProPARTIX folder and compile here the files that are necessary for the ProPARTIX engine. At this point, the SimPARTIX binary and ProPARTIX functions are all present. 

In the following, paths to the SimPARTIX binary and to the ProPARTIX functions are added to the main path as well as to the python path. 

The simulation results are supposed to be stored in a folder called "simulation_files". This folder is hence created next. 

The web communication needs to have port number to which it is listening. This port number is an arbitrary number, but it needs to be defined. 



## docker-compose.yml


```yml
---
version: '3.6'

services:

    simpartix_app:
        build: .
        environment:
            - MARKETPLACE_HOST
        secrets:
            - client_id
            - client_secret
            - flask_secret
        ports:
            - 8000:5000

secrets:
    client_id:
        file: ./secrets/client_id
    client_secret:
        file: ./secrets/client_secret
    flask_secret:
        file: ./secrets/flask_secret

```


## prepare_deployment.sh

```bash
set -e
set -u

source .env
export FLASK_SECRET_KEY=$(openssl rand -base64 24)
echo -n $CLIENT_ID > secrets/client_id
echo -n $CLIENT_SECRET > secrets/client_secret
echo -n $FLASK_SECRET_KEY > secrets/flask_secret

```






## Explanation of the optional files

### pre config

There is a tool called "pre-commit" that allows to perform checks on the source code prior to pushing them to the repository. If you are interested in such a tool, follow the explanation on [this website](https://pre-commit.com). The result of this procedure is file called "pre-commit-config.yaml".


### gitignore file ###

One best practice when using coding is to apply version control to keep track of your changes in the source code. One such version control system is git. A gitignore file allows to have files in your working directory that 
should not be tracked by git. For more information, please follow the [official documentation](https://git-scm.com/docs/gitignore). 

