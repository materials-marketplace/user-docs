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

In this file, we have defined two classes with names "SimulationStatus" and "SimulationConfig". 

The file starts with 
```python
import logging

# Global Constant to define the extension of zip files
ZIP_EXTENSION = "zip"

# Global constant to define the path of the folder where all the simulations are saved
SIMULATIONS_FOLDER_PATH = "/app/simulation_files"

```

and follows with the definition for the simulation states. Here, we define 5 different kinds of states that are
- created
- running
- completed
- stopped
- error

the class structure looks as follow
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
By writing "Enum" into the bracket, this class in heriting from the Enum class which is a built-in class from python. This allows to use a more natural syntax to ask the script whether the simulation has been created or whether it is running. In fact, we can apply the following notation
```python
state = SimulationStatus.CREATED # which is equal to "CREAETD"
# and then ask for that state by
if state == SimulationStatus.CREATED:
    print('simulation has been created')
```
which is a readable syntax to ask for the state of a simulation.

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



## Explanation of the optional files

### pre config

There is a tool called "pre-commit" that allows to perform checks on the source code prior to pushing them to the repository. If you are interested in such a tool, follow the explanation on [https://pre-commit.com][ this website]. The result of 
this procedure is file called "pre-commit-config.yaml".


### gitignore file ###

One best element practice when using coding is to apply version control to keep track of your changes in the source code. One such version control system is git. A gitignore file allows to have files in your working directory that 
should not be tracked by git. For more information, please follow the [https://git-scm.com/docs/gitignore][ official documentation]. 

