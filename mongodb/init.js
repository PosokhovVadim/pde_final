db.UserSessions.insertMany([
    {
        session_id: "s1",
        user_id: 1,
        start_time: new Date("2025-01-02T08:00:00"),
        end_time: new Date("2025-01-02T09:00:00"),
        pages_visited: ["home", "product_page"],
        device: "Desktop",
        actions: ["click", "add_to_cart"]
    },
    {
        session_id: "s2",
        user_id: 2,
        start_time: new Date("2025-01-02T10:00:00"),
        end_time: new Date("2025-01-02T11:00:00"),
        pages_visited: ["home", "cart"],
        device: "Mobile",
        actions: ["view", "checkout"]
    }
]);

db.ProductPriceHistory.insertMany([
    {
        product_id: 1,
        price_changes: [
            { date: new Date("2025-01-01"), price: 99.99 },
            { date: new Date("2025-01-02"), price: 89.99 }
        ],
        current_price: 89.99,
        currency: "USD"
    },
    {
        product_id: 2,
        price_changes: [
            { date: new Date("2025-01-01"), price: 29.99 },
            { date: new Date("2025-01-02"), price: 19.99 }
        ],
        current_price: 19.99,
        currency: "USD"
    }
]);

db.EventLogs.insertMany([
    {
        event_id: 1,
        timestamp: new Date("2025-01-02T08:15:00"),
        event_type: "Page View",
        details: { page: "home", user_id: 1 }
    },
    {
        event_id: 2,
        timestamp: new Date("2025-01-02T10:20:00"),
        event_type: "Purchase",
        details: { order_id: 1, user_id: 2 }
    }
]);

db.SupportTickets.insertMany([
    {
        ticket_id: 1,
        user_id: 1,
        status: "Open",
        messages: ["Hello, I need help with my order."],
        created_at: new Date("2025-01-02T08:00:00"),
        updated_at: new Date("2025-01-02T09:00:00"),
        issue_type: "Order Issue"
    },
    {
        ticket_id: 2,
        user_id: 2,
        status: "Closed",
        messages: ["My issue has been resolved, thank you."],
        created_at: new Date("2025-01-02T10:00:00"),
        updated_at: new Date("2025-01-02T11:00:00"),
        issue_type: "Technical Issue"
    }
]);

db.ProductRecommendations.insertMany([
    {
        user_id: 1,
        recommended_products: [1, 3, 5],
        last_updated: new Date("2025-01-02T09:00:00")
    },
    {
        user_id: 2,
        recommended_products: [2, 4, 6],
        last_updated: new Date("2025-01-02T11:00:00")
    }
]);

db.ModerationQueue.insertMany([
    {
        review_id: 1,
        user_id: 1,
        product_id: 1,
        review_text: "Great product!",
        rating: 5,
        moderation_status: "Approved",
        flags: [],
        submitted_at: new Date("2025-01-02T08:30:00")
    },
    {
        review_id: 2,
        user_id: 2,
        product_id: 2,
        review_text: "Not bad, but could be better.",
        rating: 3,
        moderation_status: "Approved",
        flags: ["Needs Improvement"],
        submitted_at: new Date("2025-01-02T10:30:00")
    }
]);

db.SearchQueries.insertMany([
    {
        query_id: 1,
        user_id: 1,
        query_text: "How can I track my order?",
        timestamp: new Date("2025-01-02T08:10:00"),
        filters: ["Order Tracking"],
        results_count: 5
    },
    {
        query_id: 2,
        user_id: 2,
        query_text: "What is the return policy?",
        timestamp: new Date("2025-01-02T10:15:00"),
        filters: ["Return Policy"],
        results_count: 3
    }
]);
