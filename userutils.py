import json
import datetime
import requests
import pandas as pd
import hashlib
import uuid

class User:
    def __init__(self, conn):
        self.__conn = conn

    def __serialize_datetime(obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        raise TypeError("Type not serializable")

    
    def get_users(self, user_id="", last_name=""):
        try: 
            if user_id != "" and user_id != None:
                qry = "MATCH (u:User)-[rel:BELONGS_TO_ROLE]->(r:Role) WHERE u.id = $id RETURN u,r "
                params = {"id" : user_id}
            elif last_name != "" and last_name != None:
                qry = "MATCH (u:User)-[rel:BELONGS_TO_ROLE]->(r:Role) WHERE lowerCase(u.last_name) = $last_name RETURN u,r "
                params = {"last_name" : last_name.lower()}
            else:
                qry = "MATCH (u:User)-[rel:BELONGS_TO_ROLE]->(r:Role) RETURN u, r"
                params = {}
            
            result = self.__conn.query(qry, parameters=params)
            #return result
            users = []
            if result != None:
                for record in result:
                    users.append(record.data())
            return json.dumps(users, default=str)
        except Neo4jError as e:
            # Log or handle the error as needed
            error_message = f"Neo4j Error: {e}"
            return json.dumps({"error": error_message})
        except Exception as e:
            # Log or handle other unexpected errors
            error_message = f"Unexpected Error: {e}"
            return json.dumps({"error": error_message})
    
    
    def users_pivot_table_with_roles(self, user_data):
        try:
            data = []
            for user in user_data:
                row = [user['u']['id'], user['u']['last_name'], user['u']['first_name'], user['u']['email'], user['u']['affiliation'], user['u']['date_created'], user['r']['role_name']]
                data.append(row)
            df = pd.DataFrame(data, columns=['user_id', 'last_name', 'first_name', 'email', 'affiliation', 'date_created', 'role_name'])
            temp = pd.pivot_table(df, values=['role_name'], 
                    index=['user_id', 'last_name', 'first_name', 'email', 'affiliation', 'date_created'],
                    columns=['role_name'], aggfunc={'role_name':'count'}, fill_value=0)
            temp.reset_index(inplace=True)
            temp.columns = [''.join(col).strip().lower().replace('role_name', '') for col in temp.columns.values]
            return temp.to_json(orient='records')
        except Exception as e:
            return json.dumps({"error": f"An error occurred: {str(e)}"})
    
    def update_user_data(self, user_id, first_name, last_name, email, affiliation, roles, password=""):
        if user_id != "" and first_name != "" and last_name != "" and affiliation != "":
            qry = "MATCH (u:User) WHERE u.id = $user_id "
            qry += "SET u.first_name = $first_name, "
            qry += "u.last_name = $last_name, "
            qry += "u.email = $email, "
            qry += "u.affiliation = $affiliation "
            qry += "RETURN u; "
            params = {
                "user_id" : user_id, 
                "first_name" : first_name, 
                "last_name" : last_name, 
                "email" : email, 
                "affiliation" : affiliation
            }
            result = self.__conn.query(qry, parameters=params)

            if password != "":
                qry = "MATCH (u:User) WHERE u.id = $user_id "
                qry += "SET u.password = $password RETURN u; "
                password = hashlib.md5(password.encode("utf-8"))
                params = {
                    "user_id" : user_id,
                    "password" : password.hexdigest()
                }
                #return str(params)
                result = self.__conn.query(qry, parameters=params)

            for k, v in roles.items():
                if roles[k] == 1:
                    qry = "MATCH (u:User), (r:Role) "
                    qry += "WHERE u.id = $user_id AND toLower(r.role_name) = toLower($role_name) "
                    qry += "MERGE (u)-[rel:BELONGS_TO_ROLE]->(r) RETURN u, rel, r; "
                else:
                    qry = "MATCH (u:User)-[rel:BELONGS_TO_ROLE]->(r:Role) "
                    qry += "WHERE u.id = $user_id AND toLower(r.role_name) = toLower($role_name) "
                    qry += "DELETE rel RETURN u, r; "
                params = {
                    "user_id" : user_id,
                    "role_name" : k
                }
                result = self.__conn.query(qry, parameters=params)
        return user_id
    

    def create_new_user(self, first_name, last_name, email, affiliation, roles, password):
        if first_name != "" and last_name != "" and affiliation != "" and email != "" and password != "":
            user_id = str(uuid.uuid4())
            password = hashlib.md5(password.encode("utf-8"))

            qry = "CREATE (u:User {id : $user_id, "
            qry += "first_name : $first_name, "
            qry += "last_name : $last_name, "
            qry += "email : $email, "
            qry += "affiliation : $affiliation, "
            qry += "password : $password,  "
            qry += "date_created : datetime() })  "
            qry += "RETURN u; "
            params = {
                "user_id" : user_id, 
                "first_name" : first_name, 
                "last_name" : last_name, 
                "email" : email, 
                "affiliation" : affiliation,
                "password" : password.hexdigest()
            }
            #return str(params)
            result = self.__conn.query(qry, parameters=params)

            

            for k, v in roles.items():
                if roles[k] == 1:
                    qry = "MATCH (u:User), (r:Role) "
                    qry += "WHERE u.id = $user_id AND toLower(r.role_name) = toLower($role_name) "
                    qry += "MERGE (u)-[rel:BELONGS_TO_ROLE]->(r) RETURN u, rel, r; "
                else:
                    qry = "MATCH (u:User)-[rel:BELONGS_TO_ROLE]->(r:Role) "
                    qry += "WHERE u.id = $user_id AND toLower(r.role_name) = toLower($role_name) "
                    qry += "DELETE rel RETURN u, r; "
                params = {
                    "user_id" : user_id,
                    "role_name" : k
                }
                result = self.__conn.query(qry, parameters=params)
        return user_id
    
    def validate_login(self, email, password):
        password = hashlib.md5(password.encode())
        qry = "MATCH (u:User)-[rel]-(r:Role) WHERE u.email = $email AND u.password = $password RETURN u, r; "
        params = {
            "email" : email,
            "password" : password.hexdigest()
        }
        #return str(params)
        result = self.__conn.query(qry, parameters=params)
        user_data = []
        for record in result:
            user_data.append(record.data())

        return user_data
        
        