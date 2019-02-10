import base64
import paramiko

import json
#fyp_scw1427
#dais_scw1077

#login


###jobs
#submit single job

#submit batch of jobs

#check job status

#restart failed jobs

#check expected start time for jobs



##remote storage (scratch/home)
#get quota of home
    #myquota

#send files to remote location

#directory of remote location

#fetch files from remote location


class ArrcaTool(object):
    def __init__(self, host, host_key=""):
        self.credentials = self.LoadCredentials()
        self.host = host

        self.client = paramiko.SSHClient()

        self.host_key = host_key
        self.decoded_key = None

        self.COMMANDS = {
            "get_job_queue":"squeue"
            ,"batch_job":"sbatch"
        }

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


    def LoadCredentials(self):
        credentials_json = None
        with open("credentials.json","r") as f:
            credentials_json = json.load(f)
        
        return credentials_json
    

    def Connect(self):
        self.client.connect(self.host, username=self.credentials["username"], password=self.credentials["pw"])


    def CloseConnection(self):
        print("___")
        print("closing connection")
        print("___")
        print("")
        self.client.close()


    def SendCommand(self,command):
        stdin, stdout, stderr = self.client.exec_command(command)
        return stdin, stdout, stderr


    def CheckJobs(self):
        return self.SendCommand(self.COMMANDS["get_job_queue"])
    
    def StartBatchJob(self,account,script_name):
        stdin, stdout, stderr = self.SendCommand(self.COMMANDS["batch_job"]+" --account="+account+" "+script_name) 
        
        job_id = None
        for line in stdout:
            if(str(line)[:20] == "Submitted batch job "):
                job_id = line[20:]
                break
        
        return stdin, stdout, stderr, job_id

    def __del__(self):
        self.CloseConnection()


if __name__ == "__main__":    
    host_key = b'SHA256:P8MxFCLE7+ROcYqIdFRZSZ1WI7CKGIWsJ96o5vjZluo' #ECDSA may not be supported by paramiko,tool uses system approved host keys
    host = "hawklogin.cf.ac.uk"

   

    arcca_tool = ArrcaTool(host,host_key)

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
        arcca_tool.CheckJobs()

        print("Job Queue:")
        print("")
        for line in stdout:
            print('... ' + line.strip('\n'))
    

    if(test_array_job):
        account = "scw1077"
        test_batch_script = "test_array_job.sh"
        
        print("Submit Batch Job:")
        stdin, stdout, stderr, job_id  = arcca_tool.StartBatchJob(account,test_batch_script)
        print("")
        for line in stdout:
            print('... ' + line.strip('\n'))
            