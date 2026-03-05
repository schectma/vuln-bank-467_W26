-- Seed data for vulnerable_bank database
-- Non-destructive: only runs if tables are empty

INSERT INTO users (id, username, password, account_number, balance, is_admin)
VALUES
  (1, 'admin', 'admin123', 'ADMIN001', 1000000.00, TRUE),
  (100, 'testuser1', 'testpassword1', 'TEST001', 1000.00, FALSE),
  (101, 'testuser2', 'testpassword2', 'TEST002', 1000.00, FALSE),
  (102, 'testuser3', 'testpassword3', 'TEST003', 1000.00, FALSE)
ON CONFLICT (id) DO NOTHING;

INSERT INTO transactions (from_account, to_account, amount, transaction_type, description)
VALUES
  ('TEST001', 'TEST002', 100.00, 'transfer', 'Test transfer 1'),
  ('TEST002', 'TEST001', 50.00, 'transfer', 'Test transfer 2'),
  ('TEST001', 'TEST003', 25.00, 'transfer', 'Test transfer 3')
ON CONFLICT DO NOTHING;

INSERT INTO virtual_cards (id, user_id, card_number, cvv, expiry_date, card_limit, current_balance, card_type, is_frozen)
VALUES
  (1, 100, '1111222233334444', '123', '12/26', 1000.00, 1000.00, 'standard', FALSE),
  (2, 101, '5555666677778888', '456', '12/26', 1000.00, 1000.00, 'standard', FALSE)
ON CONFLICT (card_number) DO NOTHING;

INSERT INTO bill_payments (user_id, biller_id, amount, payment_method, card_id, reference_number, status, description)
VALUES
  (100, 1, 75.00, 'balance', NULL, 'REF001', 'completed', 'Water bill payment'),
  (100, 2, 120.00, 'virtual_card', 1, 'REF002', 'completed', 'Electric bill payment')
ON CONFLICT DO NOTHING;
