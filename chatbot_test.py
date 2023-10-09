import openai
import json 
import random

from sentiment_analysis import *
from emotion_recog import *

openai.api_key = "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"

#use this to change the style of prompt
changePrompt = {
                    "genZ":"now rephrase the previous response, but pretend you are a gen z influencer that constantly talks in the stereotypical gen z speech pattern",
                    "yassify":"now rephrase the previous response, but yassify it as much as you can",
                    "emoji":"now rephrase the previous response, but include as many relevant emojis as you can",
                    "medieval":"now rephrase the previous response, but pretend that you are a knight in the medieval times"
}



journalPrompt = "Generate a journal entry from the point of view of Person B without mentioning Person A given the following chat logs."
#facts will be a concatenation of the list of responses from the journaling session


#randomize prompt and message:
def randomizePrompt(messages):
    buttonPressed = True
    theme, prompt = random.choice(list(changePrompt.items()))
    if(buttonPressed):
        message = prompt
        messages.append({"role":"user","content":message})
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages = messages)
        reply = response["choices"][0]["message"]["content"]
        messages.append({"role":"assistant","content":reply})
        print(">" +reply + "\n")
    return messages
    

def createJournal(messages,chatLogs):
    # prompt Ai-generated journal entry
    messages.append({"role": "assistant","content":journalPrompt + chatLogs })
    response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages = messages)
    reply = response["choices"][0]["message"]["content"]
    messages.append({"role":"assistant","content":reply})
    print(f">Here is your AI generated journal entry: {reply} ")
    return messages

# # User must send the first message
# message = input()
# messages.append({"role":"user","content":message})
# AI chat bot ask user a question to gauge their mental health
# messages.append({"role": "assistant","content":questions[index]})
# get CHAT GPT reply
def chatLoop(messages,promptAnswers):
    finished = False
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = messages)
    
    reply = response["choices"][0]["message"]["content"]
    messages.append({"role":"assistant","content":reply})
    print(">" +reply + "\n")

    # get user's response
    message = input()
    score = get_sentiment(message)
    print("score:",score)
    emotion = classify_emotion(message)
    print("emotion:",emotion)
    #if the emotion and sentiment do not match
    if(   ((emotion =='anger' or emotion == 'sadness') and score >= .2)
       or ((emotion =='joy' or emotion == 'love') and score <= -.2)):
        #disregard the ai
        #something more complex here
        score = 0
        emotion = ''
    else:
        #do something with the data
        message += f"please keep in mind that I am feeling {emotion}"

    if message == "finish":
        finished = True
    messages.append({"role":"user","content":message})

    # promptAnswers.append(f"The response to the question: {questions[index]} is {message}")
    promptAnswers.append(f"Person A: {reply}\n Person B:{message}\n")
    return messages,promptAnswers,finished

def main():
    messages = []
    promptAnswers = []
    
    #system message sets the type of behavior that you want GPT to exhibit 
    # system_msg = input("What type of chatbot would you like to create?\n")
    system_msg = "friendly, approachable, and supportive"
    messages.append({"role":"system", "content":system_msg})

    #gray text that says: type in finish to finish the session.
    initial_message = 'Hello please guide me in making a journal entry and ask me questions to help me think. Lets start with you exactly repeating the following phrase and nothing else:"Would you like to make a journal entry?""'
    # message = input()
    messages.append({"role":"user","content":initial_message})

    # Chat GPT AI Journaling help
    while True:
        messages,promptAnswers,finished = chatLoop(messages,promptAnswers)
        if(finished):
            break
    chatLogs = "\n".join(promptAnswers)
    #maybe call to change the way that it's phrased
    messages = createJournal(messages,chatLogs)
    messages = randomizePrompt(messages)


if __name__ == "__main__":
    main()

# would you like to post?
# give them the chance to modify their post
# yassify genz-ify button that changes
# asking in a x way is kinda bad ngl
# immediately takes them to the home page
# ? how do we create the profiles?

# how is the ai being used?
# create a heuristic based on sentiment analysis, as well as emotional analysis
# guides how the ai will ask you, change it's tone or ask you different questions depending on the mood

# show posts that are more relevant to you?
# how do we want to group profiles?