from sqlalchemy import desc
from classes import Businesses, Freelancers, Houses, Assets, Jobs, Stock, database

class Utils:
    @staticmethod
    def get_boost(user_id, session, type_of, title):
        # Query freelancers where the boss is the user_id and matching the given type_of and title, or "wealth" type
        highest_freelancer = (
            session.query(Freelancers.Freelancer)
            .filter(
                Freelancers.Freelancer.boss == user_id,  # Match the user_id directly
                (
                    Freelancers.Freelancer.type_of.ilike(f"%{type_of}%")  # Case-insensitive match for the specified type_of
                    | Freelancers.Freelancer.type_of.ilike("wealth")  # Include wealth type assistants
                ),
                Freelancers.Freelancer.job_title.ilike(f"%{title}%")  # Case-insensitive job_title match
            )
            .order_by(desc(Freelancers.Freelancer.boost_amount))  # Order by boost_amount in descending order
            .first()  # Get the freelancer with the highest boost
        )

        # Return the highest boost_amount if found, otherwise return 0 or another default
        return 1 + highest_freelancer.boost_amount if highest_freelancer else 1

    def get_price(user_id, session, price, type_of):
        # Initialize the boost to 0
        highest_boost = 0

        # Determine the freelancer type based on the type_of price
        if type_of == "shop":
            # Check for negotiators for shop prices
            highest_boost = (
                session.query(Freelancers.Freelancer)
                .filter(
                    Freelancers.Freelancer.boss == user_id,
                    Freelancers.Freelancer.type_of.ilike("wealth"),  # Negotiator's type_of is 'wealth'
                    Freelancers.Freelancer.job_title.ilike("negotiator")
                )
                .order_by(desc(Freelancers.Freelancer.boost_amount))
                .first()
            )

        elif type_of == "stock":
            # Check for brokers for stock prices
            highest_boost = (
                session.query(Freelancers.Freelancer)
                .filter(
                    Freelancers.Freelancer.boss == user_id,
                    Freelancers.Freelancer.type_of.ilike("stock"),  # Broker's type_of is 'stock'
                    Freelancers.Freelancer.job_title.ilike("broker")
                )
                .order_by(desc(Freelancers.Freelancer.boost_amount))
                .first()
            )

        elif type_of == "tax":
            # Check for consultants for tax prices
            highest_boost = (
                session.query(Freelancers.Freelancer)
                .filter(
                    Freelancers.Freelancer.boss == user_id,
                    Freelancers.Freelancer.type_of.ilike("tax"),  # Consultant's type_of is 'tax'
                    Freelancers.Freelancer.job_title.ilike("consultant")
                )
                .order_by(desc(Freelancers.Freelancer.boost_amount))
                .first()
            )

        # Get the boost amount if a matching freelancer is found, otherwise keep it at 0
        highest_boost_amount = highest_boost.boost_amount if highest_boost else 0

        # Apply the formula (1 - highest_boost_amount) * price
        adjusted_price = (1 - highest_boost_amount) * price

        return adjusted_price
    
    def check_agent(user_id, session, type_of):
        # Query to check if the user has an agent freelancer of the specified type
        agent_exists = (
            session.query(Freelancers.Freelancer)
            .filter(
                Freelancers.Freelancer.boss == user_id,  # Match the user ID directly
                Freelancers.Freelancer.job_title.ilike("agent"),  # Check for job title "Agent"
                Freelancers.Freelancer.type_of.ilike(type_of)  # Match the specified type
            )
            .first()  # Retrieve the first match (if any)
        )

        # Return True if an agent freelancer of the specified type exists, otherwise return False
        return agent_exists is not None


