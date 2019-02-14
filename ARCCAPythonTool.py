import base64
import paramiko

import json
import os

import re

import thread
import time



### Connection
#[x] load credentials
#[x] create credentials template if file missing
#[x] login


###jobs
#[x] submit job
#[ ] submit array of jobs
#[x] check job status 
#[x] poll job status(blocking)
#[ ] restart failed jobs
#[ ] check expected start time for jobs
#[x] cancel job



##remote storage (scratch/home)
#[ ] get quota of home
    #myquota

#[ ] send files to remote location

#[ ] directory of remote location

#[ ] fetch files from remote location


class ArccaTool(object):
    def __init__(self, host, host_key=""):
        self.credentials = self.LoadCredentials()
        self.host = host

        self.client = paramiko.SSHClient()
        self.client_open = False

        self.host_key = host_key
        self.decoded_key = None

        self.COMMANDS = {
            "get_job_queue":"squeue"
            ,"batch_job":"sbatch"
            ,"cancel job":"scancel"
        }

        self.JOB_STATUS_CODES = None

        with open("status_codes.json", "r") as f:
             self.JOB_STATUS_CODES = json.loads(f.read())
        
        self.user_jobs_list = []

        if(self.host_key != ""):
            print("___")
            print("Manual passing of host key not yet supported.")
            print("Connect using system SSH first to verify host key manually. System keys are used by this tool.")
            print("___")
            self.client.load_system_host_keys()
            # self.decoded_key = paramiko.RSAKey(data=base64.b64decode(b'SHA:AAA='))
            # self.client.get_host_keys().add(self.host, 'ssh-rsa', self.decoded_key)
        else:
            print("___")
            print("Accepted system host keys will be used to check server identity.")
            print("If connection fails due to host keys, manually connect via SSH through terminal once and verify the host key manually")
            print("___")
            print("")
            self.client.load_system_host_keys()
            # print("Warning: no host key provided - can't confirm identity of server")
            # self.client.set_missing_host_key_policy(paramiko.WarningPolicy())


    ###CREDENTIAL FUNCTIONS
    def LoadCredentials(self,credentials_path="credentials.json"):
        if(not os.path.exists(credentials_path)):
            self.CreateCredentialsTempalte(credentials_path)
            print("Credentials file did not exist. Template created at: "+credentials_path)
            credentials_file_exists = False
            assert credentials_file_exists
        
        credentials_json = None
        with open("credentials.json","r") as f:
            credentials_json = json.load(f)
        
        return credentials_json
    

    def CreateCredentialsTempalte(self,credentials_path="credentials.json"):
        template = {
            "username":"USERNAME",
            "pw":"PASSWORD"
            }
        
        with open(credentials_path, "w") as f:
            f.write(json.dumps(template,indent=4))


    ### CONNECTION FUNCTIONS
    def DangerousAutoAddHost(self):
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def Connect(self):
        self.client.connect(self.host, username=self.credentials["username"], password=self.credentials["pw"])


    def CloseConnection(self):
        print("___")
        print("closing connection")
        print("___")
        print("")
        self.client.close()


    ###COMMANDS
    def SendCommand(self,command):
        stdin, stdout, stderr = self.client.exec_command(command)
        return stdin, stdout, stderr


    #JOB POLLING FUNCTIONS
    def CheckJobs(self, job_ids=[], job_names=[], user_ids=[]):
        queue_command = self.COMMANDS["get_job_queue"]

        if(len(job_ids) > 0):
            queue_command += " --jobs "

            for id in job_ids:
                queue_command += id+","
            
            queue_command = queue_command[:-1]
        
        elif(len(job_names) > 0):
            queue_command += "--name "
            
            for name in job_names:
                queue_command += name+","
                
            queue_command = queue_command[:-1] 
        
        elif(len(user_ids) > 0):
            queue_command += " --users "

            for id in user_ids:
                queue_command += id+","
            
            queue_command = queue_command[:-1]                      

        stdin, stdout, stderr = self.SendCommand(queue_command)
        job_queue = []
        for line in stdout:
            job_queue.append(line.strip('\n'))

        return job_queue

    
    def CheckOwnJobs(self):
        return self.CheckJobs(user_ids=[self.credentials["username"]])


    def ProcessJobLine(self,job_line):
        result = re.findall(r'([\w\[\]\-\:\.\(\)]+)', job_line)
        
        job = None
        if(len(result) == 8):
            job = {
                "job_id":result[0]
                ,"partition":result[1]
                ,"name":result[2]
                ,"user":result[3]
                ,"st":result[4]
                ,"time":result[5]
                ,"nodes":result[6]
                ,"nodelist":result[7]
                }
        return job


    def GetJobListFromStringList(self,job_string_list):
        job_list = []
        failed_strings = []
        for line in job_string_list[1:]:
            job = self.ProcessJobLine(line)
            if(job is None):
                failed_strings.append(line)
            else:
                job_list.append(job)
        
        return job_list, failed_strings
    

    def PollJobs(self):
        print("Press Enter to Stop Polling Jobs")
        def input_thread(L):
            raw_input()
            L.append(None)
        L = []
        thread.start_new_thread(input_thread, (L,))
        while 1:
            time.sleep(2)
            if L: break
            jobs = self.CheckOwnJobs()
            for job in jobs:
                print(job)
    
    def CheckStartTime(self,job_id):
        queue_command = self.COMMANDS["get_job_queue"] +" -j "+job_id + "--start"

        stdin, stdout, stderr = self.SendCommand(queue_command)
        job_queue = []
        for line in stdout:
            job_queue.append(line.strip('\n'))

        return job_queue

    ###CANCEL JOB FUNCTIONS
    def CancelJob(self,job_id):
        command = self.COMMANDS["cancel_job"]+ " " + str(job_id)

        _, stdout, _ = self.SendCommand(command)
        output = ""
        for line in stdout:
            output += line
        
        return output


    ### CREATE JOB FUNCTIONS
    def StartBatchJob(self,account,script_name):
        #TODO: remove these
        #fyp_scw1427
        #dais_scw1077
        stdin, stdout, stderr = self.SendCommand(self.COMMANDS["batch_job"]+" --account="+account+" "+script_name) 
        
        job_id = None
        for line in stdout:
            if(str(line)[:20] == "Submitted batch job "):
                r'\d+'
                job_id = line[20:]
                break
        

        
        return stdin, stdout, stderr, job_id

    def __del__(self):
        if(not self.client is None):
            if(self.client.get_transport().is_active()):
                self.CloseConnection()


if __name__ == "__main__":    
    host_key = b'SHA256:P8MxFCLE7+ROcYqIdFRZSZ1WI7CKGIWsJ96o5vjZluo' #ECDSA may not be supported by paramiko,tool uses system approved host keys
    host = "hawklogin.cf.ac.uk"

   

    arcca_tool = ArccaTool(host,host_key)

    arcca_tool.Connect()

    #EXAMPLES
    list_home_dir = False
    list_jobs = False
    test_array_job = True


    if(list_home_dir):
        stdin, stdout, stderr  = arcca_tool.SendCommand('ls')

        print("Directory of home:")
        for line in stdout:
            print('... ' + line.strip('\n'))
    
    
    if(list_jobs):
        queue = arcca_tool.CheckJobs()

        print("Job Queue:")
        print("")
        for item in queue:
            print(item)
    

    if(test_array_job):
        account = "scw1077"
        test_batch_script = "test_array_job.sh"
        
        print("Submit Batch Job:")
        stdin, stdout, stderr, job_id  = arcca_tool.StartBatchJob(account,test_batch_script)
        print("")
        for line in stdout:
            print('... ' + line.strip('\n'))
            