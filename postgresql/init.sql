CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(15),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    loyalty_status VARCHAR(20)
);

CREATE TABLE Products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    category_id INT,
    price DECIMAL(10, 2),
    stock_quantity INT,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Orders (
    order_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES Users(user_id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2),
    status VARCHAR(20),
    delivery_date TIMESTAMP
);

CREATE TABLE OrderDetails (
    order_detail_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES Orders(order_id),
    product_id INT REFERENCES Products(product_id),
    quantity INT,
    price_per_unit DECIMAL(10, 2),
    total_price DECIMAL(10, 2)
);

CREATE TABLE ProductCategories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    parent_category_id INT REFERENCES ProductCategories(category_id)
);

CREATE TABLE ProductReviews (
    review_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES Users(user_id),
    product_id INT REFERENCES Products(product_id),
    rating INT CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    review_status VARCHAR(20),
    helpful_votes INT DEFAULT 0,
    attached_media TEXT[]
);

CREATE TABLE SupportChats (
    chat_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES Users(user_id),
    support_agent_id INT,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    chat_status VARCHAR(20),
    messages TEXT[],
    satisfaction_score INT CHECK (satisfaction_score BETWEEN 1 AND 10),
    issue_type VARCHAR(50)
);

CREATE TABLE Cashback (
    cashback_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES Users(user_id),
    order_id INT REFERENCES Orders(order_id),
    cashback_amount DECIMAL(10, 2),
    cashback_status VARCHAR(20),
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fraud_check_status VARCHAR(20)
);

CREATE TABLE Warehouse (
    warehouse_id SERIAL PRIMARY KEY,
    location VARCHAR(100),
    capacity INT,
    manager_id INT,
    rental_cost DECIMAL(10, 2),
    available_capacity INT
);

CREATE TABLE Promotions (
    promotion_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    discount_rate DECIMAL(5, 2),
    start_date TIMESTAMP,
    end_date TIMESTAMP
);

INSERT INTO Users (first_name, last_name, email, phone, loyalty_status)
VALUES 
('John', 'Doe', 'john.doe@example.com', '123-456-7890', 'Gold'),
('Jane', 'Smith', 'jane.smith@example.com', '987-654-3210', 'Silver');
