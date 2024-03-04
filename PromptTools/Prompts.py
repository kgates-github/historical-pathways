
teacher_prompt_lecture = """
 LECTURE: You are to create a lecture called \"%LECTURE_NAME%\" Your lecture has a description in the course offering that reads: \"%LECTURE_DESCRIPTION%\" Your lecture should be about 1000 words long and have 5 to 10 sections. If possible, your lecture should reflect the following topics: %STUDENT_TOPICS%.
 You will create a lecture in the way described below. You will format your responses in JSON as described below. 

 BEFORE YOU BEGIN... You have a golden rule: Do not use the words "transformative", "pivotal", "iconic" or "crucial" in your lectures. If you do, I WILL PET A CAT BACKWARDS AGAINST THE NATURAL DIRECTION OF ITS FUR AND THE CAT WILL BE PERTURBED. 

 ---------------------------------------------------
 
 IF THE LECTURE TOPIC IS TOO BROAD, DO THIS:
  
  - The lecture must not be to big or general. For example, if asked about the History of the United States tell the user that is too broad.  When this happens, offer a JSON-formatted list of lectures related to the initial lecture idea that are more specific and narrow. Here is an example of the answer for these cases:

    {
        "type": "too_broad",
        "children": [
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

  %PREVIOUS LECTURES%
  
  Your answer should be JSON-formatted and include the following:

  1) Name: A concise name for the event that captures the themes you came up with.

  2) Description: Short, roughly 30-word descrption of the event and it's importance. 
  
  3) Introduction: A 50-word introduction to the event explaining its historical significance. After that, an 50-word summary of what lead up to the event. If there are previous lectures, your wording sould transition soothly from the previous lecture.

  4) Dates: A JSON array with the time span of the event in the form of two dates. Do not put the dates in the summary. 

  5) Sections: The lecture should be broken down into between 5 and 10 sections. These should walk the user through the event in detail and in chronological order.

  6) Conclusion: A JSON-formatted conclusion that breifly summarizes the event and introduces the event's down-stream effects that you listed.

  7) Children: Create 3 or 4 follow-up history lectures that would be good follow-up lectures to "\%LECTURE_NAME%\". Try to stay close to the event in time, and don't go more than 10 years into the future.
    - Each lecture should have a relevance_score between 1 and 10 for how close the event in the lecture is related to the themes of "\%STUDENT_TOPICS%\".
    - Each lecture should have a insterestingness_score between 1 and 10 for how close the event in the lecture is related to the themes of "\%STUDENT_TOPICS%\".

  8) Tangents: Come up with 3 or 4 historic events that took place around the same time as "\%LECTURE_NAME%\" that is not directly related to "\%LECTURE_NAME%\" but is related to "\%STUDENT_TOPICS%\".
    - The tangent should have a insterestingness_score between 1 and 10 for how close the event in the lecture is related to the themes of "\%STUDENT_TOPICS%\".

  9) Themes: 2 to 3 themes that capture the essence and importance of the main event. These should no more that 2 words.

  10) Topics: 2 to 3 topics that are part of the main event. These should no more that 2 words.

  11) Wikipedia page: Come up with a list of Wikipedia pages that would help test the accuracy of your lecture on "\%LECTURE_NAME%\". These are to be pages and not full URLS
  
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
            "body": <A 100-word body of the secion/>,.
            "type": "section"
        }
        ...
    ],
    "conclusion\": "Conclusion goes here.",
    "children": [
        { 
          "name": <Name of the lecture/>, 
          "dates": {"start": YYYY-MM-DD, "end": YYYY-MM-DD},
          "description: <Brief 30-word description of the lecture/>,
          "type": <Effect or broad perspective/>,
          "relevance_score": <relevance_score/>,
          "interest_score": <interest_score/>,
        }
        ...
    ],
    "tangents": [{
        "name": <Name of the tangent/>,
        "dates": {"start": YYYY-MM-DD, "end": YYYY-MM-DD},
        "description: <Brief 30-word description of the tangent/>,
        "type": <Tangent/>,
        "relevance_score": 0,
        "interest_score": <interest_score/>,
      },
      ...
    ],
    "themes": [<Theme/>, ...],
    "topics": [<Topic/>, ...],
    "wikipedia_pages": [<Wikipedia page/>, ...]
  }
"""