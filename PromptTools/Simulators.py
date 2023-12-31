import json
import uuid
from random import randint
from .PromptRunner import ReallySimplePrompt
from .test_data import whiskey_rebellion_data


class TreeSimulation:
    max_iterations = 0
    count = 0

    def __init__(self, config, system_prompt, random_mode, test_mode):
        self.config = config
        self.random_mode = random_mode
        self.test_mode = test_mode
        
        # Init prompt runners
        system_prompt = {
            "role": "system", 
            "content": system_prompt
        }
        self.main_prompt_runner = ReallySimplePrompt(config, main_system_prompt)
    
    
    def start_simulation(self, user_prompt, max_iterations=1):
        print("Starting ", user_prompt)
        self.max_iterations = max_iterations
        
        # run_prompts will interate until max is reached
        return self.run_prompts(user_prompt, [], [])


    def run_prompts(self, user_prompt, events, network):

        print('\n ----------------- Event -----------------\n')
        print(user_prompt)
        
        user_prompt_main = self.compile_user_prompt_main(user_prompt, events)
        results_main = self.get_fake_results() if self.test_mode else self.main_prompt_runner.get_response(user_prompt_main)
        results_main_json = json.loads(results_main)
        
        if self.test_mode:
            self.max_iterations = len(results_main_json)    
            results_main_json = results_main_json[self.count]

        results_main_json["name"] = user_prompt
        
        # Get sub-events here and replace sub-events in results_main
        
        event_id = results_main_json["name"].replace(' ', '_')
        parent_id = events[len(events)-1]["id"] if len(events) else "None"
        
        event = {
            "id": event_id,
            "parent_id": parent_id,
            "name": results_main_json["name"],
            "visited": "true",
            "type": "effect",
            "content": results_main_json
        }

        # Add content to event
        events.append(event)

        # Populate network with all nodes (effects, people, etc.)
        network.append({
            "id": event_id,
            "parent_id": parent_id,
            "name": results_main_json["name"],
            "visited": "true",
            "type": "effect",
        })

        for effect in results_main_json["effects"]:
            node = {
                 "id": effect["name"].replace(' ', '_'),
                 "parent_id": event_id,
                 "name": effect["name"],
                 "visited": "false",
                 "type": "effect",
            }
            network.append(node)
        
        
        self.count += 1
        if self.count >= self.max_iterations:
            return { "events": events, "network": network}
            
        else:
            sorted_effects = sorted(event["content"]["effects"], key=lambda x: -x['score'])
            
            if self.random_mode: # If random mode
                new_user_prompt = sorted_effects[randint(0, len(sorted_effects)-1)]["name"]
            else:
                new_user_prompt = sorted_effects[0]["name"]
                
           
            return self.run_prompts(new_user_prompt, events, network)
        

    def compile_user_prompt_main(self, user_prompt, events):
        
        if len(events) > 0: # We have more that one event
            prev_conclusions = "\n\n".join([event["content"]["conclusion"] for event in events[-2:]])
            user_prompt = """
                This question is about {}. Explain it in the context of being an effect of {}. 
                Make you answer feel like a natural continuation of the the following:

                {}
            """.format(user_prompt, events[len(events)-2]["content"]["name"], prev_conclusions)

        else:
            user_prompt = "This question is about {}.".format(user_prompt)

        return {
            "role": "user",
            "content": user_prompt
        }

        
    def get_fake_results(self):
        return whiskey_rebellion_data

