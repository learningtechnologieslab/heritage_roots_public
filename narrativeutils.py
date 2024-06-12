
from uuid import uuid4
from urllib.request import urlopen
import json
import pandas as pd
from openai import OpenAI
import ast

# This class needs to be refactored.  
class Narrative:
    # Class constructor
    # Accepts neo4j connection object as a parameter at instantiation
    def __init__(self, conn):
        self.__conn = conn

    # Creates a node of type "Narrative" in Neo4J database
    # id: Auto-generated UUID
    # title: Title of the narrative 
    # text: The body of the narrative
    # language: The language of the narrative (e.g. 'English')
    # notes: Any notes provided by the author
    def add_narrative(self, title, text, author, translator, presenter, date_recorded, orig_language, trans_language, country, notes=""):
        qry = "CREATE (n:Narrative {id: $id, title: $title, text: $text, "
        qry += "author: $author, translator: $translator, presenter: $presenter, date_recorded: $date_recorded, "
        qry += "orig_language: $orig_language, trans_language: $trans_language, country: $country, "
        qry += "notes: $notes})"
        
        #print(qry)
        
        story_id = str(uuid4())
        
        params = {
            "id" : story_id,
            "title" : title,
            "text" : text, 
            "author" : author,
            "translator" : translator, 
            "presenter" : presenter, 
            "date_recorded" : date_recorded, 
            "orig_language" : orig_language, 
            "trans_language" : trans_language, 
            "country" : country,
            "notes" : notes
        }
        
        
        #print(params)
        self.__conn.query(qry, parameters=params)
        return story_id

    # Retrieve a narrative node by ID from Neo4J database
    # narrative_id: UUID() of the narrative node   
    def get_narrative(self, narrative_id):
        qry = "MATCH (n:Narrative {id : $id}) RETURN n "
        params = {"id" : narrative_id}
        result = self.__conn.query(qry, parameters=params)
        #print(result)
        if result != None:
            return result[0]['n'].__dict__['_properties']
        else:
            return None
        
    def get_animal_names(self, narrative_id):
        #qry = "MATCH (a:Animal) WHERE a.common_name <> '' RETURN a.common_name; "
        qry = "MATCH (a:Animal) WHERE a.common_name <> '' "
        qry += "OPTIONAL MATCH (a)-[r]-(n:Narrative) WHERE n.id = $narrative_id "
        qry += "RETURN a.id AS animal_id, a.common_name AS animal_name, n.id AS narrative_id; "
        print(qry)
        
        params = {"narrative_id" : narrative_id}
        
        result = self.__conn.query(qry, parameters=params)
        data = []
        for record in result:
            item = [
                record.data()['animal_id'],
                record.data()['animal_name'],
                record.data()['narrative_id']
            ]
            #print(item)
            data.append(item)
        df = pd.DataFrame(data)
        df.columns = ['animal_id', 'animal_name', 'narrative_id']
        df.fillna('', inplace=True)
        #df['animal_name'] = df['animal_name'].apply(lambda x: x.lower())
        return df

    # Open a data file containing animals, plants, or insects. 
    # Match data in the file with the text of the narrative
    # Return a list of matches - animals, plans, insects that
    # exist in the body of the text
    # data_file: text file containing a list of animals, plants, or insects
    # text: text of the narrative
    def get_matched_data_list(self, data_file, text, narrative_id=""):
        matches = []
        db_items = self.get_animal_names(narrative_id)
        items = pd.read_csv(data_file) # read data file
        #items = pd.concat([items, db_items], axis=0)
        for idx, row in db_items.iterrows():
            if str(row['animal_name']).lower() in text.lower(): # find matches
                item = {
                    "animal_id" : row['animal_id'],
                    "animal_name" : row['animal_name'],
                    "narrative_id" : row['narrative_id']
                }
                matches.append(item) # add matches to list
        #print(matches)

        items = items[~items['name'].isin(list(db_items['animal_name']))]
        for item in items['name']: # iterate through items (e.g. animals)
            if str(item).lower() in text.lower(): # find matches
                temp = {
                    "animal_id" : "",
                    "animal_name" : item,
                    "narrative_id" : ""
                }
                matches.append(temp) # add matches to list
        
        return matches
    
    def get_entity_list(self, text, open_ai_api_key, entity_type='animals'):
        client = OpenAI(
            api_key = open_ai_api_key,
        )

        if entity_type == 'animals':
            instruction = {"role": "user", "content": f"Provide a comma-delimited names of animals mentioned in the following text: {text}"}
        elif entity_type == 'plants':
            instruction = {"role": "user", "content": f"Provide a comma-delimited of all of names of plants mentioned in the following text: {text}"}
        
        response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "Output only python list."},
            instruction
            ],
            model="gpt-3.5-turbo",
        )
        
        
        #RESPONSE
        data = response.choices[0].message.content
        print(data)
        temp = data.split(',')
        for i in range(0, len(temp)):
            temp[i] = temp[i].strip()
        return temp
   
    
    
    # Checks if a node exists in Neo4J
    # node_label: Label of a node (e.g., Narrative, Animal)
    # key: Name of a unique identifier attribute
    # parameter: Value of a unique identifier attribute
    def check_node_exists(self, node_label, key, parameter):
        qry = "MATCH (n:" + node_label + " {" + key + ": $" + key + "}) RETURN n"
        #print(qry)
        result = self.__conn.query(qry, parameters=parameter)
        print(result)
        if result == None:
            return False
        else:
            if len(result) > 0:
                return True
            else:
                return False


    # Checks if a node exists in Neo4J
    # node_label: Label of a node (e.g., Narrative, Animal)
    # key: Name of a unique identifier attribute
    # parameter: Value of a unique identifier attribute
    def check_node_exists_get_id(self, node_label, key, parameter):
        qry = "MATCH (n:" + node_label + " {" + key + ": $" + key + "}) RETURN n.id"
        #print(qry)
        result = self.__conn.query(qry, parameters=parameter)
        print(result)
        if result == None:
            return False
        else:
            if len(result) > 0:
                return True
            else:
                return False


    # Retrieves a node from Neo4J
    # node_label: Label of a node (e.g., Narrative, Animal)
    # key: Name of a unique identifier attribute
    # parameter: Value of a unique identifier attribute
    def get_node(self, node_label, key, parameter):
        qry = "MATCH (n:" + node_label + " {" + key + ": $" + key + "}) RETURN n"
        #print(qry)
        result = self.__conn.query(qry, parameters=parameter)
        #print(result)
        return result[0]['n']

    # Creates a node of type "Animal"
    # common_name: Vernacular name of an animal
    # species: Scientific name of the animal's species
    # merge: Boolean parameter specifying whether a node 
    #       should be created even if is a duplicate
    #       or use merge to only create if a node
    #       does not exist. Merge = True is the default
    def create_living_object_node(self, label, common_name, scientific_name, species):
        # kingdom, phylum, class, order, family, genus, and species
        species_id = str(uuid4())
        params = {
            "id" : species_id,
            "common_name" : common_name,
            "scientific_name" : scientific_name,
            "species" : species    
        }
    
        qry = "CREATE  (n:" + label + "{id: $id, common_name: $common_name, scientific_name: $scientific_name, species: $species})"
        
        self.__conn.query(qry, parameters=params)
        return species_id


    def check_taxonomy_node_exists_by_name(self, node_label, attr_name, attr_value):
        qry = "MATCH (n:" + node_label + ") "
        qry += "WHERE toLower(n." + attr_name + ") = toLower($attr_value) RETURN n.id; "

        params = {
            "attr_value" : attr_value
        }
        result = self.__conn.query(qry, parameters=params)
        # print(result)
        if result != None:
            if len(result) > 0:
                for record in result:
                    if record.data()['n.id'] == None:
                        return ""
                    else:
                        return record.data()['n.id']
            else:
                return ""
        else:
            return ""

    def create_taxonomy_node(self, label, attr_name, attr_value):
        node_id = str(uuid4())
        node_data = {
            attr_name : attr_value,
            "id" : node_id
            
        }
        self.create_node(label, node_data)
        return node_id

    def check_species_exists_get_id(self, node_label, keyword):
    
        qry = "MATCH (n:" + node_label + ") "
        qry += "WHERE toLower(n.species) = toLower($keyword) or toLower(n.scientific_name) = toLower($keyword)"
        qry += "RETURN n.id; "
        # print(qry)
        # print(parameter)
        params = {
            "keyword" : keyword
        }
        result = self.__conn.query(qry, parameters=params)
        # print(result)
        if result != None:
            if len(result) > 0:
                for record in result:
                    if record.data()['n.id'] == None:
                        return ""
                    else:
                        return record.data()['n.id']
            else:
                return ""
        else:
            return ""
    

    def create_object_node(self, object_name, description, notes):
        qry = "MERGE (o:Object {"
        qry += "id : $node_id, "
        qry += "object_name : $object_name, "
        qry += "description : $description, "
        qry += "notes : $notes}) RETURN  o; "
        
        params = {
            "node_id" : str(uuid4()),
            "object_name" : object_name,
            "description" : description,
            "notes" : notes
        }
        
        # print(qry)
        
        result = self.__conn.query(qry, parameters=params)
        return json.dumps(params)
    
    def create_concept_node(self, concept_name, description, notes):
        qry = "CREATE (c:Concept {"
        qry += "id : $node_id, "
        qry += "concept_name : $concept_name, "
        qry += "description : $description, "
        qry += "notes : $notes}) RETURN  c; "
        
        params = {
            "node_id" : str(uuid4()),
            "concept_name" : concept_name,
            "description" : description,
            "notes" : notes
        }
        
        # print(qry)
        
        result = self.__conn.query(qry, parameters=params)
        return json.dumps(params)
    
    
        
    # Creates a single node in Neo4J
    # node_label: the label of a node (e.g., Animal, Plant, Narrative)
    # node_data: a dictionary that contains key/value pairs representing 
    #           attributes of a node
    def create_node(self, node_label, node_data, merge=True):
        if not merge:
            qry = "CREATE "
        else:
            qry = "MERGE "
        qry += " (n:" + node_label + "{"
        for key in node_data.keys():
            qry += key + ": $" + key + ", "
        qry = qry.strip()[:len(qry)-2] + "})"
        
        print(qry)
        
        self.__conn.query(qry, parameters=node_data)
        
    # Creates a link (an edge) of type TAXONOMY (i.e., rel = BELONGS_TO)
    # This shoudl only be used to create hierarchical relationships
    # between nodes of type Species, Genus, Kingdom, Phylum, Family, Class  
    # source_label: label of a source node
    # source_key: name of a unique identifier field in a source node
    # source_value: value of a unique identifier field in a source node
    # target_label: label of a target node
    # target_key: name of a unique identifier field in a target node
    # target_value: value of a unique identifier field in a target node
    def create_taxonomy_link(self, source_label, source_key, source_value, target_label, target_key, target_value):
        qry = "MATCH (a:{source_label} {{{source_key}: ${source_key}}}) "
        qry += ", (b:{target_label} {{{target_key} : ${target_key}}}) "
        qry += " MERGE (a)-[r:BELONGS_TO]->(b) RETURN a, b"
        
        #print(qry)
        
        qry = qry.format(source_label = source_label, source_key = source_key, target_label = target_label, target_key = target_key)
        #print(qry)

        params = {}
        params[source_key] = source_value
        params[target_key] = target_value
        
        #print(params)
        
        self.__conn.query(qry, parameters=params)

    def create_link_by_id(self, source_label, source_id, target_label, target_id, link_name):
        qry = "MATCH (a:" + source_label + "{id: '" + source_id + "'}) "
        qry += ", (b:" + target_label + "{id: '" + target_id + "'}) "
        qry += " MERGE (a)-[r:" + link_name + "]->(b) RETURN a, b"
        
        #print(qry)
        
       
        
        
        #print(params)
        
        self.__conn.query(qry)
        return qry

    # Creates a link (an edge) of any type.  The type is specified by a paramter
    # source_label: label of a source node
    # source_key: name of a unique identifier field in a source node
    # source_value: value of a unique identifier field in a source node
    # target_label: label of a target node
    # target_key: name of a unique identifier field in a target node
    # target_value: value of a unique identifier field in a target node
    # link_name: label for the edge between the source and the target nodes
    def create_link(self, source_label, source_key, source_value, target_label, target_key, target_value, link_name):
        qry = "MATCH (a:{source_label} {{{source_key}: {source_key}}}) "
        qry += ", (b:{target_label} {{{target_key} : {target_key}}}) "
        qry += " MERGE (a)-[r:" + link_name + "]->(b) RETURN a, b"
        
        #print(qry)
        
        qry = qry.format(source_label = source_label, source_key = source_key, target_label = target_label, target_key = target_key)
        # print(qry)

        params = {}
        params[source_key] = source_value
        params[target_key] = target_value
        
        #print(params)
        
        self.__conn.query(qry, parameters=params)
        return qry + str(params)
    

    def delete_link_by_id(self, link_id):
        qry = "MATCH ()-[r]-() WHERE id(r)=$id DELETE r "
        params = {"id" : link_id}
        
        
        #print(params)
        
        self.__conn.query(qry, parameters=params)
        return qry + str(params)

    def delete_link_between_nodes(self, source_id, source_label, target_id, target_label):
        qry = "MATCH (a:" + source_label + "{id: '" + source_id + "'})"
        qry += "-[r]-"
        qry += "(b:" + target_label + "{id: '" + target_id + "'}) "
        qry += " DELETE r RETURN a, b"
        
        self.__conn.query(qry)
        return qry

    def find_taxonomy_by_common_name(self, common_name):
        url = "https://api.gbif.org/v1/species/search?q=" + common_name.replace(' ', '%20')
        response = urlopen(url)
        data_json = json.loads(response.read())
        return data_json['results']
    
    

    def create_generalized_living_object(self, label, common_name, story_id = None):
        
        object_id = str(uuid4())
        object_data = {
            "id" : object_id,
            "common_name" : common_name
        }
        
        self.create_node(label + ':Generalized', object_data)

        
        
        if story_id != None and story_id != "":
            
            self.create_link_by_id('Narrative', story_id, label, object_id, 'APPEARS_IN')
        
        return object_id
    
    
    def create_living_object_taxonomy(self, label, common_name, scientific_name, taxonomy_data, story_id = None):
        
        species_id = self.create_living_object_node(label, common_name, scientific_name, taxonomy_data['species'])
        
        if story_id != None and story_id != "":
            #create_link_by_id(self, source_label, source_id, target_label, target_id, link_name):
            self.create_link_by_id('Narrative', story_id, label, species_id, 'APPEARS_IN')
        
        # Create Genus node
        genus = {
            "genus" : taxonomy_data['genus']
        }
        
        self.create_node('Genus', genus)
        self.create_taxonomy_link(label, 'species', taxonomy_data['species'], 'Genus', 'genus', taxonomy_data['genus'])


        # Create Family Node
        family = {
            "family" : taxonomy_data['family']
        }
        self.create_node('Family', family)
        self.create_taxonomy_link('Genus', 'genus', taxonomy_data['genus'], 'Family', 'family', taxonomy_data['family'])
        
        
        
        # Create class Node
        class_ = {
            "class" : taxonomy_data['class']
        }
        self.create_node("Class", class_)
        
        self.create_taxonomy_link('Family', 'family', taxonomy_data['family'], 'Class', 'class', taxonomy_data['class'])

        
        # Create phylum Node
        phylum = {
            "phylum" : taxonomy_data['phylum']
        }
        self.create_node("Phylum", phylum)
        
        self.create_taxonomy_link('Class', 'class', taxonomy_data['class'], 'Phylum', 'phylum', taxonomy_data['phylum'])
        
        # Create phylum Node
        kingdom = {
            "kingdom" : taxonomy_data['kingdom']
        }
        self.create_node("Kingdom", kingdom)
        
        self.create_taxonomy_link('Phylum', 'phylum', taxonomy_data['phylum'], 'Kingdom', 'kingdom', taxonomy_data['kingdom'])

        return species_id
        
    def create_file_node(self, file_name, file_type, server_path, description, notes):
        file_id = str(uuid4())
        qry = "CREATE (f:File {id: $id, file_name: $file_name, file_type: $file_type, server_path: $server_path, description: $description, notes: $notes}) return f;"
        params = {
            "id" : file_id,
            "file_name": file_name,
            "file_type": file_type,
            "server_path" : server_path, 
            "description" : description,
            "notes" : notes
        }
        self.__conn.query(qry, parameters=params)
        return file_id
    
    def get_file_list(self, entity_id, entity_label):
        files = []
        qry = "MATCH (n:" + entity_label + ")<-[r:ASSOCIATED_WITH]-(f:File) WHERE n.id = $entity_id RETURN f"
        params = {"entity_id" : entity_id}
        result = self.__conn.query(qry, parameters=params)
        for record in result:
            # Add record to a JSON feed
            files.append(record.data()["f"])
        return json.dumps(files)
    
    def get_media_list(self, entity_id, entity_label):
        files = []
        qry = "MATCH (n:" + entity_label + ")<-[r:ASSOCIATED_WITH]-(m:Media) WHERE n.id = $entity_id RETURN m"
        params = {"entity_id" : entity_id}
        result = self.__conn.query(qry, parameters=params)
        for record in result:
            # Add record to a JSON feed
            files.append(record.data()["m"])
        return json.dumps(files)

    def create_external_media_node(self, source, media_type, url, description, notes):
        media_id = str(uuid4())
        qry = "CREATE (m:Media {id: $id, source: $source, media_type: $media_type, url: $url, description: $description, notes: $notes}) return m;"
        params = {
            "id" : media_id,
            "source": source,
            "media_type": media_type,
            "url" : url, 
            "description" : description,
            "notes" : notes
        }
        self.__conn.query(qry, parameters=params)
        return media_id
    
    
    def update_animal_data_node(self, animal_id, common_name, scientific_name, species):
        qry = "MATCH (a:Animal) WHERE a.id = $animal_id "
        qry += "SET a.common_name = $common_name, "
        qry += "a.scientific_name = $scientific_name, "
        qry += "a.species = $species RETURN a; "    
        
        params = {
            "animal_id" : animal_id,
            "common_name": common_name,
            "scientific_name": scientific_name,
            "species" : species
        }
        self.__conn.query(qry, parameters=params)
        return animal_id
    
    def update_plant_data_node(self, plant_id, common_name, scientific_name, species):
        qry = "MATCH (p:Plant) WHERE p.id = $plant_id "
        qry += "SET p.common_name = $common_name, "
        qry += "p.scientific_name = $scientific_name, "
        qry += "p.species = $species RETURN p; "    
        
        params = {
            "plant_id" : plant_id,
            "common_name": common_name,
            "scientific_name": scientific_name,
            "species" : species
        }
        self.__conn.query(qry, parameters=params)
        return plant_id
    
    def update_object_data_node(self, object_id, object_name, description, notes):
        qry = "MATCH (o:Object) WHERE o.id = $object_id "
        qry += "SET o.object_name = $object_name, "
        qry += "o.description = $description, "
        qry += "o.notes = $notes RETURN o; "    
        
        params = {
            "object_id" : object_id,
            "object_name": object_name,
            "description": description,
            "notes" : notes
        }
        self.__conn.query(qry, parameters=params)
        return object_id
    
    def update_concept_data_node(self, concept_id, concept_name, description, notes):
        qry = "MATCH (c:Concept) WHERE c.id = $concept_id "
        qry += "SET c.concept_id = $concept_id, "
        qry += "c.description = $description, "
        qry += "c.notes = $notes RETURN c; "    
        
        params = {
            "concept_id" : concept_id,
            "concept_name": concept_name,
            "description": description,
            "notes" : notes
        }
        self.__conn.query(qry, parameters=params)
        return concept_id
    
    def create_event(self, event_data, target_label, target_id):
        #print(event_data)
        temp = {}
        for key, val in event_data.items():
            if pd.isna(val):
                event_data[key] = ""
            temp[key] = "$" + key

        qry = "CREATE (e:Event " + str(temp).replace("'", "") + ") RETURN e;"
        
        #print(temp)
        #print(qry)

        result = self.__conn.query(qry, parameters=event_data)
        
        return temp['id']
        
    def import_events(self, filepath, filetype="csv"):
        if filetype == "csv":
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)
        
        df['id'] = [str(uuid4()) for _ in range(len(df.index))]
        taxonomy_columns = ['kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species']
        for col in taxonomy_columns:
            df[col].fillna('', inplace=True)

        for col in df.columns:
            clean_col = [s for s in col if s.isalnum() or s.isspace()]
            clean_col = "".join(clean_col)
            df.rename({col:clean_col}, axis=1, inplace=True)

        #print(df.columns)


        taxonomy_data = []
        for idx, row in df.iterrows():
            taxonomy_ids = {}
            for col in taxonomy_columns:
                attr_name = col + "_name"
                attr_value = row[col]
                if row[col] != "":
                    label = str(col[0]).upper() + str(col[1:]).lower()
                    taxonomy_node_id = self.check_taxonomy_node_exists_by_name(label, attr_name, attr_value)
                    taxonomy_ids[col] = [taxonomy_node_id, attr_name, attr_value]
                else:
                    taxonomy_ids[col] = ["", attr_name, attr_value]
            taxonomy_ids['event_id'] = row['id']
                # print(col + ": " + taxonomy_node_id)
            taxonomy_data.append(taxonomy_ids)
        #print(taxonomy_data)
        
        # Kingdom. Phylum. Class. Order. Family. Genus.
        for d in taxonomy_data:
            if d['kingdom'][0] == "":
                d['kingdom'][0] = self.create_taxonomy_node("Kingdom", d['kingdom'][1], d['kingdom'][2])
                #print(d['kingdom'][0])
            if d['phylum'][0] == "":
                d['phylum'][0] = self.create_taxonomy_node("Phylum", d['phylum'][1], d['phylum'][2])
                self.create_link_by_id("Phylum", d['phylum'][0], "Kingdom", d['kingdom'][0], "BELONGS_TO")
                #print(d['phylum'][0])
            if d['class'][0] == "":
                d['class'][0] = self.create_taxonomy_node("Class", d['class'][1], d['class'][2])
                self.create_link_by_id("Class", d['class'][0], "Phylum", d['phylum'][0], "BELONGS_TO")
                #print(d['class'][0])
            if d['order'][0] == "":
                d['order'][0] = self.create_taxonomy_node("Order", d['order'][1], d['order'][2])
                self.create_link_by_id("Order", d['order'][0], "Class", d['class'][0], "BELONGS_TO")
                #print(d['order'][0])
            if d['family'][0] == "" and d['family'][2] != "":
                d['family'][0] = self.create_taxonomy_node("Family", d['family'][1], d['family'][2])
                self.create_link_by_id("Family", d['family'][0], "Order", d['order'][0], "BELONGS_TO")
                #print(d['family'][0])
            if d['genus'][0] == "" and d['genus'][2] != "":
                d['genus'][0] = self.create_taxonomy_node("Genus", d['genus'][1], d['genus'][2])
                self.create_link_by_id("Genus", d['genus'][0], "Family", d['family'][0], "BELONGS_TO")
                #print(d['genus'][0])
            
            label = "Animal"
            d['species'][0] = self.check_species_exists_get_id(label, d['species'][2])
            if d['species'][0] == "":
                if str(d['kingdom'][2]).lower() == 'animalia':
                    label = "Animal"
                elif str(d['kingdom'][2]).lower() == 'plantae':
                    label = "Plant"
                else:
                    label = "Animal"
                if d['species'][2] != "":
                    d['species'][0] = self.create_living_object_node(label, d['species'][2], d['species'][2], d['species'][2])
                    #print("New ID: " + d['species'][0])
                    self.create_link_by_id(label, d['species'][0], "Genus", d['genus'][0], "BELONGS_TO")
        
            
            
            #print("Event ID: " + d['event_id'])
            event_data = df.query("id == '" + d['event_id'] + "'").to_dict('records')

            if d['species'][0] != "" and label != "":
                self.create_event(event_data[0], label, d['species'][0])
                self.create_link_by_id("Event", d['event_id'],  label, d['species'][0], "OBSERVED")
            else:
                if d['genus'][0] != "":
                    self.create_event(event_data[0], "Genus", d['genus'][0])
                    self.create_link_by_id("Event", d['event_id'],  "Genus", d['genus'][0], "OBSERVED")
                else:
                    if d['family'][0] != "":
                        self.create_event(event_data[0], "Family", d['family'][0])
                        self.create_link_by_id("Event", d['event_id'],  "Family", d['family'][0], "OBSERVED")
            
            
        return json.dumps(df.to_dict('records'))