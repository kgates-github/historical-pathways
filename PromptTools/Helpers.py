import os
import json
import pprint

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


def test():
  result_json = text_file_to_json("static/prompts/default_system_prompt.txt")
  pp = pprint.PrettyPrinter(indent=1) 
  pp.pprint(result_json)

  result_json = text_file_to_json("static/prompts/test_prompts/")
  pp = pprint.PrettyPrinter(indent=1) 
  pp.pprint(result_json)


#test()