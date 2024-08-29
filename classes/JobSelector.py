import random
import logging
import json

class JobSelection:
    def __init__(self, jobs_with_weights):
        self.jobs = jobs_with_weights  # Dictionary {job_name: weight}
        self.normalized_weights = [weight for weight in self.jobs.values()]

    def choose_job(self):
        if not self.jobs:
            return None  # No jobs to choose from
        
        # Log each weight
        for weight in self.normalized_weights:
            logging.warning(weight)

        # Select a job based on normalized weights
        chosen_job_name = random.choices(list(self.jobs.keys()), weights=self.normalized_weights)[0]
        
        return chosen_job_name  # Return the name of the chosen job
