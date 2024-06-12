from flask import Flask, render_template, request, url_for, redirect, send_from_directory, session
import os, json
import neo4jutils as n4
import narrativeutils as nu
import userutils as uu
import searchutils as su
import restapi as api
from fileinput import filename 
#import  git 
#import openai


#import openai

app = Flask(__name__)
app.secret_key = "GRAPH_FLASK_APP"
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
# FILE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'story_worlds_files'))
FILE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "static", "uploads"))
GRAPH_ENV = "neo4j_prod"
config_url = os.path.join(SITE_ROOT, "config.json")
config = json.load(open(config_url))
#json_url = os.path.join(SITE_ROOT, "data", "story1.json")
#data = json.load(open(json_url))

def check_user_status():
   if 'current_user' in session.keys():
      if len(session['current_user']) > 5:
         # Session has some valid user info
         return True
      else:
         return False
   else:
      return False

@app.route('/get_loggedin_user_info')
def get_loggedin_user_info():
   if 'current_user' in session.keys():
      if len(session['current_user']) > 5:
         # Session has some valid user info
        return json.dumps(session['current_user'])
      else:
         return json.dumps({})
   else:
      return json.dumps({})

@app.route('/')
def index():
    
    return render_template("index.html")

@app.route('/team')
def team():
    
    return render_template("team.html")

@app.route('/search')
def search():
    
    return render_template("search.html")

@app.route('/tools')
def tools():
    
    return render_template("tools.html")

@app.route('/create')
def create():
    if check_user_status():
      return render_template("create.html")
    else:
      return render_template("login.html")

@app.route('/admin')
def admin():
    if check_user_status():
      return render_template("admin.html")
    else:
      return render_template("login.html")

@app.route('/logout')
def logout():
   #session['current_user'] = {}
   if 'current_user' in session.keys():
      session.pop('current_user')
   return redirect('/')


@app.route("/download")
def download():
   #https://flask.palletsprojects.com/en/3.0.x/api/
   filename = request.args.get('filename')
   file_id = request.args.get('file_id')
   if filename != "" and filename != None and file_id != "" and file_id != None:
      subfolder = os.path.join(FILE_ROOT, file_id)
      return send_from_directory(subfolder, filename)
   else:
      return "File not found!"

@app.route("/get_download_path")
def get_download_path():
   #https://flask.palletsprojects.com/en/3.0.x/api/
   filename = request.args.get('filename')
   #source = os.path.join(FILE_ROOT, "files")
   #return uploads + "/" + filename
   return FILE_ROOT + "/" + filename

@app.route('/viewer3d')
def viewer3d():
    return render_template("viewer3d.html")

@app.route('/upload_file', methods = ['POST'])   
def upload_file():   
    #repo = git.Repo(FILE_ROOT)
    if request.method == 'POST':   
        f = request.files['file'] 
        entity_id = request.form['entity_id']
        entity_label = request.form['entity_label']
        file_type = request.form['file_type']
        description = request.form['description']
        notes = request.form['notes']

        #return f.filename
        
        #repo.git.add('.')
        #repo.git.commit('-m', description)
        
        conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
        n = nu.Narrative(conn)
        
        file_id = n.create_file_node(f.filename, file_type, FILE_ROOT, description, notes)
        if(entity_id != "" and file_id != "" and entity_id != None and file_id != None):
           subfolder = os.path.join(FILE_ROOT, file_id)
           if not os.path.exists(subfolder):
              os.makedirs(subfolder)
           f.save(os.path.join(subfolder, f.filename))
           n.create_link_by_id("File", file_id, entity_label, entity_id, "ASSOCIATED_WITH")
        
        return "SUCCESS: Uploaded and linked file and narrative:<br />"+ entity_label + " ID: " + entity_id + "<br />File ID: " + file_id  
    return "FAIL!"

