import openai
from sqlalchemy.orm import sessionmaker
from classes import Business, Freelancer, House, Asset, Job, Stock, database
import json

class EntityGenerator:
    def __init__(self):
        openai.api_key = 'YOUR_OPENAI_API_KEY'
        # Setup DB session
        self.Session = sessionmaker(bind=database.engine)

    def generate_and_add_entities(self):
        session = self.Session()

        try:
            # Generate 10 new businesses, freelancers, houses, assets, jobs, and stocks
            generated_data = self.generate_data()

            # Process each entity category
            self.process_businesses(generated_data['businesses'], session)
            self.process_freelancers(generated_data['freelancers'], session)
            self.process_houses(generated_data['houses'], session)
            self.process_assets(generated_data['assets'], session)
            self.process_jobs(generated_data['jobs'], session)
            self.process_stocks(generated_data['stocks'], session)

            session.commit()
            return "Successfully added 10 new businesses, freelancers, houses, assets, jobs, and stocks to the database."

        finally:
            session.close()

    def generate_data(self):
        """
        Interacts with OpenAI to generate new entities.
        Each part generates businesses, freelancers, houses, assets, jobs, and stocks separately.
        """
        generated_data = {
            'businesses': self.generate_businesses(),
            'freelancers': self.generate_freelancers(),
            'houses': self.generate_houses(),
            'assets': self.generate_assets(),
            'jobs': self.generate_jobs(),
            'stocks': self.generate_stocks()
        }
        return generated_data

    def generate_businesses(self):
        # Generate 10 new businesses
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt="Generate 10 new business names with the following attributes: name, purchase_value (int), type_of (string), daily_expense (int), daily_revenue (int)",
            max_tokens=500
        )
        return response.choices[0].text

    def generate_freelancers(self):
        # Generate 10 new freelancers
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt="Generate 10 new freelancers with the following attributes: name, job_title (Agent, Assistant, Consultant, Negotiator, Broker, Accountant), initial_cost (int), daily_expense (int), type_of (wealth, work, stock, gamba), poach_minimum (int), boost_amount (float)",
            max_tokens=500
        )
        return response.choices[0].text

    def generate_houses(self):
        # Generate 10 new houses
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt="Generate 10 new houses with the following attributes: name, purchase_value (int), type_of (string), daily_expense (int)",
            max_tokens=500
        )
        return response.choices[0].text

    def generate_assets(self):
        # Generate 10 new assets
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt="Generate 10 new assets with the following attributes: name, material (string), purchase_value (int), type_of (string)",
            max_tokens=500
        )
        return response.choices[0].text

    def generate_jobs(self):
        # Generate 10 new jobs
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt="Generate 10 new jobs with the following attributes: name, salary (int), chance (float)",
            max_tokens=500
        )
        return response.choices[0].text

    def generate_stocks(self):
        # Generate 10 new stocks
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt="Generate 10 new stocks with the following attributes: name, full_name, growth_rate (float), start_value (int), volatility (float), swap_chance (float), ruination (float), type_of (string)",
            max_tokens=500
        )
        return response.choices[0].text

    def process_businesses(self, businesses_data, session):
        # Add businesses to the database
        businesses = json.loads(businesses_data)
        for business in businesses:
            new_business = Business(
                name=business['name'],
                purchase_value=business['purchase_value'],
                type_of=business['type_of'],
                daily_expense=business['daily_expense'],
                daily_revenue=business['daily_revenue']
            )
            session.add(new_business)

    def process_freelancers(self, freelancers_data, session):
        # Add freelancers to the database
        freelancers = json.loads(freelancers_data)
        for freelancer in freelancers:
            new_freelancer = Freelancer(
                name=freelancer['name'],
                job_title=freelancer['job_title'],
                initial_cost=freelancer['initial_cost'],
                daily_expense=freelancer['daily_expense'],
                type_of=freelancer['type_of'],
                poach_minimum=freelancer['poach_minimum'],
                boost_amount=freelancer['boost_amount']
            )
            session.add(new_freelancer)

    def process_houses(self, houses_data, session):
        # Add houses to the database
        houses = json.loads(houses_data)
        for house in houses:
            new_house = House(
                name=house['name'],
                purchase_value=house['purchase_value'],
                type_of=house['type_of'],
                daily_expense=house['daily_expense']
            )
            session.add(new_house)

    def process_assets(self, assets_data, session):
        # Add assets to the database
        assets = json.loads(assets_data)
        for asset in assets:
            new_asset = Asset(
                name=asset['name'],
                material=asset['material'],
                purchase_value=asset['purchase_value'],
                type_of=asset['type_of']
            )
            session.add(new_asset)

    def process_jobs(self, jobs_data, session):
        # Add jobs to the database
        jobs = json.loads(jobs_data)
        for job in jobs:
            new_job = Job(
                name=job['name'],
                salary=job['salary'],
                chance=job['chance']
            )
            session.add(new_job)

    def process_stocks(self, stocks_data, session):
        # Add stocks to the database
        stocks = json.loads(stocks_data)
        for stock in stocks:
            new_stock = Stock(
                name=stock['name'],
                full_name=stock['full_name'],
                growth_rate=stock['growth_rate'],
                start_value=stock['start_value'],
                volatility=stock['volatility'],
                swap_chance=stock['swap_chance'],
                ruination=stock['ruination'],
                type_of=stock['type_of']
            )
            session.add(new_stock)

