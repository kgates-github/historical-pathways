import json
from random import randint
from math import floor
from .PromptRunner import ReallySimplePrompt
from .test_data import election_of_1800_data
from .Helpers import is_valid_date


class PromptChain:
    max_iterations = 0
    count = 0

    def __init__(self, config, system_prompt, user_prompt, link_deviation, test_mode, grade_level, theme_mode):
        self.config = config
        self.link_deviation = link_deviation
        self.test_mode = test_mode
        self.user_prompt = user_prompt
        self.grade_level = grade_level
        self.theme_mode = theme_mode
        self.chat_history = []
        
        # Init prompt runners
        system_prompt = {
            "role": "system", 
            "content": system_prompt.replace("%GRADE_LEVEL%", self.grade_level)
        }
        self.main_prompt_runner = ReallySimplePrompt(config, system_prompt)
    
    
    def build_chain(self, user_prompt, max_iterations=1):
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
            results_main = self.main_prompt_runner.get_response(user_prompt=user_prompt_main, chat_history=None)

        results_main_json = json.loads(results_main)
       
        if self.test_mode:
            self.max_iterations = len(results_main_json)    
            results_main_json = results_main_json[self.count]
        
        results_main_json["name"] = user_prompt
        event_id = results_main_json["name"].replace(' ', '_')
        parent_id = events[len(events)-1]["id"] if len(events) else "None"
        menu = results_main_json["name"] + ":" + self.link_deviation + ":" + self.grade_level
        #print(name)

        # Make sure dates are valid
        if "dates" in results_main_json:
            if not is_valid_date(results_main_json["dates"]["start"]):
                results_main_json["dates"]["start"] = "2023-01-01"
            if not is_valid_date(results_main_json["dates"]["end"]):
                results_main_json["dates"]["end"] = "2023-01-01"
        else:
            results_main_json["dates"] = {
                "start": "2023-01-01",
                "end": "2023-01-01"
            }

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
            # Get the next event
            sorted_effects = sorted(event["content"]["next"], key=lambda x: -x['score'])
            
            if self.link_deviation == "random": # If random mode
                next_event = sorted_effects[randint(0, len(sorted_effects)-1)]
                print("\n\nRandom deviation: " + next_event["name"])
            elif self.link_deviation == "high":
                next_event = sorted_effects[len(sorted_effects)-1] # Get the lowest
                print("\n\nHigh deviation: " + next_event["name"])
            elif self.link_deviation == "medium":
                index = floor(len(sorted_effects) / 2)
                next_event = sorted_effects[index] # Get something in the middle
                print("\n\nHigh deviation: " + next_event["name"])
            else:
                next_event = sorted_effects[0]
                print("\n\nLow deviation: " + next_event["name"])
            
            new_question = next_event["name"] # + ":" + next_event["description"] 
            
            return self.run_prompts(new_question, events, network)
        

    def compile_user_prompt_main(self, new_question, events):
        
        if len(events) > 0: # We have more that one event
            # Get the previous event
            prev_event = events[len(events)-1]

            # Create list of previous lectures to add to the prompt to maintain context
            prev_lectures = "Your lecture is about {} as it pertains to {}. It should be a logical continuation of the following lectures:\n\n".format(
                new_question,
                events[len(events)-1]["content"]["name"] + ": " + prev_event["content"]["description"]
            )
            c = 0

            try:
                for event in events:
                    c += 1
                    prev_lectures += """
                        {}) Lecture name: {}: {}, Dates: {} to {} {} {}\n
                    """.format(
                        str(c), 
                        event["content"]["name"], 
                        event["content"]["description"], 
                        event["content"]["dates"]["start"], 
                        event["content"]["dates"]["end"],
                        ' '.join([str(x["summary"]) for x in [y for y in event["content"]["sections"]]]),
                        event["content"]["conclusion"],
                    )
            except:
                print("Error in compile_user_prompt_main")
                print(event)

            user_prompt = self.user_prompt.replace("%QUESTION%", new_question).replace("%PREVIOUS LECTURES%", prev_lectures)

            if self.theme_mode:
                themes = prev_event["content"]["themes"]
                theme = themes[randint(0, len(themes)-1)]
                theme_prompt = "Choose follow-up lectures that are anchored around the theme of {}.".format(theme)

                print("\n\n--------------THEME--------------\n\n")
                print(theme_prompt + "\n\n")

                user_prompt = user_prompt.replace("%THEME%", theme_prompt)
            else:
                user_prompt = user_prompt.replace("%THEME%", "")
               
        else:
            # Clear any placeholders for follow up prompts
            user_prompt = self.user_prompt.replace("%QUESTION%", new_question).replace("%PREVIOUS LECTURES%", "").replace("%THEME%", "")
       

        return {
            "role": "user",
            "content": user_prompt
        }

        
    def get_fake_results(self):
        return election_of_1800_data

