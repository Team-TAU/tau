CREATE TABLE IF NOT EXISTS kv_store (
   id bool PRIMARY KEY DEFAULT true,
   data text,
   CONSTRAINT onerow_uni CHECK (id)
);