@app.route('/upload_events_file', methods = ['POST'])   
def upload_events_file():   
   if request.method == 'POST':   
      f = request.files['file'] 
        
      if '.csv' in str(f.filename).lower() or '.xls' in str(f.filename).lower():
         conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
         n = nu.Narrative(conn)
            
         file_id = n.create_file_node(f.filename, "event_upload", FILE_ROOT, "", "")
         if file_id != "" and file_id != None:
            subfolder = os.path.join(FILE_ROOT, file_id)
            if not os.path.exists(subfolder):
               os.makedirs(subfolder)
            f.save(os.path.join(subfolder, f.filename))
         
            data = n.import_events(os.path.join(subfolder, f.filename), filetype="excel")
            return data #"SUCCESS: Uploaded and processed events file (File ID: " + file_id + ")" 
      else:
         return "Invalid extension - unable to upload file."
   return "FAIL!"

@app.route('/file_uploader')
def file_uploader():
   return render_template('file_uploader.html')

@app.route('/media_linker')
def media_linker():
   return render_template('media_linker.html')

@app.route('/link_media', methods = ['POST'])   
def link_media():   
   entity_id = request.form['entity_id']
   entity_label = request.form['entity_label']
   source = request.form['source']
   media_type = request.form['media_type']
   url = request.form['url']
   description = request.form['description']
   notes = request.form['notes']

   # return story_id
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   n = nu.Narrative(conn)
        
   media_id = n.create_external_media_node(source, media_type, url, description, notes)
   # return media_id   
   if(entity_id != "" and media_id != "" and entity_id != None and media_id != None):
      n.create_link_by_id("Media", media_id, entity_label, entity_id, "ASSOCIATED_WITH")
      return "SUCCESS: Created and linked media node and narrative:<br />" + entity_label + " ID: " + entity_id + "<br />Media ID: " + media_id  
   return "FAIL!"
   

@app.route('/graph')
def graph():
   #check_user_status()
   return render_template('graph.html')

@app.route('/graph1')
def graph1():
   #check_user_status()
   return render_template('graph1.html')

@app.route('/sankey')
def sankey():
   #check_user_status()
   return render_template('sankey.html')

@app.route('/relationships')
def relationships():
   #check_user_status()
   return render_template('relationships.html')

@app.route('/browse')
def browse():
   #check_user_status()
   return render_template('browse.html')
   
@app.route('/search_events')
def search_events():
   #check_user_status()
   return render_template('search_events.html')

@app.route('/graph_viewer')
def graph_viewer():
   #check_user_status()
   return render_template('graph_viewer.html')

@app.route('/get_data')
def get_data():
    global data    
    return json.dumps(data)

@app.route('/get_full_graph')
def get_full_graph():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   s = su.Search(conn)
   return s.get_full_graph()

@app.route('/get_file_list')
def get_file_list():
   entity_id = request.args.get('entity_id')
   entity_label = request.args.get('entity_label')
   if entity_id != "" and entity_label != "":
      conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
      n = nu.Narrative(conn)
      return n.get_file_list(entity_id, entity_label)

@app.route('/get_media_list')
def get_media_list():
   entity_id = request.args.get('entity_id')
   entity_label = request.args.get('entity_label')
   if entity_id != "" and entity_label != "":
      conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
      n = nu.Narrative(conn)
      return n.get_media_list(entity_id, entity_label)

@app.route('/event_search')
def event_search():
   searchterms = request.args.get('searchterms')
   #browse_target = request.args.get('browse_target')
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   s = su.Search(conn)
   return s.event_search(searchterms)

@app.route('/view_event')
def view_event():
   event_id = request.args.get('event_id')
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   s = su.Search(conn)
   return s.view_event(event_id)

@app.route('/event_details')
def event_details():
   return render_template('event_details.html')

@app.route('/search_plants')
def search_plants():
   searchterms = request.args.get('searchterms')
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   s = su.Search(conn)
   return s.search_plants(searchterms)

