import spacy
import openai

# Train new spacy model?
nlp = spacy.load("en_core_web_sm")

def generate_cypher_query(user_str):
    doc = nlp(user_str)

    entities = []
    relation = None
    # TODO:
    # Replace first verb (find operation) before NLP-ing
    # For example, if query = "retreive all ____", this doesnt work because retreive all gets mistaken for a relationship

    saved = ""
    relation = ""
    for token in doc:
        if token.pos_ == "NOUN" or token.pos_ == "PROPN":
            entities.append(token.text)
        elif token.pos_ == "VERB":
            # if token is not end of sentence, check next one
            if not (doc[len(doc)-1] == token):
                saved = token.text
                continue
        elif token.pos_ == "ADP":
            saved += " " + token.text
        relation = saved

    if relation:
        relation = relation.upper().replace(" ", "_")

    if len(entities) >= 3 and relation:
        return f"MATCH ({entities[1][0]}:{entities[1][:-1].capitalize()})-[:{relation}]->({entities[2]}) RETURN {entities[1][0]},{entities[2]}", entities, relation


    else:
        # err
        # TODO fix
        return ["err", entities, relation]
    
# TEST STUFF  
# user_input = "retrieve animals found in Ecuador"
# # doc = nlp(user_input)
# cypher_query = generate_cypher_query(user_str=user_input)
# print(cypher_query[0])
    
def failsafe_natural_search(user_input):
    import openai
    import json
    config = json.load(open("config.json"))
    openai.api_key = config["open_ai"]["api_key"]
    GPT_direction = """
    Given that the following are listed as nodes in the db:
    Amphibian
    Animal
    Bird
    Class
    Country
    Family
    File
    Fish
    Genus
    Kingdom
    Mammal
    Media
    Mollusc
    Narrative
    Nematode
    Order
    Phylum
    Plant
    Reptile
    Video


    and the following are listed as Relationships in the db:

    APPEARS_IN
    ASSOCIATED_WITH
    BELONGS_TO
    FOUND_IN
    REPRESENTS
    TAKES_PLACE_IN

    Output only the Cypher Query from the user's query. If asked to return a node, ensure the Cypher statement returns the entirety of the node
    """
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[
            {"role": "system", "content": "First, read this directive on the database schema" + GPT_direction},
            {"role": "user", "content": f"What is the Cypher Query for the user's query: {user_input}"}
        ]
    )

    query = completion.choices[0].message.content
    query = query.replace('\n', ' ')
    return query

def driver(user_input):
    cypher_query = generate_cypher_query(user_str=user_input)
    if cypher_query[0] == "err":
        return failsafe_natural_search(user_input)
    else:
        return cypher_query[0] + " LIMIT 100"
    
