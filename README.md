# ARCCA_Python_Tool
A python tool for interacting with the Super Computing Wakes ARCCA super computing resources.

This tool provides a python class to programitcally submit and check jobs on the ARCCA job server from within python scripts. 

The tool also allows for SFTP actions to made such as sending, fetching and deleting files to/from/on the SCW server. 

## Account Registration
To make use of the tool (and the SCW resources) be sure to first set up an account and join, or set up a project(Adhering to the rules and pre-requests to do so). 

This can be done [here](https://my.supercomputing.wales).

## Credentials File
Once registered you must create a credentials file in the root of the ARCCA_Python_Tool directory. If one does not exist and you attempt to instantiate the class, a template credentials file will be created and the script will terminate. 

If you want to manually create the credentials file, it should look like this:

```
{
  "username":"USERNAME",
  "pw":"PASSWORD"
}
```

This file is ignored by the repositry but of course, be careful with the privacy/accessability of this file.


**Please Note**: Due to security concerns and lack of support in the python SSH module being used (paramiko),the tool's login to SCW does not perform the check against man in the middle attacks using ECDSA host keys. Instead, the tool uses your system's approved host keys. This requires you to manual log on to the SCW login server once via SSH and add the key to your approved list.

## Instantiating Tool

To use the tool simply instantiate an instance of it, passing the address of your login server. The current host addresses are summarised below (if you encounter issues, check SCW for the most up to date addresses).

Institution | Server | Address
------------ | -------------| -------------
Cardiff or Bangor | Hawk | hawklogin.cf.ac.uk
Swansea or  Aberystwyth| Sunbird | sunbird.swansea.ac.uk

Instantiation:
```
host = "hawklogin.cf.ac.uk"
arcca_tool = ArccaTool(host)
```

## Job Management
Job management is approached similarly to if you were remotely accessing the job server. As such, it is reccomended that you are familar with how to submit jobs using remote access. Details of this can be found [here](https://portal.supercomputing.wales/index.php/index/submitting-jobs/).

This also means that slurm job script files (and any other required files, such as data) should be already on your file system (or should be transfered using this tool ahead of starting the job). This tool does not aim to create these for you - simply to enable run them and manage them programitcally.


### Submitting a Job

```python
#The project account to run the job under
account = "scw1234" 

#The absolute path to the directory of your file sapce to run the job from
run_from_path = "/home/c.c1234567/my_folder" 

#The realtive path to the job script from that directory
script_name = my_slurm_script.sh 

#A string repsenting the command line arguments to be passed to the job script. 
#This string will simply be concatenated as if they were typed after the job script name.
arguments = "MY_FIRST_ARG MY_SECOND_ARG OPTIONAL_ARG=10"  

arcca_tool.StartBatchJob(account,run_from_path,script_name, args=arguments)
```

### Checking Job Status
```python

#get status of all jobs on or after this date 
start_time="2019-04-01" 

status_list = arcca_tool.CheckJobsStatuses(start_time="2019-02-01")
```

status_list is a list containing dictionaries with the following format:

```python
status = {
  'account':'scw1427'
  'cpu_alloc':'1'
  'exit_code':'11:0'
  'job_id':'7896543'
  'job_name':'my_job'
  'partition':'gpu'
  'state':'FAILED'
}
```

### Checking the Predicted Start Time of a Job
```python
arcca_tool.CheckStartTime(job_id)

```

### Cancelling a Job
```python
arcca_tool.CancelJob(job_id)
```


<br>




## File Management

### Send File to Server
```python
source_path = "my_local_file.txt" #path to local file
destination_path = "explicit/path/to/destination #absolute path to file on SCW filespace

arcca_tool.SendFileToServer(source_path,destination_path)
```

### Fetch File from Server
```python
source_path = "explicit/path/to/destination #absolute path to file on SCW filespace
destination_path = "my_local_file.txt" #path to local file

arcca_tool.FetchFileFromServer(source_path,destination_path)
```

### List Remote Directory Contents
```python
arcca_tool.ListRemoteDir(path)
```


### Check Remote Path Exists
```python
arcca_tool.CheckPathExists(path)
```

### Check if Remote Path is a Directory
```python
arcca_tool.CheckRemotePathIsDirectory(path)
```

### Create Remote Directory
```python
arcca_tool.CreateFolder(path)
```

### Move Remote Files/Directories from a Remote Location to Another Remote Location
```python
arcca_tool.MoveRemoteFile(remote_source, remote_destination)
    
arcca_tool.MoveRemoteDirectory(remote_source, remote_destination)
```

### Delete Files/Folders/Either
```python
arcca_tool.RemoveRemoteDirectory(path) #only will delete path if it is a directory.

arcca_tool.DeleteRemoteFile(path) #only will delete path if it is a file.

arcca_tool.RemoveRemoteItem(path) #will check if path is a directory and then use appropriate removal function
```