@app.route('/browse_entities')
def browse_entities():
   browse_target = request.args.get('browse_target')
   starts_with = request.args.get('starts_with')
   entity_id = request.args.get('entity_id')
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   s = su.Search(conn)
   if entity_id != "" and entity_id != None:
      return s.browse_entities(browse_target, startletter="", entity_id=entity_id)
   else:
      return s.browse_entities(browse_target, startletter=starts_with)
   

@app.route('/view_entity')
def view_entity():
   return render_template('view_entity.html')

@app.route('/relationships_search')
def relationship_search():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   s = su.Search(conn)
   search_target = request.args.get('search_target')
   keywords = request.args.get('keywords')
   graph = s.pairwise_search(search_target, keywords)
   
   
   return graph; 

@app.route('/search_entities')
def search_entities():
   searchtarget = request.args.get('target')
   searchscope = request.args.get('scope') 
   searchterms = request.args.get('searchterms')
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   s = su.Search(conn)
   return s.search_entities(searchtarget, searchscope, searchterms)

@app.route('/animal_search')
def animal_search():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   s = su.Search(conn)
   return s.get_full_graph()

@app.route('/add_story')
def add_story():
   return render_template('add_story.html')

@app.route('/list_animals')
def list_animals():
   return render_template('list_animals.html')

@app.route('/list_plants')
def list_plants():
   return render_template('list_plants.html')

@app.route('/import_events')
def import_events():
   return render_template('import_events.html')

@app.route('/list_narratives')
def list_narratives():
   return render_template('list_narratives.html')


@app.route('/link_concepts', methods=['GET'])
def link_concepts():
   return render_template('link_concepts.html')

@app.route('/country_linker', methods=['GET'])
def country_linker():
   return render_template('country_linker.html')

@app.route('/animal_linker', methods=['GET'])
def animal_linker():
   return render_template('animal_linker.html')

@app.route('/plant_linker', methods=['GET'])
def plant_linker():
   return render_template('plant_linker.html')


@app.route('/object_linker', methods=['GET'])
def object_linker():
   return render_template('object_linker.html')

@app.route('/create_link', methods=['GET'])
def create_link():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   n = nu.Narrative(conn)
   source_label = request.args.get('source_label')
   source_id = request.args.get('source_id')
   target_label = request.args.get('target_label')
   target_id = request.args.get('target_id')
   link_name = request.args.get('link_name')
   return_url = request.args.get('return_url')
   qry = n.create_link_by_id(source_label, source_id, target_label, target_id, link_name)

   if return_url != "" and return_url != None:
      return redirect(return_url)
   else:
      return ""
   #return qry

@app.route('/delete_link', methods=['GET'])
def delete_link():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   n = nu.Narrative(conn)
   source_label = request.args.get('source_label')
   source_id = request.args.get('source_id')
   target_label = request.args.get('target_label')
   target_id = request.args.get('target_id')
   qry = n.delete_link_between_nodes(source_id, source_label, target_id, target_label)
   return qry

@app.route('/manage_concept_links', methods=['GET'])
def manage_concept_links():
   return render_template('manage_concept_links.html')

@app.route('/create_plant_entry', methods=['GET'])
def create_plant_entry():
   return render_template('create_plant_entry.html')

@app.route('/create_animal_entry', methods=['GET'])
def create_animal_entry():
   return render_template('create_animal_entry.html')

@app.route('/update_animal_entry', methods=['GET'])
def update_animal_entry():
   return render_template('update_animal_entry.html')

@app.route('/update_plant_entry', methods=['GET'])
def update_plant_entry():
   return render_template('update_plant_entry.html')

@app.route('/update_animal_data_node', methods=['POST'])
def update_animal_data_node():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   n = nu.Narrative(conn)
   
   animal_id = request.form['animal_id']
   common_name = request.form['txt_common_name']
   scientific_name = request.form['txt_scientific_name']
   species = request.form['txt_species']
   
   animal_id = n.update_animal_data_node(animal_id, common_name, scientific_name, species)
   #return animal_id
   return redirect("update_animal_entry?animal_id="+animal_id)

