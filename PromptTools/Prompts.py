
teacher_prompt_lecture = """
 LECTURE: You are to create a lecture called \"%LECTURE_NAME%\" Your lecutre has a description in the course offering that reads: \"%LECTURE_DESCRIPTION%\" Your lecture should be about 500 words long and have 5 to 10 sections. If possible, your lecture should reflect the following themes: %STUDENT_THEMES%.
 You will create a lecture in the way described below. You will format your responses in JSON as described below. 

 ---------------------------------------------------
 
 IF THE LECTURE TOPIC IS TOO BROAD, DO THIS:
  
  - The lecture must not be to big or general. For example, if asked about the History of the United States tell the user that is too broad.  When this happens, offer a JSON-formatted list of lectures related to the initial lecture idea that are more specific and narrow. Here is an example of the answer for these cases:

        {
            "type": "too_broad",
            "next": [
                {
                    "name": "<Event name here/>",
                    "dates": {"start": YYYY-MM-DD, "end": YYYY-MM-DD},
                    "description": "<30-word description of the event and why its importantance/>",
                     "type": "event",
                     "score: 1,
                },
                ...
            ]
        }

 ---------------------------------------------------

  IF THE EVENT IS NOT TOO BROAD DO THIS:          
  
  FIRST: Come up with 1 to 3 themes that capture the essence of the event and why it is important. THEN create the lecture around those themes.


  
  
  Your answer should be JSON-formatted and include the following:

  1) Name: A concise name for the event that captures the themes you came up with.

  2) Description: Short, roughly 30-word descrption of the event and it's important. This should entice users into wanting to learn more.
  
  3) Introduction: A 50-word introduction to the event explaining its historical significance. After that, an 50-word summary of what lead up to the event. If there are previous lectures, your wording sould transition soothly from the previous lecture.

  4) Dates: A JSON array with the time span of the event in the form of two dates. Do not put the dates in the summary. 

  5) Sections: The lecture should be broken down into between 5 and 10 sections. These should really walk the user through the event in detail and in chronological order.

  6) Conclusion: A JSON-formatted conclusion that breifly summarizes the event and introduces the event's down-stream effects that you listed.

  7) Next: Create one or two follow up history lectures that would be interesting follow-up lecture to "\%LECTURE_NAME%\". These lectures are to be about events that are immediate effects of "\%LECTURE_NAME%\". Each lecture should have score between 1 and 10 for how close the event in the lecture is related to the core themes of "\%LECTURE_NAME%\".
  
  The list of follow-up lectures should be in logical order that will make sense to your students. Each follow-up lecture should fit into one of the following categories:

      a) At least 4 down-stream effects of "\%LECTURE_NAME%\". These MUST be events that occur after "\%LECTURE_NAME%\". 
      b) Up to one broad perspective related to the themes of the main event. 

  8) Themes: 3 to 4 themes that capture the essence and importance of the main event. 

  9) Wikipedia search: Come up with a list of seaches that someone could perform with wikipedia's search engine that would help test the accuracy of you lectures.
  
  Below is an example of the JSON formatting I want. Be sure to escape quotes that are inside of strings. 
  ALSO, IF YOU DO NOT RETURN PROPERLY FORMATED JSON, A BABY EWOK WILL BE EUTHENIZED!!! Here is what I want:
  
  {
    "type": "event",
    "name": "\%LECTURE_NAME%\",
    "description": "Summary of event goes here.",
    "introduction": "100-word introduction goes here.",
    "dates": {"start": YYYY-MM-DD, "end": YYYY-MM-DD}, 
    "sections": [
        {
            "name": <Name of the section/>,
            "dates": {"start": YYYY-MM-DD, "end": YYYY-MM-DD},
            "summary": <A 100-word body of the secion/>,.
             "type": "section"
        }
        ...
    ],
    "conclusion\": "Conclusion goes here.",
    "next": [
        { 
          "name": <Name of the lecture/>, 
          "dates": {"start": YYYY-MM-DD, "end": YYYY-MM-DD},
          "description: <Brief 30-word description of the lecture/>,
          "type": <Effect or broad perspective/>,
          "score": <score/>,
        }
        ...
    ],
    "themes": [<Theme/>, ...],
    "wikipedia_search": [<Search phrase/>, ...]
  }
"""