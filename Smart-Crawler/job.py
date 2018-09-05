from decouple import config

jobs_path = config("JOBS_DIR")

class JobException(Exception):
    pass

class Job():

    def __init__(self, job_name):
        if type(job_name) != str:
            raise TypeError("job_name must be of type str")

        self.name = job_name
        self.classifiers = []
        self.seed_list = None
        self.user_limit = None

        context = Job.read_and_execute_job_file(job_name)

        # Filter functions whose name starts with "classifier"
        variables = context.keys()

        for variable in variables:
            if variable.startswith("classifier") and callable(context[variable]):
                self.classifiers.append(context[variable])
            elif variable == "seed_list":
                self.seed_list = context[variable]
            elif variable == "user_limit":
                self.user_limit = context[variable]

    def read_and_execute_job_file(job_name):
        context = {}
        file_str = None

        # Read job file
        try:
            with open(jobs_path + "/"+job_name + ".py", "r") as job_file:
                file_str = job_file.read()
        except FileNotFoundError:
            raise JobException("Specified job file is not found : {}.py".format(job_name))

        # Execute job file 
        try:
            exec(file_str, context, context)
        except SyntaxError as s:
            raise JobException("SyntaxError at {}.py : {}".format(job_name , s))

        return context

    def get_job_list(job_names):
        if not job_names:
            job_names = [x[:-3] for x in filter(lambda x : x.endswith(".py") , os.listdir(jobs_path))]

        print("List of jobs : {}".format(job_names))

        return [Job(job_name) for job_name in job_names]