import os
import openai
import pandas as pd

class Identifier:

   def __init__(self, text):
      self.text = text
      

   def chat(self):
      #API key is stored in my system environment variables for safety
      openai.api_key = os.getenv("OPENAI_API_KEY")

      #API call from the documentaion page
      completion = openai.ChatCompletion.create(
         model="gpt-3.5-turbo",
         messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "List plants, animals, and insects, with no description, in the following: '" + self.text + "'"}
         ]

      )


      #Writes response to file so calls aren't constantly being made
      file = open("data/app/tempFile.txt", "w")
      file.write(completion.choices[0].message.content)
      file.close()

      print("OPENAI API accessed and response stored")
      print("Plants, animals, and insects stored in data/app/tempFile.txt")

   def process(self):
      
      #read from temp file with model response
      tempText = open("data/app/tempFile.txt").read()
      arr = tempText.split("\n")
   
      #Need this wird series of if-elses because the model returns
      #a space after the title sometimes and sometimes it doesn't

      plantArr = []
      plantID = []

      animalArr = []
      animalID = []

      insectArr = []
      insectID = []

      for i in range(len(arr)):
         if arr[i].startswith("Plants:"):
            pID = 1
            arr[i] = arr[i][8:]
            for n in arr[i].split(","):
               if n != "None mentioned." or not n.startswith("Don't mention"):
                  plantID.append(pID)
                  plantArr.append(n.strip())
                  pID += 1
         elif arr[i].startswith("Animals:"):
            aID = 1
            arr[i] = arr[i][9:]
            for n in arr[i].split(","):
               if n != "None mentioned." or not n.startswith("Don't mention"):
                  animalID.append(aID)
                  animalArr.append(n.strip())
                  aID += 1
         elif arr[i].startswith("Insects:"):
            iID = 1
            arr[i] = arr[i][9:]
            for n in arr[i].split(","):
               if n != "None mentioned." or not n.startswith("Don't mention"):
                  insectID.append(iID)
                  insectArr.append(n.strip())
                  iID += 1

      #Creates dictionary to be turned into Dataframe 
      plantCSV = {'id': plantID, 'name': plantArr}
      animalCSV = {'id': animalID, 'name': animalArr}
      insectCSV = {'id': insectID, 'name': insectArr}

      
      #Creates a dataframe of each category 
      #Provides some input into the terminal
      #Finally converts dataframe into CSV for each plant, animal, and insect category
      df = pd.DataFrame(plantCSV)
      df.to_csv('data/app/plants_list.csv', index=False)

      df = pd.DataFrame(animalCSV)
      df.to_csv('data/app/animal_list.csv', index=False)

      df = pd.DataFrame(insectCSV)
      df.to_csv('data/app/insect_list.csv', index=False)

      print("Processing complete and results stored")
      print("Data stored in CSVs under the following.....")
      print("data/app/plants_list.csv")
      print("data/app/animals_list.csv")
      print("data/app/insects_list.csv")



   #chat(' '.join((open('data/stories/story4.txt', encoding="utf8").readlines())))

