
from ARCCAPythonTool import ArccaTool
import os
import time

from simple_toolbar import ProgressBar

import shutil

class RemoteGATool(object):
    def __init__(self,local_ga_dir,remote_ga_dir,host="hawklogin.cf.ac.uk"):
        self.local_ga_directory = local_ga_dir
        self.remote_ga_directory = remote_ga_dir
        
        self.local_policies_directory = os.path.join(self.local_ga_directory,"policies")
        self.remote_policies_directory = os.path.join(self.remote_ga_directory,"policies")

        self.host_key = b'SHA256:P8MxFCLE7+ROcYqIdFRZSZ1WI7CKGIWsJ96o5vjZluo' #ECDSA may not be supported by paramiko,tool uses system approved host keys
        self.host = host

        self.arcca_tool = ArccaTool(host)
        self.arcca_tool.DangerousAutoAddHost()

        self.ACCOUNT = "scw1427"
        self.RUN_FROM_PATH = "/home/c.c0919382/fyp_scw1427/genetic_augment"
        self.SCRIPT_NAME = "arcca_evaluate_child_model.sh"
        
        self.DATA_PATH="/home/c.c0919382/datasets/cifar-10-batches-py"

        self.training_tracker = {}
        self.job_map = {}
        self.current_generation = []
        self.running_jobs_of_generation = []

    def SendPolicyFile(self,policy_id):
        local_policy_path = os.path.join(self.local_policies_directory, policy_id+".json")
        remote_policy_path = os.path.join(self.remote_policies_directory, policy_id+".json")
        self.arcca_tool.SendFileToServer(local_policy_path,remote_policy_path)
    
    
    def StartRemoteChromosomeTrain(self, policy_id, num_epochs, data_path, dataset="cifar10", model_name="wrn", use_cpu=0, num_train_images=4000):
        _, _, _, job_id, was_error = self.arcca_tool.StartBatchJob(self.ACCOUNT,self.RUN_FROM_PATH,self.SCRIPT_NAME,'"'+str(policy_id)+'" "'+str(num_epochs)+'" "'+str(num_train_images)+'"')
        return job_id, was_error
        
    def HandleJobError(self):
        #TODO: handle job errors 
        print("job error handling not implemented")
    

    def StartGenerationTraining(self,policy_ids, num_epochs):
        for policy_id in policy_ids:
            job_id, was_error = self.StartRemoteChromosomeTrain(policy_id, num_epochs,self.DATA_PATH)
            if(not was_error):
                print(str(policy_id) + " posted as job: "+str(job_id))
                self.training_tracker[policy_id] = {"job_id":job_id,"last_known_status":"submitted"}
                self.job_map[job_id] = policy_id
                self.running_jobs_of_generation.append(policy_id)
            else:
                self.HandleJobError()
        self.current_generation = policy_ids
    

    def JobListToPolicyList(self,job_list):
        return [self.job_map[j_id]for j_id in job_list]
    
    def PolicyListToJobList(self,policy_list):
        return [self.training_tracker[p_id]["job_id"] for p_id in policy_list]
    

    def UpdateCurrentGenerationJobs(self):

        # "job_id":result[0]
        #         ,"partition":result[1]
        #         ,"name":result[2]
        #         ,"user":result[3]
        #         ,"st":result[4]
        #         ,"time":result[5]
        #         ,"nodes":result[6]
        #         ,"nodelist":result[7]
        #         }
        job_ids=self.PolicyListToJobList(self.current_generation)

        job_queue = self.arcca_tool.CheckJobs(job_ids=job_ids)

        jobs = []
        for job_line in job_queue[1:]:
            jobs.append(self.arcca_tool.ProcessJobLine(job_line))
        
        jobs_in_queue = []
        for job_id in jobs:
            jobs_in_queue.append(job_id)

        jobs_statuses = self.arcca_tool.CheckJobsStatuses(start_time="2019-02-01")
        
        for policy_id in self.current_generation:
            job_id = self.training_tracker[policy_id]["job_id"]
        
            if(job_id in jobs_statuses):
                self.training_tracker[policy_id]["last_known_status"] = jobs_statuses[job_id]["state"] #self.arcca_tool.JOB_STATUS_CODES[job["st"]]["name"]

        self.running_jobs_of_generation = jobs_in_queue


    
    def WaitForGenerationComplete(self):
        num_jobs = len(self.current_generation)

        progress = ProgressBar(num_jobs, width=20, fmt=ProgressBar.FULL)

        while len(self.running_jobs_of_generation) > 0:
            self.UpdateCurrentGenerationJobs()
            jobs_strings=""
            for policy_id in self.current_generation:
                job_id = self.training_tracker[policy_id]["job_id"]
                
                status_letter = ""
                if(policy_id in self.training_tracker):
                    status_letter = self.training_tracker[policy_id]["last_known_status"][:1]
                jobs_strings+= str(job_id)+status_letter+","
            jobs_strings = jobs_strings[:-1] 
            progress.current = num_jobs - len(self.running_jobs_of_generation)
            progress(jobs_strings)
            time.sleep(3)
        progress.done()
        

    def ReadResultsFile(self,local_file_path):
        results_headings = ["policy_id","num_epochs","model_name","dataset","use_cpu","time_taken"]
        
        # for results_heading in results_headings:
        #     results_string += str(configuration_dict[results_heading]) +","
        
        # results_string += str(test_accuracy)
        results_string = ""
        with open(local_file_path,"r") as f:
            results_string = f.read()
        
        result_split = results_string.split(",")
        
        result = {}

        for results_heading_i in range(len(results_headings)):
            result[results_headings[results_heading_i]] = result_split[results_heading_i]
        
        result["test_accuracy"] = float(result_split[-1])
        
        return result

    def GetGenerationResults(self):
        local_results_dir = os.path.join(self.local_ga_directory,"results")
        remote_results_dir = os.path.join(self.remote_ga_directory,"results")
        
        results = []
        for policy_id in self.current_generation:
            local_result_path = os.path.join(local_results_dir,policy_id+".csv")
            remote_result_path = os.path.join(remote_results_dir,policy_id+".csv")

            try:
                self.arcca_tool.FetchFileFromServer(remote_result_path,local_result_path)

                results.append(self.ReadResultsFile(local_result_path))
            except:
                print("Policy Results Fetch: "+ policy_id)
                print("")
        return results
    

    def GetPolicyResults(self,policy_id):
        local_results_dir = os.path.join(self.local_ga_directory,"results")
        remote_results_dir = os.path.join(self.remote_ga_directory,"results")
        
        local_result_path = os.path.join(local_results_dir,policy_id+".csv")
        remote_result_path = os.path.join(remote_results_dir,policy_id+".csv")

        try:
            self.arcca_tool.FetchFileFromServer(remote_result_path,local_result_path)

            return self.ReadResultsFile(local_result_path)

        except:
            print("Policy Results Fetch Failed: "+ policy_id)
            print("")

            return None
    

    def CleanCheckpoints(self,policy_ids):
        checkpoints_dir = os.path.join(self.remote_ga_directory,"checkpoints")
        for policy_id in policy_ids:
            checkpoint_path = os.path.join(checkpoints_dir,"checkpoints_"+policy_id)
            self.arcca_tool.RemoveRemoteItem(checkpoint_path)
        

    def CleanDirectoriesAndStoreCurrentGen(self,policy_ids):
        previous_generation_path = os.path.join(self.remote_ga_directory,"previous_generation")

        if(not self.arcca_tool.CheckPathExists(previous_generation_path)):
            self.arcca_tool.CreateFolder(previous_generation_path)

        #clean previous_generation folders
        self.CleanPreviousGeneration(previous_generation_path)
        
        #copy current generations to previous_generation folders
        self.MoveCurrentGenerationToPreviousGenerationFolder(policy_ids,previous_generation_path)
        

    def CleanPreviousGeneration(self,previous_generation_path):
        previous_checkpoints_path = os.path.join(previous_generation_path, "checkpoints")
        
        if(not self.arcca_tool.CheckPathExists(previous_checkpoints_path)):
            self.arcca_tool.CreateFolder(previous_checkpoints_path)
            
        checkpoints = self.arcca_tool.ListRemoteDir(previous_checkpoints_path)
        for checkpoint in checkpoints:
            checkpoint_path = os.path.join(previous_checkpoints_path,checkpoint)
            self.arcca_tool.RemoveRemoteItem(checkpoint_path)
        
        previous_policies_path = os.path.join(previous_generation_path, "policies")
        if(not self.arcca_tool.CheckPathExists(previous_policies_path)):
            self.arcca_tool.CreateFolder(previous_policies_path)
        
        policies = self.arcca_tool.ListRemoteDir(previous_policies_path)
        for policy in policies:
            policy_path = os.path.join(previous_policies_path,policy)
            self.arcca_tool.RemoveRemoteItem(policy_path)
        


    def MoveCurrentGenerationToPreviousGenerationFolder(self,policy_ids,previous_generation_path):
        checkpoints_dir = os.path.join(self.remote_ga_directory,"checkpoints")
        policies_dir = os.path.join(self.remote_ga_directory,"policies")

        previous_checkpoints_path = os.path.join(previous_generation_path, "checkpoints")
        previous_policies_path = os.path.join(previous_generation_path, "policies")
        
        for policy_id in policy_ids:
            checkpoint_path = os.path.join(checkpoints_dir,"checkpoints_"+policy_id)
            policy_path = os.path.join(policies_dir,policy_id+".json")

            checkpoint_output_path = os.path.join(previous_checkpoints_path,"checkpoints_"+policy_id)
            policy_output_path = os.path.join(previous_policies_path,policy_id+".json")

            self.arcca_tool.MoveRemoteDirectory(checkpoint_path,checkpoint_output_path)
            self.arcca_tool.MoveRemoteFile(policy_path,policy_output_path)