@app.route('/update_plant_data_node', methods=['POST'])
def update_plant_data_node():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   n = nu.Narrative(conn)
   
   plant_id = request.form['plant_id']
   common_name = request.form['txt_common_name']
   scientific_name = request.form['txt_scientific_name']
   species = request.form['txt_species']
   
   plant_id = n.update_plant_data_node(plant_id, common_name, scientific_name, species)
   return redirect("update_plant_entry?plant_id="+plant_id)

@app.route('/update_object_data_node', methods=['POST'])
def update_object_data_node():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   n = nu.Narrative(conn)
   
   object_id = request.form['object_id']
   description = request.form['txt_description']
   object_name = request.form['txt_object_name']
   notes = request.form['txt_notes']
   
   object_id = n.update_object_data_node(object_id, object_name, description, notes)
   return redirect("update_object_entry?object_id="+object_id)

@app.route('/update_concept_data_node', methods=['POST'])
def update_concept_data_node():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   n = nu.Narrative(conn)
   
   concept_id = request.form['concept_id']
   description = request.form['txt_description']
   concept_name = request.form['txt_concept_name']
   notes = request.form['txt_notes']
   
   concept_id = n.update_concept_data_node(concept_id, concept_name, description, notes)
   return redirect("update_concept_entry?concept_id="+concept_id)



@app.route('/get_animal_taxonomy_node', methods=['GET'])
def get_animal_taxonomy_node():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   s = su.Search(conn)
   animal_id = request.args.get('animal_id')
   if animal_id != "" and animal_id != None:
      data = s.get_animal_taxonomy_node(animal_id)
   else:
      data = json.dumps([])
   return data

@app.route('/get_plant_taxonomy_node', methods=['GET'])
def get_plant_taxonomy_node():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   s = su.Search(conn)
   plant_id = request.args.get('plant_id')
   if plant_id != "" and plant_id != None:
      data = s.get_plant_taxonomy_node(plant_id)
   else:
      data = json.dumps([])
   return data

@app.route('/get_countries', methods=['GET'])
def get_countries():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   s = su.Search(conn)
   entity_id = request.args.get('entity_id')
   entity_label = request.args.get('entity_label')
   searchterm = request.args.get('searchterm')
   #print(searchterm)
   if entity_id != "" and entity_id != None:
      data = s.get_countries(entity_id=entity_id, entity_label=entity_label, searchterm="")
   elif searchterm != "" and searchterm != None:
      data = s.get_countries(entity_id="", entity_label="", searchterm=searchterm)
   else:
      data = s.get_countries()
   return data

@app.route('/get_languages')
def get_languages():
   check_user_status()
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   s = su.Search(conn)
   return s.get_languages()

@app.route('/get_narratives', methods=['GET'])
def get_narratives():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   s = su.Search(conn)
   entity_id = request.args.get('entity_id')
   entity_label = request.args.get('entity_label')
   searchterm = request.args.get('searchterm')

   if entity_id != "" and entity_id != None:
      data = s.get_narratives(entity_id=entity_id, entity_label=entity_label)
   elif searchterm != "" and searchterm != None:
      data = s.get_narratives(entity_id="", entity_label="", searchterm=searchterm)
   else:
      data = s.get_narratives()
   return data

@app.route('/get_animals', methods=['GET'])
def get_animals():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   s = su.Search(conn)
   entity_id = request.args.get('entity_id')
   entity_label = request.args.get('entity_label')
   animal_name = request.args.get('searchterm')
   if entity_id != "" and entity_id != None:
      data = s.get_animals(animal_name="", entity_id=entity_id, entity_label=entity_label)
   elif animal_name != "" and animal_name != None:
      data = s.get_animals(animal_name=animal_name, entity_id="", entity_label="")
   else:
      data = s.get_animals()
   return data


