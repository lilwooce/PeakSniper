import random
import logging

class JobSelection:
    def __init__(self, jobs_with_weights):
        self.jobs = jobs_with_weights  # List of tuples (job_name, weight)
        self.total_weight = sum((weight/100) for _, weight in self.jobs)

    def choose_job(self):
        if not self.jobs:
            return None  # No jobs to choose from

        # Normalize weights
        normalized_weights = [(weight/100) / self.total_weight for _, weight in self.jobs]
        for _, weight in self.jobs:
            logging.warning((weight/100) / self.total_weight)
        logging.warning(normalized_weights)

        # Select a job based on normalized weights
        chosen_index = random.choices(range(len(self.jobs)), weights=normalized_weights)[0]
        chosen_job = self.jobs[chosen_index]
        
        return chosen_job[0]  # Return the name of the chosen job