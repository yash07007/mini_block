# Mini Block

## About this project

In this project voting system is implemented using blockchain. A cloud simulation is available in democloud directory, UI is implemented in ui directory. Some test dummy data is given in `democloud/rawdata`. This project uses mongodb as its primary dataset for sotring cloud data for which a helper utility file is given `[democloud/excel2mongo.py]` which can be used to initialize mongodb dataset with raw data present in excel files. for the first time converting raw-data into mongodb is mandatory step.

## How to use this project

### Step 1
Install prerequistes (Anaconda environment is advised as most of these comes pre installed)
- Python Packages
    - flask
    - flask_cors
    - requests
    - Crypto
    - pymongo
- MongoDB

### Step 2
After installation the first thing we need to do is host a mongodb server which can be done as follows:

Open command prompt in your machine and traverse to mongodb directory using `cd` command default path will be    

>C:\Program Files\MongoDB\Server\4.0\bin

Then enter the following command in command prompt

    mongod.exe --dbpath "...\Mini Block\democloud\cloud-data"

Make sure to add root path before Mini Block directory.

This step will make sure MongoDB server is on and data directory is set to `democloud/cloud-data`.

You can minimize this prompt for remainder of the time. Also it is not adviseable to mess with the newly created files on `democloud/cloud-data` directory.

### Step 3

This step is mandatory for the first time and optional thereafter.

Now we will create database and insert raw data present in form of excel sheets in `democloud/raw-data` directory.

All we need to do is run python file `democloud/excel2mongo.py` in any python supported prompt.

    ../democloud>python excel2mongo.py

This will insert all the data present in excel file into newly created dataset in mongodb which can ve verifies by using mongo shell.

### Step 4

Now we need to start cloud server `democloud/server.py` in any python supported prompt.

    ../democloud>python server.py

for the remainder of this tutorial this terminal has to be kept open in background.

### Step 5

In the last step of this tutorial we will run `main.py` file with specifying port with `-p` or `--port` argument in prompt. If not specified by default files opens on port `5000` . 

    ../MiniBlock>python main.py

By default this will be hosted on `localhost:5000`.

    ../MiniBlock>python main.py -p 5001
    ../MiniBlock>python main.py --port 5001

Any number of instances with diffrent ports can be created instantiated from any one of the code shown above.

This created instances can be seen in any browser with url `localhost:port`

### Final Notes

>Voting Machine Intializer Smart Card has been simulated any of the following card secret will work and appropriate data will be loaded.
> - 123001
> - 123002
> - 123003
> - 123004
> - 123005

>To observing broadcasting nature of blockchain add all the peers created to each others network under network tab.

>To get information about Constituency go to profile tab and load data.

>Before doing any transaction creating node is nessasary and once created it can be loaded whenever needed with loaf button

---