@app.route('/get_plants', methods=['GET'])
def get_plants():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   s = su.Search(conn)
   entity_id = request.args.get('entity_id')
   entity_label = request.args.get('entity_label')
   plant_name = request.args.get('searchterm')
   if entity_id != "" and entity_id != None:
      data = s.get_plants(plant_name="", entity_id=entity_id, entity_label=entity_label)
   elif plant_name != "" and plant_name!= None:
      data = s.get_plants(plant_name=plant_name, entity_id="", entity_label="")
   else:
      data = s.get_plants()
   return data

@app.route('/get_concepts_data', methods=['GET'])
def get_concepts_data():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   n = nu.Narrative(conn)
   story_id = request.args.get('story_id')
   data = {
      "story_id" : story_id,
      "story_text" : "",
      "matched_animals" : [],
      "matched_plants" : []
   }
   if story_id != "":
      narr = n.get_narrative(story_id)
      text = narr['text']
      data["story_text"] = text
      #data["matched_animals"] = n.get_entity_list(text, config["open_ai"]["api_key"]) 
      data["matched_animals"] = n.get_matched_data_list('data/animals.csv', text, story_id)
      print(data["matched_animals"])
      #data["matched_plants"] = n.get_entity_list(text, config["open_ai"]["api_key"], entity_type="plants") 
   return json.dumps(data)

@app.route('/search_bio_data', methods=['GET'])
def search_bio_data():
   searchterm = request.args.get('searchterm')
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   s = su.Search(conn)
   data = s.search_bio_data(searchterm)

   return data


@app.route('/savenarrative', methods=['POST'])
def savenarrative():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   n = nu.Narrative(conn)

   text = request.form['story_text'] #open('data/stories/story2.txt').read()
   title = request.form['story_title']
   author = request.form['author']
   translator = request.form['translator']
   presenter = request.form['presenter']
   date_recorded = request.form['date_recorded']
   orig_language = request.form['orig_language']
   trans_language = request.form['trans_language']
   country = request.form['country']

   story_id = n.add_narrative(title, text, author, translator, presenter, date_recorded, orig_language, trans_language, country, notes='')
   return redirect("link_concepts?story_id=" + story_id)
   
   # matched_animal_list = n.get_entity_list(text, config["open_ai"]["api_key"]) #get_animal_list(text) #n.get_data_list('data/animals.csv', text)
   # print(matched_animal_list)
   
   
   '''
   for animal in matched_animal_list:
      taxonomy_data = n.find_taxonomy_by_common_name(animal)
      if taxonomy_data != None:
         if 'species' in taxonomy_data[0].keys() and 'genus' in taxonomy_data[0].keys() and 'kingdom' in taxonomy_data[0].keys():
               n.create_link_animal_taxonomy(animal, taxonomy_data, story_id = story_id)
   '''
   # return text

@app.route('/create_living_object_taxonomy', methods=['POST'])
def create_living_object_taxonomy():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   n = nu.Narrative(conn)

   entity_id = request.form['entity_id'] #Narrative ID;
   entity_label = request.form['entity_label']
   common_name = request.form['txt_common_name']
   is_generalized = request.form['ddl_generalized']
   if is_generalized == "no":
      data = {
         "kingdom": request.form['txt_kingdom'],
         "phylum" : request.form['txt_phylum'],
         "class" : request.form['txt_class'],
         "order" : request.form['txt_order'],
         "family" : request.form['txt_family'],
         "genus" : request.form['txt_genus'],
         "species" : request.form['txt_species']
      }
      n.create_living_object_taxonomy(entity_label, common_name, data['species'], data, entity_id)
   else:
      n.create_generalized_living_object(entity_label, common_name)
   
   if entity_label == "Animal":
      return redirect("list_animals")
   else:
      return redirect("list_plants")
   

