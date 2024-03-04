#!/usr/bin/env python3

import os
import json
import pandas as pd
import tiktoken
import openai
import time
import uuid
import numpy as np
import pprint
#from openai.embeddings_utils import distances_from_embeddings
from .Helpers import text_file_to_json
from openai import OpenAI


class PromptRunner:
  df = None
  config = {}

  def __init__(self, config, system_prompt=None):
    global openai
    self.config = config

    # Set OpenAI API key]
    self.client = OpenAI(
      api_key=os.environ['OPENAI_API_KEY'], 
    )

    self.pretty_printer = pprint.PrettyPrinter(indent=1) 
    
    self.max_len = self.config["max_len"]
    self.size = self.config["size"]
    self.model = self.config["model"]
    self.temperature = self.config["temperature"]
    self.stop_sequence = self.config["stop_sequence"]
    self.seed = self.config["seed"] if "seed" in self.config else None
    
    if system_prompt is not None:
      self.system_prompt = system_prompt
    elif "default_system_prompt_path" in self.config:
      self.system_prompt = text_file_to_json(
        self.config["default_system_prompt_path"]
      )
    else:
      self.system_prompt = {
        "role": "system", 
        "content": "You are a helpful AI-base assistant."
      }

    #print(self.system_prompt) 

    # If custom embedding exist
    self.hasCustomEmbeddings = True if "embeddings_path" in self.config else False

    print("Custom Embeddings: ", self.hasCustomEmbeddings)
    
    if self.hasCustomEmbeddings:
      print(self.config["embeddings_path"])
      self.engine = self.config["engine"]
      self.embeddings_path = self.config["embeddings_path"]
      self.df = self.create_dataframe()

    
    temp_config = self.config
    temp_config["openai_api_key"] = "<OPEN AI KEY>"
    #self.pretty_printer.pprint(self.config) 
    
    

  def create_dataframe(self):
    print("Creating data frame")
    print("self.embeddings_path", self.embeddings_path)

    df = pd.read_csv(self.embeddings_path, index_col=0)
    df['embeddings'] = df['embeddings'].apply(eval).apply(np.array)

    return df

 
  def ask_question(
    self, 
    user_prompt=None,
    system_prompt=None,
    chat_history=None,
    config_overrides=None
  ):
    user_prompt = self.generate_user_prompt(user_prompt, False)

    if not system_prompt:
      system_prompt = self.system_prompt

    # Override temp and model
    if config_overrides:
      if config_overrides['temperature']: 
        temperature = config_overrides['temperature']
      else:
        temperature = self.temperature
      if config_overrides['model']: 
        model = config_overrides['model']
      else:
        model = self.model
    else:
      model = self.model
      temperature = self.temperature

    messages = [
      system_prompt,
      user_prompt
    ]

    if chat_history:
      # Add prompt injection (prior answers)
      messages = messages + chat_history

    print("Calling API...")

    start_time = time.time() 
    result = self.generate_answer(model, messages, temperature, self.seed)
    end_time = time.time()  
    elapsed_time = end_time - start_time
    
    print(f"API call took {elapsed_time:.2f} seconds")

    return result


  def create_context(self, question, df, max_len=1800, size="ada"):

    # THIS BREAKS WITH OPENAI v1.2

    # Get the embeddings for the question
    q_embeddings = openai.Embedding.create(input=question, engine=self.engine)['data'][0]['embedding']

    # Get the distances from the embeddings
    #self.df['distances'] = distances_from_embeddings(q_embeddings, self.df['embeddings'].values, distance_metric='cosine')
    returns = []
    cur_len = 0

    # Sort by distance and add the text to the context until the context is too long
    for i, row in df.sort_values('distances', ascending=True).iterrows():
        
      # Add the length of the text to the current length
      cur_len += row['n_tokens'] + 4
      
      # If the context is too long, break
      if cur_len > max_len:
          break
      
      # Else add it to the text that is being returned
      returns.append(row["text"])
    

    return "\n\n###\n\n".join(returns)


  def generate_user_prompt(self, user_prompt, debug=False):

    if isinstance(user_prompt, str):
      question = user_prompt # if question string is passed
    elif isinstance(user_prompt, dict):
      question = user_prompt['content']

    # Generic user prompt to be populated
    new_user_prompt = {
      "role": "user", 
      "content": None
    }

    # Create prompt with contexts and without
    if self.hasCustomEmbeddings:

      context = self.create_context(
        question,
        self.df,
        max_len=self.max_len,
        size=self.size,
      )
      new_user_prompt["content"] =  """
        context: {context} \n\n
        question: {question} \n\n
      """.format(context=context, question=question)

    else:
      new_user_prompt["content"] = question
        
      
    return new_user_prompt


  def generate_answer(
    self, 
    model="gpt-4",
    messages=[],
    temperature=0.5,
    seed=None
  ):

    #try: .
    response = self.client.chat.completions.create(
      model=model, #"gpt-3.5-turbo",
      messages=messages,
      temperature=temperature,
      seed=seed,
      response_format={"type": "json_object"}
    )

    
    #return response['choices'][0]['message']['content'].strip()
    return response.choices[0].message.content.strip()
      
    #except Exception as e:
    #  print(e)
    #  return ""


