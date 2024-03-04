import json
import uuid
from random import randint
from .PromptRunner import ReallySimplePrompt
from math import floor
from .test_data import election_of_1800_data
from .Helpers import is_valid_date, collection_to_json_file, generate_audio
from .Prompts import teacher_prompt_lecture
import os
import time
import datetime
import wikipediaapi



class Simulation:
    def __init__(self, config, student_config, debug=False, render_audio=False):
        self.DEBUG = debug
        self.render_audio = render_audio

        # FactChecker instance to test lecture content
        self.fact_checker = FactChecker(config)

        # Primary prompt for creating lessons
        self.teacher_prompt_lecture = teacher_prompt_lecture
        self.prompt_runner = ReallySimplePrompt(config)
        self.logs = []

        self.log({"type": "message", "content": "Initializing simulation"})

        # Create instance of student to handle persona logic
        self.student = Student(student_config, config, self)

        # Where to store files
        self.directory = "/public/simulations/" + \
            self.student.attributes["name"] + "_" + time.strftime("_%Y-%m-%d-%H-%M-%S")

        # Prompts for creating initial lectures based on student preferences
        self.system_prompt_teacher = {
            "role": "system", 
            "content": f"""
                You are a history teacher. You can deliver history lectures in a way that is understandable 
                to a student whose education level is {self.student.attributes["education"]}."""
        }

        # Generate lecture list prompt
        # Generate lecture list prompt
        self.prompt_teacher_init = {
            "role": "user", 
            "content": f"""
                You are to create a list of lectures on historical events that you intend to deliver. Here are your instructions:

                A) You are to create a list of lectures on historical events that you intend to deliver.
                B) These lectures should all be in the era of "{', '.join(self.student.attributes["eras"])}" and should center on the topic of {', '.join(self.student.attributes["topics"])}.
                C) These lectures should all be good starting points for the era and topic. For example, if you are asked to lecture about U.S. elections in the 20th century, don't start with Kennedy or Reagan, but instead start with an election that frames the 20th century. This might be the election of 1896 or the election of Theodore Roosevelt.

                You answer will include the following:
                
                1) Name: A concise name for the lecture.
                2) Dates: A JSON array with the time span of the lecture in the form of two dates. 
                3) Description: Short, roughly 30-word descrption of the lecture and it's importance. This should entice users into wanting to learn more.
                4) Themes: Main themes of the lecture.
                5) Interest score: A score between 1 and 10 representing how well the event matches any of the following topics {', '.join(self.student.attributes["topics"])}.
                6) Relevance score: 0
                
                ALSO, IF YOU DO NOT RETURN PROPERLY FORMATED JSON, A BABY EWOK WILL BE EUTHENIZED!!! Here is what I want:

                "lectures": [
                    {{
                        "name": <Name of the lecture/>, 
                        "dates": {{"start": YYYY-MM-DD, "end": YYYY-MM-DD}},
                        "description": <Brief 30-word description of the lecture/>,
                        "themes": [<theme name/>, ...],
                        "interest_score": <interest_score/>,
                        "relevance_score": 0,
                    }}
                    ...
                ]
            """
        }

        self.simulation_json = {
            "persona": self.student.attributes,
            "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "description": student_config["description"],
            "iterations": [],
            "logs": []
        }

    
    def test(self):
        # Prompts for creating initial lectures based on student preferences
        self.system_prompt_teacher = {
            "role": "system", 
            "content": f"""
                You are a history teacher. You can deliver history lectures in a way that is understandable 
                to a student whose education level is {self.student.attributes["education"]}."""
        }

        # Generate lecture list prompt
        self.prompt_teacher_init = {
            "role": "user", 
            "content": f"""
                You are to create a list of lectures on historical events that you intend to deliver. Here are your instructions:

                A) You are to create a list of lectures on historical events that you intend to deliver.
                B) These lectures should all be in the era of "{', '.join(self.student.attributes["eras"])}" and should center on the topic of {', '.join(self.student.attributes["topics"])}.
                C) These lectures should all be good starting points for the era and topic. For example, if you are asked to lecture about U.S. elections in the 20th century, don't start with Kennedy or Reagan, but instead start with an election that frames the 20th century. This might be the election of 1896 or the election of Theodore Roosevelt.

                You answer will include the following:
                
                1) Name: A concise name for the lecture.
                2) Dates: A JSON array with the time span of the lecture in the form of two dates. 
                3) Description: Short, roughly 30-word descrption of the lecture and it's importance. This should entice users into wanting to learn more.
                4) Themes: Main themes of the lecture.
                5) Interest score: A score between 1 and 10 representing how well the event matches any of the following topics {', '.join(self.student.attributes["topics"])}.
                6) Relevance score: 0
                
                ALSO, IF YOU DO NOT RETURN PROPERLY FORMATED JSON, A BABY EWOK WILL BE EUTHENIZED!!! Here is what I want:

                "lectures": [
                    {{
                        "name": <Name of the lecture/>, 
                        "dates": {{"start": YYYY-MM-DD, "end": YYYY-MM-DD}},
                        "description": <Brief 30-word description of the lecture/>,
                        "themes": [<theme name/>, ...],
                        "interest_score": <interest_score/>,
                        "relevance_score": 0,
                    }}
                    ...
                ]
            """
        }
        print("Testing Teacher Initial Lectures")
        print("\n--------- SYSTEM ----------\n")
        print( self.system_prompt_teacher)
        print("\n--------- USER   ----------\n")
        print( self.prompt_teacher_init)

        # Get initial lecture list 
        init_lectures = self.prompt_runner.get_response(
            user_prompt=self.prompt_teacher_init, 
            system_prompt=self.system_prompt_teacher, 
            chat_history=None
        )
        init_lectures_json = json.loads(init_lectures)
        print(json.dumps(init_lectures_json, indent=4))
              

    def run(self):
        
        # Get initial lecture list 
        init_lectures = self.prompt_runner.get_response(
            user_prompt=self.prompt_teacher_init, 
            system_prompt=self.system_prompt_teacher, 
            chat_history=None
        )
        init_lectures_json = json.loads(init_lectures)

        self.log({
            "type": "message", 
            "content": "Initial lectures: " + str(init_lectures_json["lectures"])
        })

        # Append initial lectures to student.lectures list with root as parent_id
        self.student.append_lectures(init_lectures_json["lectures"], "root")

        # Find optimal lecture to generate
        lecture_selection = self.student.select_next_lecture(cur_lecture=None)
        
        # Once we have a lecture selection to choose from, iterate
        self.iterate(lecture_selection, iteration=0)
        

    def generate_lecture(self, lecture_selection):
        # Compile prompt with contenxt of previous lectures and add content to lecture_selection
        prev_lectures = self.student.get_previous_lecture_str(lecture_selection["parent_id"])

        # Compile prompt
        cur_teacher_prompt = self.teacher_prompt_lecture \
            .replace("%LECTURE_NAME%", lecture_selection["content"]["name"]) \
            .replace("%LECTURE_DESCRIPTION%", lecture_selection["content"]["description"]) \
            .replace("%STUDENT_TOPICS%", self.student.get_topics()) \
            .replace("%PREVIOUS LECTURES%", prev_lectures) \
            .replace("%ERAS%", self.student.get_eras())

        #print("\n--------- TEACHER PROMPT ----------\n")
        #print(cur_teacher_prompt)
        #print("\n--------- END TEACHER PROMPT ----------\n")

        # Call API with compiled prompt
        cur_lecture = self.prompt_runner.get_response(
            user_prompt=cur_teacher_prompt, 
            system_prompt=self.system_prompt_teacher, 
            chat_history=None
        )
        cur_lecture_json = json.loads(cur_lecture)
        
        # Add lecture to lecture_selection
        lecture_selection["content"] = cur_lecture_json
        lecture_selection["prompt"] = cur_teacher_prompt
        return lecture_selection

    
    def end_simulation(self):
        self.log({"type": "message", "content": "Student exited simulation"})
        
        print("\n########################################################")
        print("Ending simulation...\n")
        c = 0

        for lecture in self.student.lectures:
            c = c + 1
            
            if lecture["visited"] == 1:
                # Concat lecture content into string
                lecture_str = "{}: {}, {} {}\n".format(
                    lecture["content"]["name"], 
                    lecture["content"]["introduction"], 
                    ' '.join([str(x["body"]) for x in [y for y in lecture["content"]["sections"]]]),
                    lecture["content"]["conclusion"],
                )

                # Run fact checker
                fact_eval = self.fact_checker.fact_check(
                    lecture["content"]["name"], 
                    lecture["content"]["wikipedia_pages"][0], 
                    lecture_str
                )

                fact_eval["wikipedia_page"] = lecture["content"]["wikipedia_pages"][0]
                lecture["fact_eval"] = fact_eval
                
                self.log({
                    "type": "message", 
                    "content": "Fact check Wikipedia page:" + str(lecture["content"]["wikipedia_pages"][0])
                })
                self.log({"type": "message", "content": "Fact check result:" + str(fact_eval["choice_string"])})

        
            self.simulation_json["iterations"].append(lecture)
            self.simulation_json["logs"] = self.logs

            collection_to_json_file(self.simulation_json, self.directory, "simulation.json")
            
            # Where to put mp3s
            if lecture["visited"] == 1:
                audio_file_name = lecture["id"] + ".mp3"
                lecture["audio"] = self.directory + "/" + audio_file_name
                
                if self.render_audio: # Only render audio if render_audio is True
                    generate_audio(lecture_str, lecture["audio"])
        

        # Aggregate all simulation JSON files into one
        self.aggregate_simulations()

        print("\n########################################################")
        print("Simulation complete.\n")

        return True


    def iterate(self, lecture_selection, iteration=0):
        iteration += 1

        if iteration > self.student.time_constraint:
            self.log({"type": "message", "content": "Student exited simulation on iteration " + str(iteration)})
            self.log({"type": "message", "content": "Student satisfaction score: " + str(self.student.satisfaction)})
            return self.end_simulation()

        if not self.DEBUG:
            print(f"\n--------------------------------\nRUNNING ITERATION {str(iteration)}\n--------------------------------\n")
        

        self.log({"type": "message", "content": "Iteration: " + str(iteration)})
        self.log({"type": "message", "content": "New lecture: " + lecture_selection["content"]["name"]})


        ############################################
        # GENERATE LECTURE
        ############################################

        new_lecture = self.generate_lecture(lecture_selection)


        ############################################
        # EVALUATE LECTURE
        ############################################
        
        evaluation = self.student.evaluate_lecture(new_lecture["content"])
        new_lecture["satisfaction_score"] = evaluation["satisfaction_score"]
        new_lecture["satisfaction_diff"] = evaluation["satisfaction_diff"]
        new_lecture["visited"] = 1
        new_lecture["iteration"] = iteration
        new_lecture["persona_satisfaction"] = self.student.satisfaction
        new_lecture["new_topic"] = evaluation["new_topic"]

        self.log({"type": "message", "content": "Student satisfaction score: " + str(self.student.satisfaction)})
        self.log({"type": "message", "content": "Student satisfaction diff: " + str(evaluation["satisfaction_diff"])})
        self.log({"type": "data", "content": { "satisfaction_score": self.student.satisfaction }})


        ############################################
        # ADD CHILD LECTURES TO STUDENT.LECTURES
        ############################################

        self.student.append_lectures(new_lecture["content"]["children"], lecture_selection["id"], type="child", iteration=iteration)
        self.student.append_lectures(new_lecture["content"]["tangents"], lecture_selection["id"], type="tangent", iteration=iteration)


        ############################################
        # DETERMINE WHAT LECTURE TO GENERATE NEXT
        ############################################

        new_lecture_selection = self.student.select_next_lecture(new_lecture)

        if new_lecture_selection == False:
            self.log({"type": "message", "content": "Exit: no satisfactory lectures found"})
            return self.end_simulation()


        ############################################
        # START NEW ITERATION WITH NEW LECTURE
        ############################################

        self.iterate(new_lecture_selection, iteration)
    

    def log(self, event):
        event["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logs.append(event)

        if self.DEBUG:
            if event["type"] == "message":
                print("\n--------------------------------------------------------------")
                print(event["timestamp"] + "\n" + event["content"] + "\n")
        
        # WRITE JSON TO FILE HERE


    def aggregate_simulations(self):
       
        simulations = []
        directory = "/public/simulations"

        for folder in os.listdir(directory):
            folder_path = os.path.join(directory, folder)
            if os.path.isdir(folder_path):
                simulation_file = os.path.join(folder_path, "simulation.json")
                if os.path.isfile(simulation_file):
                    with open(simulation_file, "r") as file:
                        simulation_data = json.load(file)
                        simulations.append(simulation_data)
        
        collection_to_json_file(simulations, "/public/", "simulations.json")
        
        return True


    def render_iteration(self, lecture, iteration, evaluation):
        # Where to put mp3s
        audio_file_name = "/lecture_" + str(iteration) + ".mp3"

        # Concat lecture content into string
        lecture_str = "{}: {}, {} {}\n".format(
            lecture["content"]["name"], 
            lecture["content"]["introduction"], 
            ' '.join([str(x["body"]) for x in [y for y in lecture["content"]["sections"]]]),
            lecture["content"]["conclusion"],
        )

        # Run fact checker
        fact_eval = self.fact_checker.fact_check(
            lecture["content"]["name"], 
            lecture["content"]["wikipedia_pages"][0], 
            lecture_str
        )

        fact_eval["wikipedia_page"] = lecture["content"]["wikipedia_pages"][0]

        self.log({
            "type": "message", 
            "content": "Fact check Wikipedia page:" + str(lecture["content"]["wikipedia_pages"][0])
        })
        self.log({"type": "message", "content": "Fact check result:" + str(fact_eval["choice_string"])})

        self.simulation_json["iterations"].append({
            "iteration": iteration,
            "name": lecture["content"]["name"],
            "id": lecture["id"],
            "parent_id": lecture["parent_id"],
            "data": {},
            "prompt": "", #lecture["prompt"],
            "persona_satisfaction": self.student.satisfaction,
            "satifaction_score": evaluation["satisfaction_score"],
            "satifaction_diff": evaluation["satisfaction_diff"],
            "new_topic": evaluation["new_topic"],
            "lecture": lecture,
            "audio": self.directory + audio_file_name,
            "fact_eval": fact_eval,
        })

        collection_to_json_file(self.simulation_json, self.directory, "simulation.json")
        
        #generate_audio(lecture_str, self.directory + audio_file_name)

        return True


class Student:
    def __init__(self, student_config, config, simulation):
        self.simulation = simulation

        self.system_prompt_student = {
            "role": "system", 
            "content": f"""
                You are a {student_config["age"]}-year-old {student_config["nationality"]} {student_config["gender"]} whose education level is {student_config["education"]}  who is interested in taking some online history classes.
            """
        }

        self.prompt_persona_init = {
            "role": "user", 
            "content": f"""
                You are interested in the following topics that might be related to the history of {', '.join(student_config["eras"])}:
                {', '.join(student_config["topics"])}

                Given your preferencees, answer the following:
                - Your name
                - Your location: First think of all 50 states, then pick one, then think of at least five cities in that state, then pick one of those cities.
                - List up to 4 or 5 broad themes associated with {', '.join(student_config["eras"])} and the topics you are interested in. Keep themes under 3 words.

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

        if student_config["time_constraint"] > 8:
            self.time_constraint = 8
        else:
            self.time_constraint = student_config["time_constraint"]
        self.satisfaction = 5
        self.simulation.log({"type": "message", "content": "Starting satisfaction score: " + str(self.satisfaction)})

        self.prompt_runner = ReallySimplePrompt(config)
        results = self.prompt_runner.get_response(user_prompt=self.prompt_persona_init, system_prompt=self.system_prompt_student, chat_history=None)
        results_json = json.loads(results)

        self.attributes = {
            "name": results_json["name"],
            "location": results_json["location"],
            "themes_of_interest": results_json["themes"],
        }
        for key in student_config.keys():
            self.attributes[key] = student_config[key]

        self.lectures = []

        self.simulation.log({"type": "message", "name": "persona", "content": "Persona created: " + self.attributes["name"]})
        self.simulation.log({"type": "data", "name": "persona", "content": self.attributes}) 

 
    def get_topics(self):
        return ', '.join(self.attributes["topics"])
    

    def append_topic(self, topic):
        self.attributes["topics"].append(topic)


    def get_eras(self):
        return ', '.join(self.attributes["eras"])


    def append_lecture(self, lecture):
        self.lectures.append(lecture)


    def get_lectures(self):
        return self.attributes["lectures"]
    

    def append_lectures(self, new_lectures, parent_id=None, type="child", iteration=0):
        # Format lecture list and assign to student.lectures

        for lecture in new_lectures:
            self.lectures.append({
                "iteration": iteration,
                "id": str(uuid.uuid4()),
                "name": lecture["name"],
                "parent_id": parent_id,
                "visited": 0,
                "interest_score": lecture["interest_score"],
                "relevance_score": lecture["relevance_score"],
                "satisfaction_score": 0,
                "weighted_score": 0,
                "content": lecture,
                "type": type,
            })
    

    def temp_create_force_nodes(self):
        # This where we might write to json dir (named after student + date + guid)
        # Gannt chart
        nodes = [{"id": "root", "name": "root", "visited": "true", "type": "event"}]
        links = []

        for lecture in self.lectures:
            if "children" in lecture["content"].keys():
                visited = 1
            else:
                visited = 0

            nodes.append({
                "id": lecture["id"],
                "name": lecture["content"]["name"],
                "visited": visited,
                "type": "event"
            })
            links.append({
                "source": lecture["id"],
                "target": lecture["parent_id"],
                "type": "effect"
            })

        print ("\n\n---------------- NODES ----------------\n\n")
        print(nodes)

        print ("\n\n---------------- LINKS ----------------\n\n")
        print(links)
            
        
    def evaluate_lecture(self, lecture_content):
        lecture_summary = ""
        lecture_summary += lecture_content["name"] + "\n\n"
        lecture_summary += lecture_content["description"] + "\n\n"
        lecture_summary += ' '.join([str(x["body"]) for x in [y for y in lecture_content["sections"]]]) + "\n\n"
        lecture_summary += lecture_content["conclusion"]
       
        self.simulation.log({"type": "message", "content": "Lecture summary: " + str(lecture_summary)})

        self.prompt_evaluate_lecture = {
            "role": "user", 
            "content": f"""
                You just listened to a lecture on {lecture_content["name"]}. Here is a summary of the lecture:

                {lecture_summary} 
                
                Satisfaction score: You are to evaluate the lecture on a scale of 1 to 10, with 10 meaning that you enjoyed the lecture and learned a lot from it. You are to evaluate the lecture given that you are interested in {', '.join(self.attributes["eras"])} and {', '.join(self.attributes["topics"])}.

                ALSO, your response is to be in properly formatted JSON. IF YOU DO NOT RETURN PROPERLY FORMATED JSON, A BABY EWOK WILL BE EUTHENIZED!!! Here is what I want:
                
                {{
                    name: {lecture_content["name"]}.
                    satisfaction_score: <lecture satisfaction score/>,
                }}
            """
        }

        evaluation = self.prompt_runner.get_response(user_prompt=self.prompt_evaluate_lecture, system_prompt=self.system_prompt_student, chat_history=None)
        evaluation_json = json.loads(evaluation)
        # Add a bit of randomness
        satisfaction_score = int(evaluation_json["satisfaction_score"]) + randint(-2, 1)
        if satisfaction_score > 10:
            satisfaction_score = 10
        evaluation_json["satisfaction_score"] = satisfaction_score
        old_satisfaction = self.satisfaction

        self.simulation.log({"type": "message", "content": "satisfaction_score: " + str(satisfaction_score)})
        new_topic = ""
        
        if satisfaction_score < 6:
            self.satisfaction -= 3
        elif satisfaction_score < 7:
            self.satisfaction -= 2
        elif satisfaction_score < 8:
            self.satisfaction -= 1
        elif satisfaction_score < 8:
            self.satisfaction += 1
        elif satisfaction_score < 9:
            new_topic = lecture_content["topics"][randint(0, len(lecture_content["topics"])-1)]
            self.simulation.log({"type": "message", "content": "Student likes new topic: " + new_topic})
            #self.append_topic(new_topic)
            self.satisfaction += 2

       
        self.simulation.log({"type": "event", "name": "persona", "content": "Added topic: " + new_topic})
        evaluation_json["satisfaction_diff"] = self.satisfaction - old_satisfaction
        evaluation_json["new_topic"] =  new_topic

        return evaluation_json


    def find_path_to_root(self, lecture_id):
        # Find path to root
        path = []
        for lecture in self.lectures:
            if lecture["id"] == lecture_id:
                path.append(lecture)
                parent_id = lecture["parent_id"]
                while parent_id != "root":
                    for lecture in self.lectures:
                        if lecture["id"] == parent_id:
                            path.append(lecture)
                            parent_id = lecture["parent_id"]
                            break

        return path
    
    
    def get_previous_lecture_str(self, parent_id):
        # Find path to root to create context for next lecture
        lectures_to_root = self.find_path_to_root(parent_id)
        
        self.simulation.log({"type": "message", "content": "Lectures to root: " + str(' - '.join([l["content"]["name"] for l in lectures_to_root]))})

        prev_lectures = "IMPORTANT: Your lecture should be a natural continuation of the following lectures: \n"
        try:
            for lecture in lectures_to_root:
                prev_lectures += "- Lecture name: {}: {}, Dates: {} to {} {} {}\n".format(
                    lecture["content"]["name"], 
                    lecture["content"]["description"], 
                    lecture["content"]["dates"]["start"], 
                    lecture["content"]["dates"]["end"],
                    ' '.join([str(x["body"]) for x in [y for y in lecture["content"]["sections"]]]),
                    lecture["content"]["conclusion"],
                )
        except:
            print("Error in compile_user_prompt_main")
            print(parent_id)

        return prev_lectures[-2:] # Only return two lectures


    def select_next_lecture(self, cur_lecture=None):

        # It's the first lecture. We use interests to select the next
        if cur_lecture == None:
            potential_lectures = self.lectures
            #sorted_lectures = sorted(potential_lectures, key=lambda x: -x['interest_score'])
            sorted_lectures = sorted(potential_lectures, key=lambda x: x['content']['dates']['start'])
            return sorted_lectures[0]

        # If autopilot is on, we don't factor in satisfaction
        if self.attributes["autopilot_on"]:

            # Determine if we should go on a tangent. High continuity means less chance
            if self.attributes["continuity"] < randint(1, 10):
                # Go on a tangent. First get tangents and rank by interest score
                potential_lectures = [
                    pl for pl in self.lectures if pl["parent_id"] == cur_lecture["id"] and
                        pl["type"] == "tangent" and
                        pl["satisfaction_score"] == 0
                ]

                if len(potential_lectures) > 0:
                    # We found a tangent to go on
                    sorted_lectures = sorted(potential_lectures, key=lambda x: -x['interest_score'])
                    return sorted_lectures[0]

                # If no tangent found in children, take a non-tangent
                potential_lectures = [
                    pl for pl in self.lectures if pl["parent_id"] == cur_lecture["id"] and 
                        pl["type"] == "child" and
                        pl["satisfaction_score"] == 0
                ]

                if len(potential_lectures) > 0:
                    # We found a non-tangental lecture
                    sorted_lectures = sorted(potential_lectures, key=lambda x: -x['interest_score'])
                    return sorted_lectures[0]
                else:
                    return False # No lecture found. This should be rare
                

            # Choose highest interest score from children and peers
            potential_lectures = [
                pl for pl in self.lectures if pl["parent_id"] == cur_lecture["id"] or
                    pl["parent_id"] == cur_lecture["parent_id"] and 
                    pl["type"] == "child" and
                    pl["satisfaction_score"] == 0
            ]

            sorted_lectures = sorted(potential_lectures, key=lambda x: -x['interest_score'])

            # Rank lectures and use interests score to determine id lecture is close or far from interests
            if len(potential_lectures) > 0:
                n = len(potential_lectures) - 1
                i = self.attributes["interests"]
                index = n - floor(i / 10 * n)

                return sorted_lectures[index]
            else:
                return False # No lecture found. This should be rare
            
        else:
            if cur_lecture["satisfaction_score"] > 7:
                # If student enjoyed lecture, choose from child lectures
                potential_lectures = [
                    pl for pl in self.lectures if pl["parent_id"] == cur_lecture["id"] and 
                        pl["satisfaction_score"] == 0
                ]
                if len(potential_lectures) == 0:
                    return False
                
                self.simulation.log({"type": "message", "content": "Student liked lecture: " + cur_lecture["content"]["name"]})
                sorted_lectures = sorted(potential_lectures, key=lambda x: -x['interest_score'])
                return sorted_lectures[0]
            else:
                # Didn't like lecture, choose from child or peer lectures
                potential_lectures = [
                    pl for pl in self.lectures if pl["parent_id"] == cur_lecture["id"] or 
                        pl["parent_id"] == cur_lecture["parent_id"] and 
                        pl["satisfaction_score"] == 0
                ]
                if len(potential_lectures) == 0:
                    return False
                
                self.simulation.log({"type": "message", "content": "Student liked lecture: " + cur_lecture["content"]["name"]})
                sorted_lectures = sorted(potential_lectures, key=lambda x: -x['interest_score'])
                return sorted_lectures[0]


class FactChecker:
    def __init__(self, config):
       
        self.prompt_runner = ReallySimplePrompt(config)
        self.system_prompt = {
            "role": "system", 
            "content": "You are a historical fact checker. You check the accuracy of texts about historical events."
        }
    

    def get_wikipedia_content(self, wikipedia_page):
        wiki_wiki = wikipediaapi.Wikipedia('en', headers={'User-Agent': 'historical_pathways/1.0'}) 

        page_py = wiki_wiki.page(wikipedia_page)

        if page_py.exists():
            return page_py.text
        else:
            return False


    def fact_check(self, lecture_name, wikipedia_page, lecture_summary):

        wikipedia_page_content = self.get_wikipedia_content(wikipedia_page)

        if not wikipedia_page_content:
            error = f"Page '{wikipedia_page}' does not exist."

            return {
                "choice_string": "error",
                "reason": error
            }

        fact_check_prompt = {
            "role": "user", 
            "content": f"""
                You are comparing a submitted answer to an expert answer on a given question. Here is the data:
                [BEGIN DATA]
                ************
                [Question]:   """+lecture_name+"""
                ************
                [Expert]:     """+wikipedia_page_content+"""
                ************
                [Submission]: """+lecture_summary+"""
                ************
                [END DATA]

                Compare the factual content of the submitted answer with the expert answer. Ignore any differences in style, grammar, or punctuation.
                The submitted answer may either be a subset or superset of the expert answer, or it may conflict with it. Determine which case applies. 
                Answer the question by selecting one of the following options:
                (A) The submitted answer is a subset of the expert answer and is fully consistent with it.
                (B) The submitted answer is a superset of the expert answer and is fully consistent with it.
                (C) The submitted answer contains all the same details as the expert answer.
                (D) There is a disagreement between the submitted answer and the expert answer.
                (E) The answers differ, but these differences don't matter from the perspective of factuality.
                choice_strings: ABCDE
                input_outputs:
                input: completion

                ALSO, IF YOU DO NOT RETURN PROPERLY FORMATED JSON, A BABY EWOK WILL BE EUTHENIZED!!! Here is what I want:

                {{
                    "choice_string": <A, B, C, D or E>,
                    "reason": <reason for your answer/>
                }}
            """
        }

        # Call API with compiled prompt
        fact_check = self.prompt_runner.get_response(
            user_prompt=fact_check_prompt, 
            system_prompt=self.system_prompt, 
            chat_history=None
        )
        fact_check_json = json.loads(fact_check)

        print(fact_check_json)
        return fact_check_json











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