@app.route('/create_generalized_living_object')
def create_generalized_living_object():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   n = nu.Narrative(conn)

   entity_label = request.args.get('entity_label')
   common_name = request.args.get('common_name')
   narrative_id = request.args.get('narrative_id')

   #return entity_label + ", " + common_name + ", " + narrative_id
   
   
   object_id = n.create_generalized_living_object(entity_label, common_name, narrative_id)
   
   return redirect("link_concepts?story_id=" + narrative_id)
   
   
   
@app.route('/get_users')
def get_users():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   u = uu.User(conn)
   user_id = request.args.get('user_id')
   last_name = request.args.get('last_name')
   user_list = u.get_users(user_id, last_name)
   return u.users_pivot_table_with_roles(json.loads(user_list))

@app.route('/manage_users')
def manage_users():
   return render_template('manage_users.html')

@app.route('/update_user')
def update_user():
   return render_template('update_user.html')

@app.route('/create_user')
def create_user():
   return render_template('create_user.html')

@app.route('/login')
def login():
   return render_template('login.html')

@app.route('/validate_login', methods=['POST'])
def validate_login():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   u = uu.User(conn)
   email = request.form['txt_email']
   password = request.form['txt_password']
   current_user = {}
   if email != "" and password != "":
      user_data = u.validate_login(email, password)
      if len(user_data) > 0:
         current_user['user_info'] = user_data[0]['u']
         current_user['roles'] = []
         for item in user_data:
            current_user['roles'].append(item['r'])
         session['current_user'] = json.dumps(current_user, default=str)
         return redirect("graph")
   
   return redirect("login")
       

@app.route('/update_user_data', methods=['POST'])
def update_user_data():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   u = uu.User(conn)
   user_id = request.form['user_id']
   last_name = request.form['txt_last_name']
   first_name = request.form['txt_first_name']
   affiliation = request.form['txt_affiliation']
   email = request.form['txt_email']

   # Password
   password = request.form['txt_password']
   repeat_password = request.form['txt_repeat_password']


   # Roles
   roles = {
      "admin" : 0,
      "owner" : 0,
      "editor" : 0,
      "contributor" : 0,
      "viewer" : 0
   }

   if "chk_role_admin" in request.form:
      roles["admin"] = 1
   if "chk_role_owner" in request.form:
      roles["owner"] = 1
   if "chk_role_editor" in request.form:
      roles["editor"] = 1
   if "chk_role_contributor" in request.form:
      roles["contributor"] = 1
   if "chk_role_viewer" in request.form:
      roles["viewer"] = 1
   

   if password != "" and repeat_password != "" and password == repeat_password:
      u.update_user_data(user_id, first_name, last_name, email, affiliation, roles, password=password)               
      
   else:
      u.update_user_data(user_id, first_name, last_name, email, affiliation, roles)     
             
   return redirect('update_user?user_id='+user_id)


@app.route('/create_new_user', methods=['POST'])
def create_new_user():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   u = uu.User(conn)
   last_name = request.form['txt_last_name']
   first_name = request.form['txt_first_name']
   affiliation = request.form['txt_affiliation']
   email = request.form['txt_email']

   # Password
   password = request.form['txt_password']
   repeat_password = request.form['txt_repeat_password']


   # Roles
   roles = {
      "admin" : 0,
      "owner" : 0,
      "editor" : 0,
      "contributor" : 0,
      "viewer" : 0
   }

   if "chk_role_admin" in request.form:
      roles["admin"] = 1
   if "chk_role_owner" in request.form:
      roles["owner"] = 1
   if "chk_role_editor" in request.form:
      roles["editor"] = 1
   if "chk_role_contributor" in request.form:
      roles["contributor"] = 1
   if "chk_role_viewer" in request.form:
      roles["viewer"] = 1
   


   data = u.create_new_user(first_name, last_name, email, affiliation, roles, password)
      
             
   return redirect('manage_users')
   
