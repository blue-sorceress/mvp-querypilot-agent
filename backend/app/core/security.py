import re

class SQLSecurityValidationError(Exception):
    """Custom exception raised when a dangerous SQL command is detected."""
    pass

def verify_sql_safety(generated_sql: str) -> bool:
    """
    Inspects the AI-generated SQL query BEFORE it touches the database.
    Blocks any data-modifying or destructive actions.
    """
    # 1. Standardize text to uppercase for robust matching
    clean_sql = generated_sql.upper().strip()
    
    # 2. Define our blacklist of destructive SQL keywords
    banned_keywords = [
        "DROP", 
        "DELETE", 
        "UPDATE", 
        "INSERT", 
        "ALTER", 
        "TRUNCATE", 
        "GRANT", 
        "REVOKE"
    ]
    
    # 3. Check for exact keyword matches using regex boundaries
    for keyword in banned_keywords:
        # \b ensures we match the exact word 'DROP', not words like 'DROPoff' or 'droplet'
        if re.search(r'\b' + keyword + r'\b', clean_sql):
            raise SQLSecurityValidationError(
                f"Security Intercept: Banned database operation '{keyword}' detected in query."
            )
            
    # 4. Enforce that the query MUST start with a read-only SELECT statement
    if not clean_sql.startswith("SELECT") and not clean_sql.startswith("WITH"):
        raise SQLSecurityValidationError(
            "Security Intercept: Query must be a read-only statement (must start with SELECT or WITH)."
        )
        
    return True