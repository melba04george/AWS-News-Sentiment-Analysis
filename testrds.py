from sqlalchemy import create_engine

# Replace with your actual RDS endpoint
rds_endpoint = "newsdatabase.c1o4u2ksu2dq.eu-north-1.rds.amazonaws.com"
engine = create_engine(f"postgresql://postgres:awsadmin1234@{rds_endpoint}:5432/postgres")

# Try a simple query
import pandas as pd
print(pd.read_sql("SELECT version();", engine))
