import psycopg2

try:
    conn = psycopg2.connect(
        host="aws-1-ap-south-1.pooler.supabase.com",
        port=6543,
        dbname="postgres",
        user="postgres.ufcxpwybejclrymjlfmn",
        password="Maneesh@12574",
        sslmode="require"
    )
    print("✅ Connection successful")
    conn.close()
except Exception as e:
    print("❌ Connection failed:", e)