if __name__ == "__main__":
    test_after_posting_jobs = False
    submitted_policies = [("000001","2833647"),("000002","2833648") ] #for testing after jobs are posted
        
    local_ga_directory = "/media/harborned/ShutUpN/repos/final_year_project/genetic_augment"
    remote_ga_directory = "/home/c.c0919382/fyp_scw1427/genetic_augment"

    remote_tool = RemoteGATool(local_ga_directory,remote_ga_directory)

    #TODO: uncomment section after testing
    test_policy_ids = ["000001","000002"]

    for policy_id in test_policy_ids:
        remote_tool.SendPolicyFile(policy_id)

    
    if(test_after_posting_jobs):
        #TODO: remove code after testing:
        for submitted_policy in submitted_policies:
            remote_tool.training_tracker[submitted_policy[0]] = {"job_id":submitted_policy[1],"last_known_status":"submitted"}
            remote_tool.job_map[submitted_policy[1]] = submitted_policy[0]
            remote_tool.running_jobs_of_generation.append(submitted_policy[0])
        remote_tool.current_generation = [p[0] for p in submitted_policies]
    else:
        remote_tool.StartGenerationTraining(test_policy_ids,5)

        # remote_tool.arcca_tool.PollJobs()


        # remote_tool.arcca_tool.CheckJobs(job_ids=remote_tool.current_generation)

    remote_tool.WaitForGenerationComplete()

    time.sleep(2)
    results = remote_tool.GetGenerationResults()

    for r in results:
        print(r)