import random
import logging

class JobSelection:
    def __init__(self, jobs_with_weights):
        self.jobs = jobs_with_weights  # List of tuples (job_name, weight)
        self.normalized_weights = [weight for _, weight in self.jobs]

    def choose_job(self):
        if not self.jobs:
            return None  # No jobs to choose from
        
        for _, weight in self.normalized_weights:
            logging.warning(weight)

        # Select a job based on normalized weights
        chosen_index = random.choices(range(len(self.jobs)), weights=self.normalized_weights)[0]
        chosen_job = self.jobs[chosen_index]
        
        return chosen_job[0]  # Return the name of the chosen job