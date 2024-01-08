import json
from random import randint
from math import floor
from .PromptRunner import ReallySimplePrompt
from .test_data import election_of_1800_data
from .Helpers import is_valid_date
from .Prompts import teacher_prompt_lecture


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

        print('\n ----------------- Lecture Topic -----------------\n')
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

class Simulation:
    def __init__(self, config, student_config):
        # This is the primary prompt for creating lessons
        self.teacher_prompt_lecture = teacher_prompt_lecture
        self.prompt_runner = ReallySimplePrompt(config)
        self.log = []

        # Create instance of student to handle persona logic
        self.student = Student(student_config, config)

        # Prompts for creating initial lectures based on student preferences
        self.system_prompt_teacher = {
            "role": "system", 
            "content": f"""
                You are a history teacher. You can deliver history lectures in a way that is understandable to 
                a student whose education level is {self.student.attributes["education"]}."""
        }
            
        # Generate lecture list prompt
        self.prompt_teacher_init = {
            "role": "user", 
            "content": f"""
                You are to create a list of lectures on history that you intend to deliver. 
                The list of up to 5 lectures should be about historical events that are of interest to a student who is interested in {self.student.attributes["areas_of_interest"]}.
                In addition, the lecture should be of interest to a student who is into any or all of the following themes:
                {' -'.join(self.student.attributes["themes_of_interest"])}

                You answer will include the following:
                
                1) Name: A concise name for the lecture.
                2) Dates: A JSON array with the time span of the lecture in the form of two dates. 
                3) Description: Short, roughly 30-word descrption of the lecture and it's importance. This should entice users into wanting to learn more.
                4) Themes: Main themes of the lecture.
                5) Score: A score between 1 and 10 representing how well the event matches the themes listed above.
                
                ALSO, IF YOU DO NOT RETURN PROPERLY FORMATED JSON, A BABY EWOK WILL BE EUTHENIZED!!! Here is what I want:

                "lectures": [
                    {{
                        "name": <Name of the lecture/>, 
                        "dates": {{"start": YYYY-MM-DD, "end": YYYY-MM-DD}},
                        "description": <Brief 30-word description of the lecture/>,
                        "themes": [<theme name/>, ...],
                        "score": <score/>,
                    }}
                    ...
                ]
            """
        }

    
    def run(self):
        print("\nINITIALIZING SIMULATION\n")

        # Get initial lecture list
        lectures = self.prompt_runner.get_response(user_prompt=self.prompt_teacher_init, system_prompt=self.system_prompt_teacher, chat_history=None)
        lectures_json = json.loads(lectures)
        
        # Take top ranked to start simulation
        sorted_lectures = sorted(lectures_json["lectures"], key=lambda x: -int(x['score']))
        self.iterate(sorted_lectures[-1], sorted_lectures)
        
       
    def iterate(self, cur_lecture_idea, prev_lectures):
        print("\n---------------- ITERATION ----------------\n")
        print(prev_lectures[:2])
        cur_teacher_prompt = self.teacher_prompt_lecture.replace("%LECTURE_NAME%", cur_lecture_idea["name"]).replace("%LECTURE_DESCRIPTION%", cur_lecture_idea["description"]).replace("%STUDENT_THEMES%", self.student.get_themes())

        print(self.student.get_themes())
        print(cur_teacher_prompt)

        print("\n---------------- LECTURE ----------------\n")
        print("\nGenerating Lecture\n")

        # TO DO: add prev lectures
        #try:
        #    for lecture in self.student.get_lectures():
        #        c += 1
        #        prev_lectures += """
        #            {}) Lecture name: {}: {}, Dates: {} to {} {} {}\n
        #        """.format(
        #            str(c), 
        #            lecture["content"]["name"], 
        #            lecture["content"]["description"], 
        #            lecture["content"]["dates"]["start"], 
        #            lecture["content"]["dates"]["end"],
        #            ' '.join([str(x["summary"]) for x in [y for y in lecture["content"]["sections"]]]),
        #            lecture["content"]["conclusion"],
        #        )
        #except:
        #    print("Error in compile_user_prompt_main")
        #    print(lecture)

        cur_lecture = self.prompt_runner.get_response(user_prompt=cur_teacher_prompt, system_prompt=self.system_prompt_teacher, chat_history=None)
        cur_lecture_json = json.loads(cur_lecture)
        print(json.dumps(cur_lecture_json, indent=2))

       

        # TO DO: Add parent id to lecture
        self.student.append_lecture(cur_lecture_json)

        # Studet evaluated lecture
        lecture_evaluation = self.student.evaluate_lecture(cur_lecture_json)
        

        # %PREVIOUS LECTURES% !!!
        # Take next_lecture and generate lecture
        # Log event and add lecture to student.lectures list
        # Determine satisfaction
        # - If satisfaction is above 8, increment satisfaction
        # - Take top lecture from new_lecture.next_lectures list
        # - If satisfaction is below 8, decrement satisfaction
        # - Take top lecture from cur_lecture.next_lectures list
        pass

    
    def log_event(self, event):
        self.log.append(event)
        # WRITE JSON TO FILE HERE


