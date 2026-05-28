from sqlalchemy import inspect
from app.database.session import engine

def get_database_schema_context() -> str:
    """
    Programmatically reflects the live database using SQLAlchemy inspection.
    Generates a clean markdown schema context for the AI Agent.
    """
    # Initialize the database inspector
    inspector = inspect(engine)
    
    schema_output = "### LIVE DATABASE SCHEMA CONTEXT\n"
    schema_output += "Use the following exact table definitions and relational mappings:\n\n"
    
    # Fetch all table names currently inside the public schema
    table_names = inspector.get_table_names()
    
    for table_name in table_names:
        schema_output += f"#### Table: `{table_name}`\n"
        schema_output += "Columns:\n"
        
        # Extract metadata for every single column in the current table
        columns = inspector.get_columns(table_name)
        pk_columns = inspector.get_pk_constraint(table_name).get("constrained_columns", [])
        
        for col in columns:
            col_name = col["name"]
            col_type = str(col["type"])
            is_nullable = "NULL" if col.get("nullable", True) else "NOT NULL"
            
            # Label primary keys clearly so the LLM understands the indexing anchors
            pk_label = " [PRIMARY KEY]" if col_name in pk_columns else ""
            
            schema_output += f"  - `{col_name}` ({col_type}) {is_nullable}{pk_label}\n"
            
        # Extract foreign key linkages to assist the AI in writing JOIN statements accurately
        fk_constraints = inspector.get_foreign_keys(table_name)
        if fk_constraints:
            schema_output += "Relationships / Joins:\n"
            for fk in fk_constraints:
                constrained_cols = fk["constrained_columns"]
                referred_table = fk["referred_table"]
                referred_cols = fk["referred_columns"]
                
                # Format: local_column references foreign_table(foreign_column)
                for local_c, foreign_c in zip(constrained_cols, referred_cols):
                    schema_output += f"  - `{table_name}.{local_c}` references `{referred_table}.{foreign_c}`\n"
                    
        schema_output += "\n"
        
    return schema_output