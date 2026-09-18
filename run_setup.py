import pyodbc

# Connect to the MSSQL container as SA
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=master;"
    "UID=sa;"
    "PWD=FdeEnterprisePass123!;"
    "TrustServerCertificate=yes",
    autocommit=True,
)
cur = conn.cursor()

print("1. Executing scripts/setup_security_and_view.sql...")
with open("scripts/setup_security_and_view.sql", "r") as f:
    sql_script = f.read()

for batch in sql_script.split("GO"):
    b = batch.strip()
    if b:
        try:
            cur.execute(b)
        except pyodbc.Error as e:
            # Safely skip 'object already exists' errors (2714)
            if "2714" not in str(e):
                print(f"Notice: {e}")

print("2. Provisioning FDE_VIEWS.AgentAuditLog table...")
ddl = """
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'FDE_VIEWS')
    EXEC('CREATE SCHEMA FDE_VIEWS');

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'AgentAuditLog' AND schema_id = SCHEMA_ID('FDE_VIEWS'))
BEGIN
    CREATE TABLE FDE_VIEWS.AgentAuditLog (
        LogID INT IDENTITY(1,1) PRIMARY KEY,
        Timestamp DATETIME DEFAULT GETDATE(),
        SessionID VARCHAR(50),
        NodeExecuted VARCHAR(50),
        ToolName VARCHAR(100),
        Content NVARCHAR(MAX)
    );
    GRANT INSERT ON FDE_VIEWS.AgentAuditLog TO USR_FDE_RO;
END
"""

cur.execute(ddl)
print("✅ Phases 2 & 4 database operations completed successfully!")