class Student:
    def __init__(self, student_config, config):
        self.system_prompt_student = {
            "role": "system", 
            "content": f"""
                You are a {student_config["age"]}-year-old {student_config["nationality"]} {student_config["gender"]} whose education level is {student_config["education"]}  who is interested in taking some online history classes.
            """
        }

        self.prompt_persona_init = {
            "role": "user", 
            "content": f"""
                You are interested in the following topics that might be related to the history of {student_config["areas_of_interest"]}:
                {student_config["topics_of_interest"]}

                Given your preferencees, answer the following:
                - Your name
                - Your location: First think of all 50 states, then pick one, then think of at least five cities in that state, then pick one of those cities.
                - List up to 4 or 5 broad themes associated with {student_config["areas_of_interest"]} and the topics you are interested in. Keep themes under 3 words.

                ALSO, IF YOU DO NOT RETURN PROPERLY FORMATED JSON, A BABY EWOK WILL BE EUTHENIZED!!! Here is what I want:

                {{
                    name: <a random first and last name/>,
                    location: <where you live/>,
                    themes: [
                        <name of theme/>
                        ...
                    ]
                }}
            """
        }

        #print(json.dumps(prompt_persona_init, indent=2))
        print("\nGENERATING STUDENT PERSONA\n")
        self.prompt_runner = ReallySimplePrompt(config)
        results = self.prompt_runner.get_response(user_prompt=self.prompt_persona_init, system_prompt=self.system_prompt_student, chat_history=None)
        results_json = json.loads(results)

        self.attributes = {
            "name": results_json["name"],
            "location": results_json["location"],
            "themes_of_interest": results_json["themes"],
            "lectures": [],
        }
        for key in student_config.keys():
            self.attributes[key] = student_config[key]

        print("\n\n---------------- STUDENT ATTRIBUTES ----------------\n\n")
        print(json.dumps(self.attributes, indent=2)) 
    

    def get_themes(self):
        return ', '.join(self.attributes["themes_of_interest"])
    
    def append_lecture(self, lecture):
        self.attributes["lectures"].append(lecture)

    def get_lectures(self):
        return self.attributes["lectures"]
    
    def evaluate_lecture(self, cur_lecture_json):
        print("\n---------------- EVALUATE LECTURE ----------------\n")
        lecture_summary = ""
        lecture_summary += cur_lecture_json["name"] + "\n"
        lecture_summary += cur_lecture_json["description"] + "\n"
        #            cur_lecture_json["content"]["dates"]["start"]
        #            cur_lecture_json["content"]["dates"]["end"]
        lecture_summary += ' '.join([str(x["summary"]) for x in [y for y in cur_lecture_json["sections"]]]) + "\n"
        lecture_summary += cur_lecture_json["conclusion"]
       
        print("\n---------------- LECTURE SUMMARY ----------------\n")
        print(lecture_summary)

        self.prompt_evaluate_lecture = {
            "role": "user", 
            "content": f"""
                You just listened to a lecture on {cur_lecture_json["name"]}. Here is a summary of the lecture:

                {lecture_summary} 
                
                You are to evaluate the lecture on a scale of 1 to 10, with 10 meaning that you enjoyed the lecture and learned a lot from it. You are to evaluate the lecture given that you are interested in {self.attributes["areas_of_interest"]} and the themes of {self.get_themes()}.

                ALSO, your response is to be in properly formatted JSON. IF YOU DO NOT RETURN PROPERLY FORMATED JSON, A BABY EWOK WILL BE EUTHENIZED!!! Here is what I want:
                
                {{
                    name: {cur_lecture_json["name"]}.
                    score: <your lecture score/>,
                }}
            """
        }

        print("\n---------------- LECTURE EVALUATION ----------------\n")
        evaluation = self.prompt_runner.get_response(user_prompt=self.prompt_evaluate_lecture, system_prompt=self.system_prompt_student, chat_history=None)
        evaluation_json = json.loads(evaluation)
        print(evaluation)

        return evaluation



"""

Logical flow:
-----------------------
Pick initial lesson
Generate lesson 
- Takes lecture name, description, dates
- Generates Title, Introduction, Sections, and Conclusion
Choose one of the followiung:
- Whether to futher explore current topic: compare satifaction score to interest score (SATISFACTION_PROMPT)
- If yes, generate new lecture set (FOLLOW-UP_PROMPT) and choose top scoring lecture
- If no, generate new lecture base on next best lecture (then test satisfaction, etc.)
If satisfaction is below interest score, decrement satisfaction
If satisfaction is equal or above interest score, increment satisfaction
If there are no lecures with an insterest score above 5, check previous lectures
If that fails, end simulation
If satisfaction score goes below 0, end simulation

"""