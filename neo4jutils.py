from neo4j import GraphDatabase
import pandas as pd

# The following class is based on the "Create a graph database in Neo4j using Python" 
# tutorial by CJ Sullivan, Feb 10, 2021. 
# https://towardsdatascience.com/create-a-graph-database-in-neo4j-using-python-4172d40f89c4


class Neo4jConnection:
    
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)
        
    def close(self):
        if self.__driver is not None:
            self.__driver.close()
        
    def query(self, query, parameters=None, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try: 
            session = self.__driver.session(database=db) if db is not None else self.__driver.session() 
            response = list(session.run(query, parameters))
        except Exception as e:
            print("Query failed:", e)
        finally: 
            if session is not None:
                session.close()
        return response
    
    def query_to_dataframe(self, query, parameters=None, db=None):
        df = pd.DataFrame([dict(_) for _ in self.query(query, parameters, db)])
        return df