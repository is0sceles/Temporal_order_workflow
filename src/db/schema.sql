CREATE TABLE orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  state TEXT NOT NULL,
  address_json JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE payments (
  payment_id TEXT PRIMARY KEY,          -- external or Temporal activity ID
  order_id UUID REFERENCES orders(id),
  status TEXT NOT NULL,
  amount NUMERIC,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id UUID REFERENCES orders(id),
  type TEXT NOT NULL,
  payload_json JSONB,
  ts TIMESTAMP DEFAULT NOW()
);
