import os
import json
import pprint
from datetime import datetime
from pathlib import Path
from openai import OpenAI
client = OpenAI()

def text_file_to_json(directory_path):

  results = []

  if os.path.isdir(directory_path):
    file_list = os.listdir(directory_path)
    text_files = [
      os.path.join(directory_path, file) for file in file_list if file.endswith('.txt') or file.endswith('.json')
    ]
  elif os.path.isfile(directory_path):
    text_files = [directory_path]

  print(text_files)
  # Loop through the text files and strip line breaks
  for file_path in text_files:
    stack = [] # Use to store lines
    
    with open(file_path, 'r') as file:
      file_contents = file.readlines()

    for line in file_contents:
      data = line.strip()
      stack.append(data)
    
    stripped = ''.join(stack).replace('\n', ' ')
    parsed_text = json.loads(stripped)
    
    results.append(parsed_text)


  if len(results) == 1:
    return results[0]
  
  

  return results


def load_json(self, path):
  with open(path) as file:
    loaded_file = file.read()
    parsed_json = json.loads(loaded_file)

  return parsed_json


def collection_to_json_file(data, directory, file_name):
  # Create the directory if it doesn't exist
  if not os.path.exists(directory):
    os.makedirs(directory)

  # Specify the file path for the JSON file
  file_path = os.path.join(directory, file_name)

  # Write JSON data to the file
  with open(file_path, 'w') as json_file:
    json.dump(data, json_file, indent=2)

  #print(f"JSON data has been written to {file_path}")


def create_js_from_json(directory, output_directory, js_file):
  json_data_list = [] # Store data from JSON

  # Iterate over each file in the directory
  for filename in os.listdir(directory):
    if filename.endswith(".json"):
        # Construct the full file path
        file_path = os.path.join(directory, filename)

        # Read JSON data from the file
        with open(file_path, 'r') as json_file:
            try:
                # Load JSON data and append it to the list
                json_data = json.load(json_file)
                json_data_list.append(json_data)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in {filename}: {e}")
  

  if not os.path.exists(output_directory):
    os.makedirs(output_directory)

  # Specify the file path for the JSON file
  file_path = os.path.join(output_directory, js_file)

  js = f"var data = {json_data_list};"

  # Write JSON data to the file
  with open(file_path, 'w') as js_file:
    js_file.write(js)
    print(f"js written to json_file {file_path}")
  
  
  #collection_to_json_file(json_data_list, output_directory, js_file)


def is_valid_date(date_str, format='%Y-%m-%d'):
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False


def generate_audio(input, file_path):
    voice = "echo"

    print("Generating audio...")
    
    speech_file_path = Path(file_path)

    response = client.audio.speech.create(
      model="tts-1",
      voice=voice,
      input=input
    )
    
    response.stream_to_file(speech_file_path)
    
    print("Audio created")



def test():
  result_json = text_file_to_json("static/prompts/default_system_prompt.txt")
  pp = pprint.PrettyPrinter(indent=1) 
  pp.pprint(result_json)

  result_json = text_file_to_json("static/prompts/test_prompts/")
  pp = pprint.PrettyPrinter(indent=1) 
  pp.pprint(result_json)


#test()