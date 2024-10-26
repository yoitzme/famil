-- Events table for calendar
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE,
    event_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chores table
CREATE TABLE IF NOT EXISTS chores (
    id SERIAL PRIMARY KEY,
    task VARCHAR(255) NOT NULL,
    assigned_to VARCHAR(100),
    due_date DATE,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Grocery items table
CREATE TABLE IF NOT EXISTS grocery_items (
    id SERIAL PRIMARY KEY,
    item VARCHAR(255) NOT NULL,
    quantity INTEGER DEFAULT 1,
    category VARCHAR(100),
    added_by VARCHAR(100),
    purchased BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- School events table
CREATE TABLE IF NOT EXISTS school_events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    event_date DATE NOT NULL,
    event_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    notification_id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_status BOOLEAN DEFAULT FALSE,
    priority INTEGER DEFAULT 1 -- 1: low, 2: medium, 3: high
);
