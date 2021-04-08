# Team 22 Supply Back end
This is the Team 22 backend for supply services. This repository deals with any requests handled in `https://supply.team22.sweispring21.tk/api/v1/supply/[request-name]` for `supply` services.

## Objective ##
The objective of `Supply Backend` is to handle any requests sent to `supply/[request-name]` and write to database.

This repository includes `unittest` so that we are able to test our objects and soon we will implement CI/CD for  automated builds and testing.

## REST API ## 
You can view working REST API for supply using [Postman]()

## Structure ##
```
team22-supply-backend
├── docs                            # Documentation Directory
├── unittest                        # Unit Test Directory to test Object classes                     
│   └── dispatch_test_case.py       # Test cases for `dispatch.py` class
│   └── fleetmanager_test_case.py   # Test cases for `fleetmanager.py` class
├── dispatch.py                     # Dispatch class object
├── fleetmanager.py                 # FleetManager class object
├── server.py                       # The main Python endpoints server for supply cloud
├── requirements.txt                # Python Dependencies to run `server.py`
└── README.md                       # Documentation about this repo
```

> Use short lowercase names for files and folders except for
> `README.md`

# Modifying This Repo
### Cloning repository
***Before you star you must have Python 3.8 installed in your system***  
If you would like to contribute to this repository, you first must clone this repository by running:  
```git clone https://bitbucket.org/swe-spring-2021-team-22/team22-supply-backend.git```  

### Setting Up Environment
After doing so, go to the `team22-supply-backend` directory using command line or PyCharm Terminal and we will install the `env` environment for your setup by running:  
`python3 -m venv env`  
  
### Activating Environment
Now that you have the environment, in order to be in the environment you type:  
`source env/bin/activate`  
  
### Installing/Uninstalling Dependencies
Make sure you install dependencies. You do so by running `python3 -m pip install -r requirements.txt`. If you added more or removed dependencies and need to generate a new `requirements.txt`, you do so by running `pip freeze > requirements.txt`.

#### .env file ####
This file you have to make on your own. It should be on the project directory. If you notice, `MongoUtils.py` script uses `MONGO_SECRET`, which needs to be defined in `.env` file. This holds our mongo database `developer` password.

### Deactivating Environment
Now you should be in the `env` environment. To get out of the environment you type `deactivate` in command line.


### MAKE SURE IF YOU CLONE THIS THAT THE PARENT DIRECTORY ALSO HAS `team22-common-services-backend`.