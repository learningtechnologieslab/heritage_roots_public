import json
import datetime
import requests

class RestApi:
    def __init__(self, conn):
        self.__conn = conn

    def __serialize_datetime(obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        raise TypeError("Type not serializable")

    def get_narrative(self, narrative_id):
        qry = "MATCH (narrative:Narrative) WHERE narrative.id = $narrative_id " 
        qry += "OPTIONAL MATCH (narrative_media:Media)-[r1]->(narrative) "
        qry += "OPTIONAL MATCH (narrative_file:File)-[r2]->(narrative) "
        qry += "OPTIONAL MATCH (animal:Animal)-[r3]->(narrative) "
        qry += "OPTIONAL MATCH (animal_media:Media)-[r4]-(animal) "
        qry += "OPTIONAL MATCH (animal_file:File)-[r5]-(animal) "
        qry += "OPTIONAL MATCH (plant:Plant)-[r6]->(narrative) "
        qry += "OPTIONAL MATCH (plant_media:Media)-[r7]-(plant) "
        qry += "OPTIONAL MATCH (plant_file:File)-[r8]-(plant) "
        qry += "OPTIONAL MATCH (object:Object)-[r9]->(narrative) "
        qry += "OPTIONAL MATCH (object_media:Media)-[r10]-(object) "
        qry += "OPTIONAL MATCH (object_file:File)-[r11]-(object) "
        qry += "RETURN  "
        qry += "narrative, narrative_media, narrative_file,  "
        qry += "animal, animal_media, animal_file,  "
        qry += "plant, plant_media, plant_file,  "
        qry += "object, object_media, object_file; "

        params = {
            "narrative_id" : narrative_id
        }

        
        data = []
        result = self.__conn.query(qry, parameters=params)
        if result != None:
            for record in result:
                data.append(record.data())
        
        return data

    
    def get_object(self, object_id, include_media = True):
        qry = "MATCH (o:Object)-[r]-(f:File) WHERE o.id = $object_id RETURN o, r, f;"
        params = {
            "object_id" : object_id
        }
        
        object_data = {}
        file_data = []
        result = self.__conn.query(qry, parameters=params)
        if result != None:
            for record in result:
                for k, v in record.data().items():
                    if v != None:
                        if k[0] == 'o':
                            object_data['item_id'] = v['id']
                            object_data['item_type'] = "object"
                            object_data['item_name'] = v['object_name']
                        else:
                            file_data.append(v)
            object_data['files'] = file_data
        
        return json.dumps(object_data)