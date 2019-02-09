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

host = "hawklogin.cf.ac.uk"

credentials_json = None
with open("credentials.json","r") as f:
    credentials_json = json.load(f)

print(credentials_json["username"])


# key = paramiko.RSAKey(data=base64.b64decode(b'AAA...'))
# client = paramiko.SSHClient()
# client.get_host_keys().add('ssh.example.com', 'ssh-rsa', key)
# client.connect('ssh.example.com', username='strongbad', password='thecheat')
# stdin, stdout, stderr = client.exec_command('ls')
# for line in stdout:
#     print('... ' + line.strip('\n'))
# client.close()