class DatabaseError(Exception):
    pass

class DatabaseConnectionError(DatabaseError):
    pass

class DatabaseQueryError(DatabaseError):
    pass