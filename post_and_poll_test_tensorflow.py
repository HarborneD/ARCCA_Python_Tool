from ARCCAPythonTool import ArccaTool
import sys

print("Initialise Tool and Connect")
host_key = ''
host = 'hawklogin.cf.ac.uk'
arcca_tool = ArccaTool(host,host_key)

arcca_tool.DangerousAutoAddHost()

arcca_tool.Connect()
print("")

try:
    print("Post job")
    stdin, stdout, stderr, job_id = arcca_tool.StartBatchJob("scw1427","/home/c.c0919382/test_scripts/ARCCA_Python_Tool/test_arcca_scripts","test_tensorflow.sh")
    print("")
except:
    "posting job failed"
    sys.exit()

print("Check Jobs Start Time")
for job in arcca_tool.user_jobs_list:
    job_queue = arcca_tool.CheckStartTime(job_id)

    for job in job_queue:
        print(job)

print("")

print("Poll Jobs")
arcca_tool.PollJobs()
print("")