import os
import random
from datetime import datetime, timedelta
import psycopg2
from pymongo import MongoClient
from faker import Faker

fake = Faker()

def generate_postgres_data():
    conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('POSTGRES_HOST'),
        port=5432
    )
    cursor = conn.cursor()

    # Users
    cursor.execute("TRUNCATE TABLE Users CASCADE;")
    users = []
    for _ in range(10):
        users.append((
            fake.first_name(),
            fake.last_name(),
            fake.email(),
            fake.phone_number(),
            random.choice(['Gold', 'Silver', 'Bronze'])
        ))
    cursor.executemany("""
        INSERT INTO Users (first_name, last_name, email, phone, loyalty_status)
        VALUES (%s, %s, %s, %s, %s);
    """, users)

    # ProductCategories
    cursor.execute("TRUNCATE TABLE ProductCategories CASCADE;")
    categories = [(fake.word(), None) for _ in range(5)]
    cursor.executemany("""
        INSERT INTO ProductCategories (name, parent_category_id)
        VALUES (%s, %s);
    """, categories)

    # Products
    cursor.execute("TRUNCATE TABLE Products CASCADE;")
    products = []
    for _ in range(10):
        products.append((
            fake.word(),
            fake.text(),
            random.randint(1, 5),
            round(random.uniform(10.0, 500.0), 2),
            random.randint(10, 100)
        ))
    cursor.executemany("""
        INSERT INTO Products (name, description, category_id, price, stock_quantity)
        VALUES (%s, %s, %s, %s, %s);
    """, products)

    # Orders
    cursor.execute("TRUNCATE TABLE Orders CASCADE;")
    orders = []
    for _ in range(10):
        orders.append((
            random.randint(1, 10),
            fake.date_time_this_year(),
            round(random.uniform(50.0, 1000.0), 2),
            random.choice(['Pending', 'Shipped', 'Delivered', 'Cancelled']),
            fake.date_time_this_year() + timedelta(days=3)
        ))
    cursor.executemany("""
        INSERT INTO Orders (user_id, order_date, total_amount, status, delivery_date)
        VALUES (%s, %s, %s, %s, %s);
    """, orders)

    # OrderDetails
    cursor.execute("TRUNCATE TABLE OrderDetails CASCADE;")
    order_details = []
    for _ in range(20):
        order_details.append((
            random.randint(1, 10),
            random.randint(1, 10),
            random.randint(1, 5),
            round(random.uniform(10.0, 100.0), 2),
            round(random.uniform(10.0, 500.0), 2)
        ))
    cursor.executemany("""
        INSERT INTO OrderDetails (order_id, product_id, quantity, price_per_unit, total_price)
        VALUES (%s, %s, %s, %s, %s);
    """, order_details)

    # ProductReviews
    cursor.execute("TRUNCATE TABLE ProductReviews CASCADE;")
    reviews = []
    for _ in range(10):
        reviews.append((
            random.randint(1, 10),
            random.randint(1, 10),
            random.randint(1, 5),
            fake.text(),
            fake.date_time_this_year(),
            random.choice(['Approved', 'Pending', 'Rejected']),
            random.randint(0, 100),
            ['image1.jpg', 'image2.png']
        ))
    cursor.executemany("""
        INSERT INTO ProductReviews (user_id, product_id, rating, review_text, creation_date, review_status, helpful_votes, attached_media)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """, reviews)

    # SupportChats
    cursor.execute("TRUNCATE TABLE SupportChats CASCADE;")
    chats = []
    for _ in range(5):
        chats.append((
            random.randint(1, 10),
            random.randint(1, 5),
            fake.date_time_this_year(),
            fake.date_time_this_year() + timedelta(hours=1),
            random.choice(['Open', 'Closed']),
            ['Hello', 'How can I help you?'],
            random.randint(1, 10),
            random.choice(['Technical', 'Billing'])
        ))
    cursor.executemany("""
        INSERT INTO SupportChats (user_id, support_agent_id, start_time, end_time, chat_status, messages, satisfaction_score, issue_type)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """, chats)

    # Cashback
    cursor.execute("TRUNCATE TABLE Cashback CASCADE;")
    cashback_entries = []
    for _ in range(10):
        cashback_entries.append((
            random.randint(1, 10),
            random.randint(1, 10),
            round(random.uniform(5.0, 50.0), 2),
            random.choice(['Pending', 'Processed']),
            fake.date_time_this_year(),
            random.choice(['Checked', 'Unchecked'])
        ))
    cursor.executemany("""
        INSERT INTO Cashback (user_id, order_id, cashback_amount, cashback_status, creation_date, fraud_check_status)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, cashback_entries)

    # Warehouse
    cursor.execute("TRUNCATE TABLE Warehouse CASCADE;")
    warehouses = []
    for _ in range(5):
        warehouses.append((
            fake.city(),
            random.randint(1000, 5000),
            random.randint(1, 5),
            round(random.uniform(1000.0, 5000.0), 2),
            random.randint(500, 3000)
        ))
    cursor.executemany("""
        INSERT INTO Warehouse (location, capacity, manager_id, rental_cost, available_capacity)
        VALUES (%s, %s, %s, %s, %s);
    """, warehouses)

    # Promotions
    cursor.execute("TRUNCATE TABLE Promotions CASCADE;")
    promotions = []
    for _ in range(5):
        promotions.append((
            fake.word(),
            fake.text(),
            round(random.uniform(5.0, 50.0), 2),
            fake.date_time_this_year(),
            fake.date_time_this_year() + timedelta(days=30)
        ))
    cursor.executemany("""
        INSERT INTO Promotions (name, description, discount_rate, start_date, end_date)
        VALUES (%s, %s, %s, %s, %s);
    """, promotions)

    conn.commit()
    cursor.close()
    conn.close()
    print("Postgres data have been generated.")


def generate_mongo_data():
    mongo_client = MongoClient(host=os.getenv('MONGO_HOST'), port=int(os.getenv('MONGO_PORT')))
    db = mongo_client['test_db']

    # UserSessions
    db.UserSessions.delete_many({})
    sessions = []
    for _ in range(10):
        sessions.append({
            "session_id": fake.uuid4(),
            "user_id": random.randint(1, 10),
            "start_time": fake.date_time_this_year(),
            "end_time": fake.date_time_this_year() + timedelta(hours=1),
            "pages_visited": [fake.uri_path() for _ in range(3)],
            "device": random.choice(["Desktop", "Mobile"]),
            "actions": ["click", "view", "add_to_cart"]
        })
    db.UserSessions.insert_many(sessions)

    # ProductPriceHistory
    db.ProductPriceHistory.delete_many({})
    price_history = []
    for product_id in range(1, 11):
        price_history.append({
            "product_id": product_id,
            "price_changes": [
                {"date": fake.date_time_this_year(), "price": round(random.uniform(10.0, 500.0), 2)}
            ],
            "current_price": round(random.uniform(10.0, 500.0), 2),
            "currency": "USD"
        })
    db.ProductPriceHistory.insert_many(price_history)

    # ProductReviews (ModerationQueue)
    db.ModerationQueue.delete_many({})
    reviews = []
    for _ in range(10):
        reviews.append({
            "review_id": random.randint(1, 100),
            "user_id": random.randint(1, 10),
            "product_id": random.randint(1, 10),
            "review_text": fake.text(),
            "rating": random.randint(1, 5),
            "moderation_status": random.choice(["Pending", "Approved", "Rejected"]),
            "flags": [fake.word() for _ in range(2)],
            "submitted_at": fake.date_time_this_year()
        })
    db.ModerationQueue.insert_many(reviews)

    # ProductRecommendations
    db.ProductRecommendations.delete_many({})
    recommendations = []
    for _ in range(10):
        recommendations.append({
            "user_id": random.randint(1, 10),
            "recommended_products": [random.randint(1, 10) for _ in range(5)],
            "last_updated": fake.date_time_this_year()
        })
    db.ProductRecommendations.insert_many(recommendations)

    # UserQueries (SearchQueries)
    db.SearchQueries.delete_many({})
    queries = []
    for _ in range(10):
        queries.append({
            "query_id": random.randint(1, 100),
            "user_id": random.randint(1, 10),
            "query_text": fake.sentence(),
            "timestamp": fake.date_time_this_year(),
            "filters": [fake.word() for _ in range(3)],
            "results_count": random.randint(0, 100)
        })
    db.SearchQueries.insert_many(queries)

    print("MongoDB data have been generated.")


if __name__ == "__main__":
    generate_postgres_data()
    generate_mongo_data()