# Run SimplePrompt from command line:
# python3 -c "from PromptRunner import SimplePrompt; SimplePrompt('configs/portfolio-config.json');"


class SimplePrompt:

  def __init__(self, config_path=None):
    self.prompt_runner = None
    self.pretty_printer = pprint.PrettyPrinter(indent=1)  
    self.config_path = config_path
    self.input_str = "User prompt: "

    self.question_prompt(None)


  def load_config(self, config_path):
    # Load config as JSON
    with open(config_path) as file:
      loaded_file = file.read()
      return json.loads(loaded_file)


  def question_prompt(self, question=None):

    # Load config for each question to use any changes
    config = self.load_config(self.config_path)
    self.prompt_runner = PromptRunner(config)

    if question is not None: 
      try:
        result = self.prompt_runner.ask_question(question)

        print(result) 
        
        question = str(input(self.input_str))
        self.question_prompt(question)
      
      except Exception as e:
        print(e)
    
    question = str(input(self.input_str))
    self.question_prompt(question)


"""
ReallySimplePrompt
Takes config json
Takes system_prompt str
Takes user_prompt str
"""

class ReallySimplePrompt:
  def __init__(self, config, system_prompt=None):
    self.prompt_runner = PromptRunner(config, system_prompt)
  
  def get_response(self, user_prompt=None, system_prompt=None, chat_history=None):
    response = self.prompt_runner.ask_question(user_prompt=user_prompt, system_prompt=system_prompt, chat_history=chat_history)
    return response



# Run IterativePrompt from command line
# python3 -c "from IterativePrompt import IterativePrompt; rr = IterativePrompt('configs/recursing-config.json'); rr.get_tree('U.S. Election of 1896', 0);"


class IterativePrompt:
  def __init__(self, path_to_config):
    self.config = self.load_config(path_to_config)
    self.prompt_runner = PromptRunner(self.config)
    self.pretty_printer = pprint.PrettyPrinter(indent=1) 


  def get_tree(self, topic, max_tiers=0, closeness=8):
    tree = []
    name = topic
    self.node = {
      "id": str(uuid.uuid4()),
      "name": name,
      "summary": None,
      "children": [],
    }
    
    tree.append(self.node)

    # TO DO: Why does this return a tuple?
    user_prompt = self.generate_user_prompt(topic, parent_summary=None),

    self.run_iteration(self.node, user_prompt[0], max_tiers, 0, closeness)

    print("------------ DONE ------------")

    return tree


  def load_config(self, path_to_config):
    # Load config as JSON
    with open(path_to_config) as file:
      loaded_file = file.read()
      return json.loads(loaded_file)


  def run_iteration(
    self, 
    node=None, 
    user_prompt=None, 
    max_tiers=2, 
    tier=0, 
    closeness=8
  ):
    # Run iterations for n tiers
    #try:
    result_str = self.prompt_runner.ask_question(user_prompt)
    result = json.loads(result_str)

    node["summary"]  = str(result["summary"])
    node["dates"]    = result["dates"]
    node["people"]   = result["people"]
    node["places"]   = result["places"]
    node["events"]   = result["events"]
    node["themes"]   = result["themes"]
    node["children"] = [ 
      {"id": str(uuid.uuid4()), "name":child["name"], "score":child["score"], "themes":[]} for child in result["children"] if child["score"] >= closeness
    ]
    node["tier"]     = tier

    print("\n\nTIER: ", tier)
    #print("RESULT\n{}".format(result_str))
    self.pretty_printer.pprint(node) 

    if tier == max_tiers:
      return
    
    tier = tier + 1
    
    for i in range(0, len(node["children"])):
      if node["children"][i]["score"] >= closeness:
        child_user_prompt = self.generate_user_prompt(
          node["children"][i], parent_summary=node["summary"]
        )

        # TO DO: Why tuple?
        if type(child_user_prompt) == 'Tuple':
          child_user_prompt = child_user_prompt[0]
        
        self.run_iteration(
          node=node["children"][i], 
          user_prompt=child_user_prompt,
          max_tiers=max_tiers, 
          tier=tier,
          closeness=closeness
        )

    #except Exception as e:
    #  print(e)

    
  def generate_user_prompt(self, topic, parent_summary=None):

    if parent_summary is not None:
      user_prompt = "This question is about {}. Explain {} as the follow-up content to this excerpt: '{}' ".format(topic, topic, parent_summary)
    else:
      user_prompt = "Explain {}".format(topic)

    return user_prompt


  def get_fake_results(self, user_prompt):
    global fake_results
    return fake_results["result"] 
    

fake_results = {
  "result": {
    "id": "123",
    "title": "The French Revolution",
    "summary": "Summary here...",
    "children": [
      {
        "id": "456",
        "title": "The Rise of Napolean",
        "score": 10
      },
      {
        "id": "789",
        "title": "The Rise of Nation States",
        "score": 9
      },
    ],
    "concepts": [
      {"name": "Some concept"},
      {"name": "Another concept"},
    ]
  }
}
  






