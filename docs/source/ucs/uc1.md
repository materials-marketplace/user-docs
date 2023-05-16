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
- __init__.py
- config.py
- propartix_files_creation.py
- simpartix_output.py
- SimPARTIXOutput.json
- simulation_manager.py
- simulation.py


The file "__init__.py" is an empty file and its only purpose is that python allows to include all function via the regular 
package syntax as libraries. This means in all files, we can include classes and function of other files with simple commands. Usually, python has no problem to import a whole directory. But when it comes to importing a class from a file in a directory, this will raise an exception. 





## explanation of the optional files

### pre config

There is a tool called "pre-commit" that allows to perform checks on the source code prior to pushing them to the repository. If you are interested in such a tool, follow the explanation on [https://pre-commit.com/][this website]. The result of 
this procedure is file called "pre-commit-config.yaml".


### gitignore file ###

One best element practice when using coding is to apply version control to keep track of your changes in the source code. One such version control system is git. A gitignore file allows to have files in your working directory that 
should not be tracked by git. 

