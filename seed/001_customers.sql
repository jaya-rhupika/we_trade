INSERT INTO customer (
    customer_id,
    name,
    dob,
    email,
    password_hashed
) VALUES
    (
        'cust-001',
        'Alice Johnson',
        '1990-05-14',
        'alice.johnson@example.com',
        '$2b$12$abcdefghijklmnopqrstuuV6f4zKqY8wJx9N2rP5sT7u'
    ),
    (
        'cust-002',
        'Bob Smith',
        '1985-11-23',
        'bob.smith@example.com',
        '$2b$12$bcdefghijklmnopqrstuuvV6f4zKqY8wJx9N2rP5sT7u'
    ),
    (
        'cust-003',
        'Carol Williams',
        '1978-02-09',
        'carol.williams@example.com',
        '$2b$12$cdefghijklmnopqrstuuvwV6f4zKqY8wJx9N2rP5sT7u'
    ),
    (
        'cust-004',
        'David Brown',
        '1995-07-30',
        'david.brown@example.com',
        '$2b$12$defghijklmnopqrstuuvwxV6f4zKqY8wJx9N2rP5sT7u'
    ),
    (
        'cust-005',
        'Emma Davis',
        '1969-12-18',
        'emma.davis@example.com',
        '$2b$12$efghijklmnopqrstuuvwxyV6f4zKqY8wJx9N2rP5sT7u'
    ),
    (
        'cust-006',
        'Frank Miller',
        '2001-04-02',
        'frank.miller@example.com',
        '$2b$12$fghijklmnopqrstuuvwxyzV6f4zKqY8wJx9N2rP5sT7u'
    );