import json
from random import randint
from .PromptRunner import ReallySimplePrompt
from .test_data import election_of_1800_data


class TreeChain:
    max_iterations = 0
    count = 0

    def __init__(self, config, system_prompt, user_prompt, link_deviation, test_mode, grade_level):
        self.config = config
        self.link_deviation = link_deviation
        self.test_mode = test_mode
        self.user_prompt = user_prompt
        self.grade_level = grade_level
        self.chat_history = []
        
        # Init prompt runners
        system_prompt = {
            "role": "system", 
            "content": system_prompt.replace("%GRADE_LEVEL%", self.grade_level)
        }
        self.main_prompt_runner = ReallySimplePrompt(config, system_prompt)
    
    
    def start_simulation(self, user_prompt, max_iterations=1):
        print("Starting ", user_prompt)
        self.max_iterations = max_iterations
        
        # run_prompts will interate until max is reached
        return self.run_prompts(user_prompt, [], [])


    def run_prompts(self, user_prompt, events, network):

        print('\n ----------------- Event -----------------\n')
        print(user_prompt)
        
        user_prompt_main = self.compile_user_prompt_main(user_prompt, events)

        if self.test_mode:
            results_main = self.get_fake_results() 
        else:
            results_main = self.main_prompt_runner.get_response(user_prompt=user_prompt_main, chat_history=self.chat_history)

        results_main_json = json.loads(results_main)
       
        if self.test_mode:
            self.max_iterations = len(results_main_json)    
            results_main_json = results_main_json[self.count]

        self.chat_history += [
          {"role": "user", "content": user_prompt},
          {"role": "assistant", "content": results_main_json["introduction"]}
        ]

        print("++++++++++++++++++++++++++++++++++++++++\n")
        print(self.chat_history)
        

        results_main_json["name"] = user_prompt
        event_id = results_main_json["name"].replace(' ', '_')
        parent_id = events[len(events)-1]["id"] if len(events) else "None"
        menu = results_main_json["name"] + ":" + self.link_deviation + ":" + self.grade_level
        #print(name)

        event = {
            "id": event_id,
            "parent_id": parent_id,
            "name": results_main_json["name"],
            "menu": menu,
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
            "type": "event",
        })

        for next in results_main_json["next"]:
            node = {
                 "id": next["name"].replace(' ', '_'),
                 "parent_id": event_id,
                 "name": next["name"],
                 "visited": "false",
                 "type": next["type"],
            }
            network.append(node)
        
        self.count += 1
        if self.count >= self.max_iterations:
            return { "events": events, "network": network}
            
        else:
            sorted_effects = sorted(event["content"]["next"], key=lambda x: -x['score'])
            
            if self.link_deviation == "random": # If random mode
                new_question = sorted_effects[randint(0, len(sorted_effects)-1)]["name"]
                print("\n\nRandom deviation: " + new_question)
            elif self.link_deviation == "high":
                new_question = sorted_effects[len(sorted_effects)-1]["name"] # Get the lowest
                print("\n\nHigh deviation: " + new_question)
            else:
                new_question = sorted_effects[0]["name"]
                print("\n\nLow deviation: " + new_question)
                
            return self.run_prompts(new_question, events, network)
        

    def compile_user_prompt_main(self, new_question, events):
        
        if len(events) > 0: # We have more that one event
            prev_conclusions = "\n\n".join([event["content"]["conclusion"] for event in events[-2:]])
            user_prompt = self.user_prompt.replace("%QUESTION%", new_question)
            
            """
                This question is about {}. Explain it in the context of being an effect of {}. 
                Make you answer feel like a natural continuation of the the following:

                {}
            """.format(user_prompt, events[len(events)-2]["content"]["name"], prev_conclusions)

        else:
            user_prompt = self.user_prompt.replace("%QUESTION%", new_question)

        return {
            "role": "user",
            "content": user_prompt
        }

        
    def get_fake_results(self):
        return election_of_1800_data

