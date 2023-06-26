# Implementation of Use Case 1

This documentation explains how the software SimPARTIX is installed at the MarketPlace. In detail, this manual provides an overview on most of the functions that were created for this Use Case and the manual should serve as a detailed explanation on how to onboard your very own software at the MarketPlace. In the end, we aim at having the "SimPARTIX application" or "SimPARTIX app" which should allow to access SimPARTIX via the MarketPlace. The purpose of this manual is to provide guidance of programmers that know how to handle their simulation software and that are now facing the challenge to bring their software onto the MarketPlace.

All files are organized within one folder (the parent folder) and we will slowly go through each folder and each file therein. In this Use Case, the software SimPARTIX is included. Please follow along with this guide and replace SimPARTIX mentally with your own software in mind and add the corresponding scripts and functions where necessary.
In the end of this tutorial, you should have the following files and folder in your working directory

- [Folder] [simpartix](#including-your-own-software)
- [Folder] [simulation_controller](#the-simulation-controller-folder)
- [Folder] [models](#models)
- [app.py](#apppy)
- [.gitmodules](#including-your-own-software)
- [docker-compose.yml](#docker-composeyml)
- [Dockerfile](#dockerfile)
- [openAPI.yml](#openapiyml)
- [requirements.txt](#requirementstxt)

Furthermore, optionally to you, we also have the following two files in the folder.

- [.pre-commit-config.yaml](#pre-config)
- [.gitignore](#gitignore-file)

We will first start with including the own software and then gradually move on to understanding how to provide the software on the MarketPlace.

## Including your own software

In a first step, the own software should be made available. In our case, we host SimPARTIX on GitLab and use Git as version control system. Using the git submodule commands, we added
our software to the folder. This procedure allows us to keep the own software up to date easily as frequent changes in the source code are expected in order to implement new routines for the communication in MarketPlace.

The result of this procedure are

- [Folder] simpartix with the source code for SimPARTIX
- a file .gitmodules that was created by git

Please read through the [git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules) documentation if you are not familiar with it.

## The simulation controller folder

Now we are working on the folder "simulation_controller" which contains several files that provide the functions to create, start and stop a simulation as well as retrieving the simulation results.
The converter function to convert the SimPARTIX results to MICRESS input files are also placed here. These functions will be called by the SimPARTIX app via the RestAPI.

Let us have a look at the following list of files that are all found in the folder "simulation_controller"

- \_\_init\_\_.py
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
to a great extend in the following files in order to import classes from specific files, two of mich are presented in the next chapter.

### propartix_files_creation.py

This file is tailored to SimPARTIX and it uses the function that are provided by SimPARTIX to create
the start configurations. The python engine of SimPARTIX is ProPARTIX which is the reason
for the file name. This file has the following structure.

```python
import os
import numpy as np
import propartix as px

from models.transformation import TransformationInput

def create_input_files(foldername: str, simulation_input: TransformationInput):
    """
    Function to create the start configuration for the MarketPlace simulation.

    simulation_input : TransformationInput
        instance with the specific configuration values for a run
    """
    # it follows a list of code lines specific to ProPARTIX to create the
    # start configuration
```

This function "create_input_files" has the function to create the start configuration as well as to create the input files that are necessary for the simulation. To fullfil this task, it needs to have access to the input parameter that the user has requested on the web page. These parameters are shifted within the variable "simulation_input". The parameters can be accessed similar as class attributes. For example, if the user has requested a certain sphere diameter, this respected value can be obtained by
```python
simulation_input.sphereDiameter
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

The pieces of information that need to be transferred between SimPARTIX and MICRESS are temperature, a quantity called group which is the ID of each powder element, and state of matter which describes whether this specific part of the powder is still solid, liquid or vaporous.

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
to ontology concepts is started. This is what is referred to as Level 2 integration on the MarketPlace that should provide a clear description on the data. In order to make the data of an SimPARTIX output available to other programs, it needs a description of the data that we provide in the file "SimPARTIXOutput.json". In this case, we apply a json file to provide this description. For each of the properties of interest (temperature, group and state of matter), we apply a "properties" field in which we provide the corresponding names of the field, the unit and the dimensions as well as a description.

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
stage. This is realized by a simple dictionary.

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

Obviously, we apply a nested dictionary. Please note at this point that we have provided a name to our mapping that we called "SimpartixOutput". If you want to provide further options for mapping, this can easily be done by another dictionary within the mappings dictionary. In this case, we only have one mapping, but applying the nested dictionary allows to to allow further mapping in future if necessary. 

The remaining part of the script can be copied directly and needs only few adoptions.

```
import logging

from marketplace_standard_app_api.models.transformation import (
    TransformationState,
)

from simulation_controller.simulation import Simulation


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
        simulation = self._get_simulation(job_id)
        return simulation.get_output()

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

    def get_simulation_state(self, job_id: str) -> TransformationState:
        """Return the status of a particular simulation.

        Args:
            job_id (str): id of the simulation

        Returns:
            TransformationState: status of the simulation
        """
        return self._get_simulation(job_id).status

    def get_simulations(self) -> dict:
        """Return unique ids of all the simulations.

        Returns:
            list: list of simulation ids
        """
        items = []
        for simulation in self.simulations.values():
            items.append(
                {
                    "id": simulation.job_id,
                    "parameters": simulation.parameters,
                    "state": simulation.status,
                }
            )
        return items
```

### simulation.py

This file represents a unique simulation run.
It is one of the more complex files and hence will be described more in detail. At the beginning, the necessary libraries are imported

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

- logging -> allows to keep track of error messages
- os, shutil, subprocesses -> to create new directories, copy files and start the simulation software SimPARTIX
- uuid -> a useful library to assign unique IDs to the simulation
- Tuple from tying is imported. In the function declaration, the return type of the data is also provided. Tuple is a built-in data type of python, but in the current version of python, this data type must be imported in order to be provided as return type.
- dlite is a C implementation of the SINTEF Open Framework and Tools which is a set of concepts and tools for using data models to efficiently describe and work with scientific data.

We also import the following classes and function from our previously created files

```python
from marketplace_standard_app_api.models.transformation import (
    TransformationState,
)

from models.transformation import TransformationInput
from simulation_controller.propartix_files_creation import (
    create_input_files,
    get_output_values,
)
from simulation_controller.simpartix_output import SimPARTIXOutput
```

Special notes should be made for 
```python
from marketplace_standard_app_api.models.transformation import TransformationState
```
which imports the class "TransformationState". This class holds the MarketPlace internal stati which will be used in the following to ask whether a simulation is still running, has ended already, or has stopped with error messages. Examples on this class are provided further below. 


It follows the "Simulation" class which is given in its completeness first to the sake of simplified copy and paste and afterwards each of its functions is explained more in detail

```python
SIMULATIONS_FOLDER_PATH = "/app/simulation_files"

```

It follows the detailed explanation

```python
def __init__(self, simulation_input: TransformationInput):
    self.job_id: str = str(uuid.uuid4())
    self.simulationPath = os.path.join(
        SIMULATIONS_FOLDER_PATH, self.job_id
    )
    create_input_files(self.simulationPath, simulation_input)
    self.parameters = simulation_input
    self._status: TransformationState = TransformationState.CREATED
    self._process = None
    logging.info(
        f"Simulation '{self.job_id}' with "
        f"configuration {simulation_input} created."
    )
```

In the init method, the unique ID is created ("uuid.uuid4()") and stored as internal variable "job_id". Based on this ID, a unique simulation folder path is created based on the parent folder. Next, the function "create_input_files" from the file "propartix_files_creation" is called. This was again a function unique to SimPARTIX in which the start configuration is created and hence that must be written individually for each new simulation software. Last but not least, the status of the simulation is set to "created" and the corresponding
pieces of information are written to the log file. This is the first example that shows how to make use of MarketPlace class Transformation States to describe the state of the simulation. 

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
    if self.status == TransformationState.RUNNING:
        msg = f"Simulation '{self.job_id}' already in progress."
        logging.error(msg)
        raise RuntimeError(msg)
    outputPath = os.path.join(self.simulationPath, "output")
    if not os.path.isdir(outputPath):
        os.mkdir(outputPath)
    os.chdir(self.simulationPath)
    self.process = subprocess.Popen(["SimPARTIX"], stdout=subprocess.PIPE)
    self.status = TransformationState.RUNNING
    logging.info(f"Simulation '{self.job_id}' started successfully.")
```

This function first checks if a simulation with that ID is already running like in the case that the user accidentally clicks multiple times on the "run" button. Next, the output path is defined and created which in this case is simply called "output" Then, we change into that directory in which the simulation is to going to be executed and then start calling "SimPARTIX" as subprocess. This is like having a terminal and typing "SimPARTIX" into that terminal. Finally, the state of the simulation is set to "running" and the corresponding info message is written to the log file. If your script has to be called via another command, the corresponding command has to be written where "SimPARTIX" is written in third last line.

```python
@property
def status(self) -> TransformationState:
    """Getter for the status.

    If the simulation is running, the process is checked for completion.

    Returns:
        TransformationState: status of the simulation
    """
    if self._status == TransformationState.RUNNING:
        process_status = self.process.poll()
        if process_status is None:
            return TransformationState.RUNNING
        elif process_status == 0:
            logging.info(f"Simulation '{self.job_id}' is now completed.")
            self.status = TransformationState.COMPLETED
        else:
            logging.error(f"Error occured in simulation '{self.job_id}'.")
            self.status = TransformationState.FAILED
    return self._status
    ```

This piece of code checks if the simulation is still running. The idea behind this function is that first we check for the flag "TransformationState.RUNNING" as the simulation cannot be running otherwise. If the simulation was declared as running the last time, we check again. We remember that the simulation resource when starting the simulation was stored in the variable _self.process_. This allows us to check if there is still a running resources behind _self.process_. This is done by _self.process.poll()_. This function does not work on all operating system, but on Linux it can be used to screen for I/O events that would occur during the simulation.

This function is written with a property decorator in the first line. Usually, a function needs to be called with opening and closing bracket, i.e.

```python
Simulation.status()
```

Adding '@property' allows to use the following notation

```python
Simulation.status
```

without the opening and closing bracket. This allows to use a notation in which it seems that we directly access the attribute _status_ but actually we call the getter function _status()_ instead.

It follows a list of further setter and getter to set the simulation or process status.

```python
@status.setter
def status(self, value: TransformationState):
    self._status = value

@property
def process(self):
    return self._process

@process.setter
def process(self, value):
    self._process = value
```

Similarly to the _@property_ decorator, _@status.setter_ is another decorator that serves the same purpose like _@property_ but just to realize a setter function. Here, the first word in _@status.setter_ is the function name, followed by a period, followed by the keyword _setter_.

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
    self.status = TransformationState.STOPPED
    self.process = None
    logging.info(f"Simulation '{self.job_id}' stopped successfully.")
```

This function first checks if the processes to be stopped is actually running as it cannot be stopped otherwise and raises an error message if it is not running. If the process is running, it is stopped by _self.process.terminate()_ and the accompanying flag _self.status_ is set. Furthermore, the process of running the simulation is stopped by calling terminate. 

Finally, the data of a simulation can be deleted by the following function

```python
def delete(self):
    """
    Delete all the simulation folders and files.

    Raises:
        RuntimeError: if deleting a running simulation
    """
    if self.status == TransformationState.RUNNING:
        msg = f"Simulation '{self.job_id}' is running."
        logging.error(msg)
        raise RuntimeError(msg)
    shutil.rmtree(self.simulationPath)
    logging.info(f"Simulation '{self.job_id}' and related files deleted.")
```

This function first checks if a simulation has already stopped running. If it is not running, the data is simply deleted using the "rmtree" function of the shutil library. This library is a built-in-library of python that can be used to delete folders.

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
        TransformationState.RUNNING,
        TransformationState.CREATED,
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

gets the dictionary _result_ so that each piece of result can be called by using keys. Now, an empty dlite object is created. In the init method of that class we provide the object _SimPARTIXOutput_ the content of which is displayed here again

```python
class SimPARTIXOutput:
    def __init__(self, temperature, group, state_of_matter):
        self.temperature = temperature
        self.group = group
        self.state_of_matter = state_of_matter
```

This class can hold the data for each attribute (temperature, group and state of matter).

After a check that the simulation has actually finished, the data in the _result_ dictionary is fed into the dlite simpartix output object. One instance of the dlite object is saved to a file and another one is returned back by the function.

## models

The folder models contains only one single file with the name "transformation.py". This script is used as an interface between the GUI and the SimPARITX app. Its content is

```python
from pydantic import BaseModel, validator


class TransformationInput(BaseModel):
    laserPower: float = 150
    laserSpeed: float = 3.0
    sphereDiameter: float = 30e-6
    phi: float = 0.7
    powderLayerHeight: float = 60e-6

    @validator("sphereDiameter")
    def check_diameter(cls, v):
        if v <= 5e-6:
            raise ValueError("Sphere diameter value too small.")
        return v

    @validator("phi")
    def check_phi(cls, v):
        if v >= 1 or v < 0:
            raise ValueError("Phi must be between 0 and 1.")
        return v

    @validator("powderLayerHeight")
    def check_powderLayerHeight(cls, v, values):
        if v < values["sphereDiameter"]:
            raise ValueError(
                "Powder layer height must be at least the sphere diameter."
            )
        return v

```

Here, we use a python built-in library pydantic to facilitate read in of input data while performing some basic checks if the input data is within an acceptable range. 

## app.py

This is a function that is actually called when building the docker image.  The handling of the web application is realized by FastAPI. Understanding this part requires knowledge on web communication. Creating the webpage is not part of this tutorial.

We start with importing the main libraries

```python
import json
import logging

from fastapi import FastAPI, HTTPException, Response

from marketplace_standard_app_api.models.transformation import (
    TransformationCreateResponse,
    TransformationId,
    TransformationListResponse,
    TransformationStateResponse,
    TransformationUpdateModel,
    TransformationUpdateResponse,
)

from marketplace_standard_app_api.routers import object_storage

from models.transformation import TransformationInput

from simulation_controller.simulation_manager import (
    SimulationManager,
    mappings,
)
```

It follows the common notation to create an instance of FastAPI.

```python
app = FastAPI()
```

We then create an object of the SimulationManger class.

```python
simulation_manager = SimulationManager()
```

In FastAPI, the endpoints are provided with the _@app_ decorator. We will hence see lines that start with this decorator throughout the script. Our first example is the _heartbeat_, a function that is used by MarketPlace to check whether the corresponding app itsel is running and can be called.  

```python
@app.get(
    "/heartbeat", operation_id="heartbeat", summary="Check if app is alive"
)
async def heartbeat():
    return "SimPARTIX app up and running"
```

This function returns a string saying that the application is running. 

We continue with the function to cate a new simulation which is called whenever the "submit" button it hit.

```python
@app.post(
    "/transformations",
    operation_id="newTransformation",
    summary="Create a new transformation",
    response_model=TransformationCreateResponse,
)
async def new_simulation(
    payload: TransformationInput,
) -> TransformationCreateResponse:
    job_id = simulation_manager.create_simulation(payload)
    return {"id": job_id}
```

This function retrieves the parameter set from the GUI that contains the values such as laser power, laser speed and the geometry of the powder bed. The "create_simulation" function from the simulation manager is called which was the SimPARTIX individual function to actually create all input files and the start configuration. 

We continue with the function to update the simulation state. This function actually initiates running the simulation or stopping of a simulation.

```python
@app.patch(
    "/transformations/{transformation_id}",
    summary="Update the state of the simulation.",
    response_model=TransformationUpdateResponse,
    operation_id="updateTransformation",
    responses={
        404: {"description": "Not Found."},
        409: {"description": "Requested state not available"},
        400: {"description": "Error executing update operation"},
    },
)
def update_simulation_state(
    transformation_id: TransformationId, payload: TransformationUpdateModel
) -> TransformationUpdateResponse:
    state = payload.state
    try:
        if state == "RUNNING":
            simulation_manager.run_simulation(str(transformation_id))
        elif state == "STOPPED":
            simulation_manager.stop_simulation(str(transformation_id))
        else:
            msg = f"{state} is not a supported state."
            raise HTTPException(status_code=400, detail=msg)
        return {"id": TransformationId(transformation_id), "state": state}
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Transformation not found: {transformation_id}",
        )

    except RuntimeError as re:
        raise HTTPException(status_code=409, detail=re)
    except Exception as e:
        msg = (
            "Unexpected error while changing state of simulation "
            f"{transformation_id}. Error message: {e}"
        )
        logging.error(msg)
        raise HTTPException(status_code=400, detail=msg)
```

The next function is used to retrieve the simulation state. This function simply calls the "get_simulation_state" function from the simulation manager and handles some commonly occurring error states.

```python
@app.get(
    "/transformations/{transformation_id}/state",
    summary="Get the state of the simulation.",
    response_model=TransformationStateResponse,
    operation_id="getTransformationState",
    responses={404: {"description": "Unknown simulation"}},
)
def get_simulation_state(
    transformation_id: TransformationId,
) -> TransformationStateResponse:
    """Get the state of a simulation.

    Args:
        transformation_id (TransformationId): ID of the simulation

    Returns:
        TransformationStateResponse: The state of the simulation.
    """
    try:
        state = simulation_manager.get_simulation_state(str(transformation_id))
        return {"id": transformation_id, "state": state}

    except KeyError:
        raise HTTPException(status_code=404, detail="Simulation not found")
    except Exception as e:
        msg = (
            "Unexpected error while querying for the status of simulation "
            f"{transformation_id}. Error message: {e}"
        )
        raise HTTPException(status_code=400, detail=msg)
```

The next function is used to retrieve a list of all simulations. This function, again, makes used of the core features provided in the simulation manager.

```python
@app.get(
    "/transformations",
    summary="Get all simulations.",
    response_model=TransformationListResponse,
    operation_id="getTransformationList",
)
def get_simulations():
    try:
        items: list = simulation_manager.get_simulations()

        logging.info(f"simulations: {items}")
        return {"items": items}
    except Exception as e:
        msg = (
            "Unexpected error while fetching the list of simulations. "
            f"Error message: {e}"
        )
        logging.error(msg)
        return Response(msg, status=400)
```

The next function "delete_simulation" provides the interface to the "delete_simulation" function of the simulation manager.

```python
@app.delete(
    "/transformations/{transformation_id}",
    summary="Delete a transformation",
    operation_id="deleteTransformation",
)
def delete_simulation(transformation_id: TransformationId):
    try:
        simulation_manager.delete_simulation(str(transformation_id))
        return {
            "status": f"Simulation '{transformation_id}' deleted successfully!"
        }

    except KeyError as ke:
        raise HTTPException(status_code=404, detail=ke)
    except RuntimeError as re:
        raise HTTPException(status_code=400, detail=re)
    except Exception as e:
        msg = (
            "Unexpected error while deleting simulation "
            f"{transformation_id}. Error message: {e}"
        )
        raise HTTPException(status_code=400, detail=msg)
```

There is also a function "get_results" to call the "get_simulation_output" function of the simulation manager.

```python
@app.get(
    "/results",
    summary="Get a simulation's result",
    operation_id="getDataset",
    responses={200: {"content": {"vnd.sintef.dlite+json"}}},
)
def get_results(
    collection_name: object_storage.CollectionName,
    dataset_name: object_storage.DatasetName,
    response: Response,
):
    json_payload = simulation_manager.get_simulation_output(str(dataset_name))
    response.headers["x-semantic-mappings"] = "SimpartixOutput"
    return json_payload
```

There are two functions related to ontologies to realize the level-2 integration. These two functions are

```python
@app.get(
    "/mappings",
    summary="Get a list of the available mappings",
    operation_id="listSemanticMappings",
)
def list_mappings():
    return list(mappings.keys())
```

and

```python
@app.get(
    "/mappings/{semantic_mapping_id}",
    summary="Get a specific mapping",
    operation_id="getSemanticMapping",
)
def get_mapping(semantic_mapping_id: str):
    mapping = json.dumps(mappings.get(semantic_mapping_id))
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    return mapping
```

to provide a list of all existing mappings and to retrieve one specific mapping.

## requirements.txt

The requirements file is an ordinary ascii file that contains those python libraries that are necessary somewhere in our python scripts. Some libraries are already installed elsewhere (explained [here](#dockerfile)), but several further libraries are necessary for the web communication. These libraries and more specific also the version of this library is defined in following manner

```
fastapi<1.0.0
marketplace-standard-app-api~=0.4
DLite-Python == 0.3.9
uvicorn<1.0.0
```


## openAPI.yml

openAPI is a standardized format which helps that everybody can understand the server communication in a simpler way. Here, we make use of the yaml structure which is one way to create the API specification (the alternative is a json file). The yaml file applies simple key-value pairs like we know from python dictionaries. The yaml file also allows nesting of mappings by where the structure is simply provided by indentation. So let us have a look at the content of the yaml file and then discuss some of the elements more in detail.
In short, the API specification describes how to describe the RestAPI interface. This includes for example properties, endpoints, types of authorization and data types.

```yml
---
openapi: 3.0.0

info:
    title: SimPARTIX MarketPlace app
    description: MarketPlace app for the SimPARTIX simulation software
    version: 1.0.5
    x-api-version: 0.3.0
    x-products:
        - name: Monthly
          productId:
servers:
    - url: https://simpartix.materials-data.space

paths:
    /heartbeat:
        get:
            summary: Check if app is alive
            operationId: heartbeat
            responses:
                '200':
                    description: Successful Response
                    content:
                        application/json:
                            schema: {}
    /transformations:
        get:
            summary: Get all simulations.
            operationId: getTransformationList
            responses:
                '200':
                    description: Successful Response
                    content:
                        application/json:
                            schema:
                                $ref: '#/components/schemas/TransformationListResponse'
        post:
            summary: Create a new transformation
            operationId: newTransformation
            requestBody:
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/TransformationInput'
                required: true
            responses:
                '200':
                    description: Successful Response
                    content:
                        application/json:
                            schema:
                                $ref: '#/components/schemas/TransformationCreateResponse'
                '422':
                    description: Validation Error
                    content:
                        application/json:
                            schema:
                                $ref: '#/components/schemas/HTTPValidationError'
    /transformations/{transformation_id}:
        delete:
            summary: Delete a transformation
            operationId: deleteTransformation
            parameters:
                - required: true
                  schema:
                      title: Transformation Id
                      type: string
                      format: uuid4
                  name: transformation_id
                  in: path
            responses:
                '200':
                    description: Successful Response
                    content:
                        application/json:
                            schema: {}
                '422':
                    description: Validation Error
                    content:
                        application/json:
                            schema:
                                $ref: '#/components/schemas/HTTPValidationError'
        patch:
            summary: Update the state of the simulation.
            operationId: updateTransformation
            parameters:
                - required: true
                  schema:
                      title: Transformation Id
                      type: string
                      format: uuid4
                  name: transformation_id
                  in: path
            requestBody:
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/TransformationUpdateModel'
                required: true
            responses:
                '200':
                    description: Successful Response
                    content:
                        application/json:
                            schema:
                                $ref: '#/components/schemas/TransformationUpdateResponse'
                '400':
                    description: Error executing update operation
                '404':
                    description: Not Found.
                '409':
                    description: Requested state not available
                '422':
                    description: Validation Error
                    content:
                        application/json:
                            schema:
                                $ref: '#/components/schemas/HTTPValidationError'
    /transformations/{transformation_id}/state:
        get:
            summary: Get the state of the simulation.
            description: |-
                Get the state of a simulation.

                Args:
                    transformation_id (TransformationId): ID of the simulation

                Returns:
                    TransformationStateResponse: The state of the simulation.
            operationId: getTransformationState
            parameters:
                - required: true
                  schema:
                      title: Transformation Id
                      type: string
                      format: uuid4
                  name: transformation_id
                  in: path
            responses:
                '200':
                    description: Successful Response
                    content:
                        application/json:
                            schema:
                                $ref: '#/components/schemas/TransformationStateResponse'
                '404':
                    description: Unknown simulation
                '422':
                    description: Validation Error
                    content:
                        application/json:
                            schema:
                                $ref: '#/components/schemas/HTTPValidationError'
    /results:
        get:
            summary: Get a simulation's result
            operationId: getDataset
            parameters:
                - required: true
                  schema:
                      title: Collection Name
                      maxLength: 255
                      minLength: 1
                      type: string
                  name: collection_name
                  in: query
                - required: true
                  schema:
                      title: Dataset Name
                      minLength: 1
                      type: string
                  name: dataset_name
                  in: query
            responses:
                '200':
                    description: Successful Response
                    content:
                        - vnd.sintef.dlite+json
                '422':
                    description: Validation Error
                    content:
                        application/json:
                            schema:
                                $ref: '#/components/schemas/HTTPValidationError'
    /mappings:
        get:
            summary: Get a list of the available mappings
            operationId: listSemanticMappings
            responses:
                '200':
                    description: Successful Response
                    content:
                        application/json:
                            schema: {}
    /mappings/{semantic_mapping_id}:
        get:
            summary: Get a specific mapping
            operationId: getSemanticMapping
            parameters:
                - required: true
                  schema:
                      title: Semantic Mapping Id
                      type: string
                  name: semantic_mapping_id
                  in: path
            responses:
                '200':
                    description: Successful Response
                    content:
                        application/json:
                            schema: {}
                '422':
                    description: Validation Error
                    content:
                        application/json:
                            schema:
                                $ref: '#/components/schemas/HTTPValidationError'
components:
    schemas:
        HTTPValidationError:
            title: HTTPValidationError
            type: object
            properties:
                detail:
                    title: Detail
                    type: array
                    items:
                        $ref: '#/components/schemas/ValidationError'
        TransformationCreateResponse:
            title: TransformationCreateResponse
            required:
                - id
            type: object
            properties:
                id:
                    title: Id
                    type: string
                    format: uuid4
        TransformationInput:
            title: TransformationInput
            type: object
            properties:
                laserPower:
                    title: Laserpower
                    type: number
                    default: 150
                laserSpeed:
                    title: Laserspeed
                    type: number
                    default: 3
                sphereDiameter:
                    title: Spherediameter
                    type: number
                    default: 3.0e-05
                phi:
                    title: Phi
                    type: number
                    default: 0.7
                powderLayerHeight:
                    title: Powderlayerheight
                    type: number
                    default: 6.0e-05
        TransformationListResponse:
            title: TransformationListResponse
            required:
                - items
            type: object
            properties:
                items:
                    title: Items
                    type: array
                    items:
                        $ref: '#/components/schemas/TransformationModel'
        TransformationModel:
            title: TransformationModel
            required:
                - id
                - parameters
            type: object
            properties:
                id:
                    title: Id
                    type: string
                    format: uuid4
                parameters:
                    title: Parameters
                    type: object
                state:
                    $ref: '#/components/schemas/TransformationState'
        TransformationState:
            title: TransformationState
            enum:
                - CREATED
                - RUNNING
                - STOPPED
                - COMPLETED
                - FAILED
            type: string
            description: An enumeration.
        TransformationStateResponse:
            title: TransformationStateResponse
            required:
                - id
                - state
            type: object
            properties:
                id:
                    title: Id
                    type: string
                    format: uuid4
                state:
                    $ref: '#/components/schemas/TransformationState'
        TransformationUpdateModel:
            title: TransformationUpdateModel
            required:
                - state
            type: object
            properties:
                state:
                    title: State
                    enum:
                        - RUNNING
                        - STOPPED
                    type: string
        TransformationUpdateResponse:
            title: TransformationUpdateResponse
            required:
                - id
                - state
            type: object
            properties:
                id:
                    title: Id
                    type: string
                    format: uuid4
                state:
                    title: State
                    enum:
                        - RUNNING
                        - STOPPED
                    type: string
        ValidationError:
            title: ValidationError
            required:
                - loc
                - msg
                - type
            type: object
            properties:
                loc:
                    title: Location
                    type: array
                    items:
                        anyOf:
                            - type: string
                            - type: integer
                msg:
                    title: Message
                    type: string
                type:
                    title: Error Type
                    type: string

```

First the version of openAPI is provided which is 3.0.0.

```yml
openapi: 3.0.0
```

We continue with some basic information that have the only purpose of providing a description to the user

```yml
info:
  title: SimPARTIX
  description: MarketPlace app for the SimPARTIX simulation software
  version: 1.0.5
  x-api-version: 0.3.0
  x-products:
    - name: Monthly
      productId:
```

and continue with the server on which the software should be running.

```yml
servers:
  - url: https://simpartix.materials-data.space
```

Now we provide all the endpoints which are used as the flask route in the [previous section](#apppy). Let us have a look at some of the endpoints to better understand the yaml file.

```yml
/heartbeat:
    get:
        summary: Check if app is alive
        operationId: heartbeat
        responses:
            '200':
                description: Successful Response
                content:
                    application/json:
                        schema: {}
```

This snippet provides the endpoints _heartbeat_ and defines that is only has a _get_ method. There is one function to be called that we named _heartbeat_. Finally, we provide the security scheme and the response types where we only provided the 200 response which stands for a successful operation.

The remaining endpoints follow the same strategy and can be understood in the very same way.

## Dockerfile

The SimPARTIX app is actually running within a docker container. [Docker](https://www.docker.com/) is a powerful tool to provide a well defined architecture with all necessary libraries. The docker file provided below is the instruction to build up a so called image in which all programs (such as python) and libraries (such as the python libraries) are defined. We build up this image based on an already present image that exist for SimPARTIX and which is hosted on the Fraunhofer own [docker image repository](hub.cc-asp.fraunhofer.de).
In this image, the libraries for SimPARTIX and ProPARTIX are already included such as numpy or pandas while applying the very same strategy as explained in this section. This is the reason for which they have not to be included again in the file [requirements.txt](#requirementstxt) again. If you are unfamiliar with docker, continue first with one of the vast options for docker tutorial. Docker has a steep learning curve though.

We provide the content of our docker file and describe its content afterwards

```dockerfile
# download the image that is already used for SimPARTIX and build up on that image
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
WORKDIR /app
# To store the files from the simulations
RUN mkdir simulation_files
ADD models ./models
ADD simpartix  ./simpartix
ADD simulation_controller ./simulation_controller
ADD static ./static
ADD requirements.txt  .
ADD app.py .
RUN pip install -r requirements.txt

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

In the first step, we load the SimPARTIX image from the Fraunhofer repository to have a base with all functionalities available that are already required by SimPARTIX and ProPARTIX. This however does not include the software itself, but only the libraries. In the following, we add the "simpartix" folder to the image (see again [here](#including-your-own-software)) as a git submodule. In the image, the simpartix folder is however called "source". We change into that directory and there into a "code" folder where we put out files with which the SimPARTIX binary is compiled. Calling "RUN make -j 4" compiles the SimPARTIX binary. Similarly, we change into the ProPARTIX folder and compile here the files that are necessary for the ProPARTIX engine. At this point, the SimPARTIX binary and ProPARTIX functions are all present. We then move into the folder "app" in which alle the services of the SimPARTIX app are going to be running. 

We then copy the folder "simulation\_files", "models", "simpartix", "static" and "simpartix\_controller" and define the flask app and the port. These folders include all the files explained above as well as the SimPARTIX binary. The folder "static" has not been explained as it only contains some figures. Next, we add the file _requirements.txt_ and install all the python libraries via pip. Finally, we add the file _app.py_, set the corresponding environment variables for flask and start the fastapi application.

## docker-compose.yml

Docker compose is build on the docker engine and it is used for running multiple container applications. Using docker compose requires a file _docker-compose.yml_ which is discussed in this section.

```yml
---
version: '3.6'

services:

    simpartix_app:
        build: .
        ports:
            - 8000:8000

```

This files provides the following information

- the version number of the docker engine to allow the correct functionality of docker compose.
- the services which in this case is only the simpartix app. For each service, we must specify where docker can find the corresponding docker file. This is done by the keyword _build_ and the docker file is already in this folder and hence we add the point. Last but not least, the port 8000 is exposed.

When having such a docker compose yaml file within our directory, the only command we have to execute is

```bash
docker-compose up
```

Now docker is automatically downloading all layers and install dependencies.

## Explanation of the optional files

### pre config

There is a tool called "pre-commit" that allows to perform checks on the source code prior to pushing them to the repository. If you are interested in such a tool, follow the explanation on [this website](https://pre-commit.com). The result of this procedure is file called "pre-commit-config.yaml".

### gitignore file

One best practice when using coding is to apply version control to keep track of your changes in the source code. One such version control system is git. A gitignore file allows to have files in your working directory that
should not be tracked by git. For more information, please follow the [official documentation](https://git-scm.com/docs/gitignore).
