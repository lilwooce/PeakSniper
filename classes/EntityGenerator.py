import openai
from sqlalchemy.orm import sessionmaker
from classes import Businesses, Freelancers, Houses, Assets, Jobs, Stock, database
import json
import os
from packaging import version
import logging

required_version = version.parse("1.1.1")
current_version = version.parse(openai.__version__)

if current_version < required_version:
    raise ValueError(f"Error: OpenAI version {openai.__version__}"
                     " is less than the required version 1.1.1")
else:
    print("OpenAI version is compatible.")

from openai import OpenAI



class EntityGenerator:
    def __init__(self):
        openAIKey = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=openAIKey)
        # Setup DB session
        self.Session = sessionmaker(bind=database.engine)

    async def generate_and_add_entities(self):
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
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                temperature=0.5,
                max_tokens=4000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                messages=[
    				{"role": "system", "content": "You are a helpful chatbot assistant designed to give great responses in proper json format to any question asked."},
    				{"role": "user", "content": '''Generate 10 new businesses as a JSON array with each object having the following attributes:
            {
                "name": "string",
                "purchase_value": "int",
                "type_of": "string",
                "daily_expense": "int",
                "daily_revenue": "int"
            }.
            Ensure the output is valid JSON.'''}
                ]
            )
            businesses_data = response.choices[0].message.content
            return self.validate_and_parse_json(businesses_data, ['name', 'purchase_value', 'type_of', 'daily_expense', 'daily_revenue'])
        except Exception as e:
            logging.warning(e)

    def generate_freelancers(self):
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                temperature=0.5,
                max_tokens=4000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                messages=[
                    {"role": "system", "content": "You are a helpful chatbot assistant designed to give great responses in proper json format to any question asked."},
                    {"role": "user", "content": '''Generate 10 new freelancers as a JSON array with each object having the following attributes:
                    {
                        "name": "string",
                        "job_title": "string",
                        "initial_cost": "int",
                        "daily_expense": "int",
                        "type_of": "string",
                        "poach_minimum": "int",
                        "boost_amount": "float"
                    }.
                    Ensure the output is valid JSON.'''}
                ]
            )
            freelancers_data = response.choices[0].message.content
            return self.validate_and_parse_json(freelancers_data, ['name', 'job_title', 'initial_cost', 'daily_expense', 'type_of', 'poach_minimum', 'boost_amount'])
        except Exception as e:
            logging.warning(e)

    def generate_houses(self):
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                temperature=0.5,
                max_tokens=4000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                messages=[
                    {"role": "system", "content": "You are a helpful chatbot assistant designed to give great responses in proper json format to any question asked."},
                    {"role": "user", "content": '''Generate 10 new houses as a JSON array with each object having the following attributes:
                    {
                        "name": "string",
                        "purchase_value": "int",
                        "type_of": "string",
                        "daily_expense": "int"
                    }.
                    Ensure the output is valid JSON.'''}
                ]
            )
            houses_data = response.choices[0].message.content
            return self.validate_and_parse_json(houses_data, ['name', 'purchase_value', 'type_of', 'daily_expense'])
        except Exception as e:
            logging.warning(e)

    def generate_assets(self):
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                temperature=0.5,
                max_tokens=4000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                messages=[
                    {"role": "system", "content": "You are a helpful chatbot assistant designed to give great responses in proper json format to any question asked."},
                    {"role": "user", "content": '''Generate 10 new assets as a JSON array with each object having the following attributes:
                    {
                        "name": "string",
                        "material": "string",
                        "purchase_value": "int",
                        "type_of": "string"
                    }.
                    Ensure the output is valid JSON.'''}
                ]
            )
            assets_data = response.choices[0].message.content
            return self.validate_and_parse_json(assets_data, ['name', 'material', 'purchase_value', 'type_of'])
        except Exception as e:
            logging.warning(e)

        

    def generate_jobs(self):
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                temperature=0.5,
                max_tokens=4000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                messages=[
                    {"role": "system", "content": "You are a helpful chatbot assistant designed to give great responses in proper json format to any question asked."},
                    {"role": "user", "content": '''Generate 10 new jobs as a JSON array with each object having the following attributes:
                    {
                        "name": "string",
                        "salary": "int",
                        "chance": "float"
                    }.
                    Ensure the output is valid JSON.'''}
                ]
            )
            jobs_data = response.choices[0].message.content
            return self.validate_and_parse_json(jobs_data, ['name', 'salary', 'chance'])
        except Exception as e:
            logging.warning(e)

        

    def generate_stocks(self):
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                temperature=0.5,
                max_tokens=4000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                messages=[
                    {"role": "system", "content": "You are a helpful chatbot assistant designed to give great responses in proper json format to any question asked."},
                    {"role": "user", "content": '''Generate 10 new stocks as a JSON array with each object having the following attributes:
                    {
                        "name": "string",
                        "full_name": "string",
                        "growth_rate": "float",
                        "start_value": "int",
                        "volatility": "float",
                        "swap_chance": "float",
                        "ruination": "float",
                        "type_of": "string"
                    }.
                    Ensure the output is valid JSON.'''}
                ]
            )
        except Exception as e:
            logging.warning(e)

        stocks_data = response.choices[0].message.content
        return self.validate_and_parse_json(stocks_data, ['name', 'full_name', 'growth_rate', 'start_value', 'volatility', 'swap_chance', 'ruination', 'type_of'])


    def validate_and_parse_json(self, data, required_fields):
        try:
            parsed_data = json.loads(data)
            if isinstance(parsed_data, list) and all(isinstance(item, dict) for item in parsed_data):
                # Further validation (check required fields and types)
                for item in parsed_data:
                    for field in required_fields:
                        if field not in item:
                            raise ValueError(f"Missing field '{field}' in one of the generated items.")
                return parsed_data
            else:
                raise ValueError("Generated response is not a valid JSON list.")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error in parsing or validating generated data: {e}")
            return []

    def process_businesses(self, businesses_data, session):
        businesses = businesses_data
        for business in businesses:
            new_business = Businesses.Business(
                name=business['name'],
                purchase_value=business['purchase_value'],
                type_of=business['type_of'],
                daily_expense=business['daily_expense'],
                daily_revenue=business['daily_revenue']
            )
            session.add(new_business)

    def process_freelancers(self, freelancers_data, session):
        freelancers = freelancers_data
        for freelancer in freelancers:
            new_freelancer = Freelancers.Freelancer(
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
        houses = houses_data
        for house in houses:
            new_house = Houses.House(
                name=house['name'],
                purchase_value=house['purchase_value'],
                type_of=house['type_of'],
                daily_expense=house['daily_expense']
            )
            session.add(new_house)

    def process_assets(self, assets_data, session):
        assets = assets_data
        for asset in assets:
            new_asset = Assets.Asset(
                name=asset['name'],
                material=asset['material'],
                purchase_value=asset['purchase_value'],
                type_of=asset['type_of']
            )
            session.add(new_asset)

    def process_jobs(self, jobs_data, session):
        jobs = jobs_data
        for job in jobs:
            new_job = Jobs.Jobs(
                name=job['name'],
                salary=job['salary'],
                chance=job['chance']
            )
            session.add(new_job)

    def process_stocks(self, stocks_data, session):
        stocks = stocks_data
        for stock in stocks:
            new_stock = Stock.Stock(
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