@app.route('/create_object', methods=['POST'])
def create_object():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   n = nu.Narrative(conn)

   object_name = request.form['txt_object_name']
   description = request.form['txt_description']
   notes = request.form['txt_notes']
   n.create_object_node(object_name, description, notes)
   return redirect("create")

@app.route('/create_concept', methods=['POST'])
def create_concept():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   n = nu.Narrative(conn)

   concept_name = request.form['txt_concept_name']
   description = request.form['txt_description']
   notes = request.form['txt_notes']
   n.create_concept_node(concept_name, description, notes)
   return redirect("create")


@app.route('/create_object_entry', methods=["GET"])
def create_object_entry():
   return render_template('create_object_entry.html')

@app.route('/create_concept_entry', methods=["GET"])
def create_concept_entry():
   return render_template('create_concept_entry.html')

@app.route('/update_object_entry', methods=["GET"])
def update_object_entry():
   return render_template('update_object_entry.html')

@app.route('/update_concept_entry', methods=["GET"])
def update_concept_entry():
   return render_template('update_concept_entry.html')

@app.route('/get_objects', methods=["GET"])
def get_objects():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   s = su.Search(conn)
   searchterm = request.args.get('searchterm')
   entity_id = request.args.get('entity_id')
   entity_label = request.args.get('entity_label')
   
   data = []
   if searchterm != "" and searchterm != None:
      data = s.get_objects(searchterm = searchterm)
   elif entity_id != "" and entity_id != None and (entity_label == "" or entity_label == None):
      data = s.get_objects(searchterm = "", entity_id=entity_id)
   elif entity_id != "" and entity_id != None and entity_label != "" and entity_label != None:
      data = s.get_objects(searchterm = "", entity_id=entity_id, entity_label=entity_label)
   else:
      data = s.get_objects()
   
   return data

@app.route('/get_concepts', methods=["GET"])
def get_objget_conceptsects():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   s = su.Search(conn)
   searchterm = request.args.get('searchterm')
   entity_id = request.args.get('entity_id')
   entity_label = request.args.get('entity_label')
   
   data = []
   if searchterm != "" and searchterm != None:
      data = s.get_concepts(searchterm = searchterm)
   elif entity_id != "" and entity_id != None and (entity_label == "" or entity_label == None):
      data = s.get_concepts(searchterm = "", entity_id=entity_id)
   elif entity_id != "" and entity_id != None and entity_label != "" and entity_label != None:
      data = s.get_concepts(searchterm = "", entity_id=entity_id, entity_label=entity_label)
   else:
      data = s.get_concepts()
   
   return data


@app.route('/list_objects')
def list_objects():
   return render_template('list_objects.html')

@app.route('/list_concepts')
def list_concepts():
   return render_template('list_concepts.html')

@app.route('/mediaviewer')
def mediaviewer():
   return render_template('mediaviewer.html')


### RESTful API Calls
@app.route('/api/get_narrative', methods=["GET"])
def get_narrative():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   rest = api.RestApi(conn)

   narrative_id = request.args.get('narrative_id')
   data = rest.get_narrative(narrative_id)
   
   
   return data

@app.route('/api/get_object', methods=["GET"])
def get_object():
   conn = n4.Neo4jConnection(uri=config[GRAPH_ENV]["uri"], user=config[GRAPH_ENV]["user"], pwd=config[GRAPH_ENV]["passwd"])
   rest = api.RestApi(conn)

   object_id = request.args.get('object_id')
   data = rest.get_object(object_id)
   
   return data

#### ========= HELPER METHODS ========= ####


# LOG FILE, used for finetuning GPT in the future
def log_natural_lang_search(user_input, output_query):
   with open("naturallangsearch_log.txt", "a") as f:
      f.write("===============\n")
      f.write(f"User Input: {user_input}\n")
      f.write(f"Generated Query: {output_query}\n")
      f.write("\n===============\n\n")
   print("Logged to file")


if __name__ == '__main__':
   app.run(debug=True, port=5000)