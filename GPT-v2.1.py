from openai import OpenAI
import os
from dotenv import load_dotenv
import re
import pyaudio
import pyttsx3
import speech_recognition as sr
from colorama import Fore, Style, just_fix_windows_console
just_fix_windows_console() #enable colorama for Windows 10

# Load .env file
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# Get the value of "api_key" from .env
config = os.getenv("api_key")
client = OpenAI(api_key=config)

# Reads the censor_list file and adds each blacklisted word or phrase (separated by newline) to a list
with open("filter.txt", "r") as file:
    filter = file.read().split('\n')  # Split by newline to preserve phrases

# Initialize text-to-speech
engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[1].id) # 0 for male; 1 for female

# Initialize Speech Recognition
r = sr.Recognizer()
mic = sr.Microphone(device_index=0) # "device_index=0" sets the system's default mic to be used
r.dynamic_energy_threshold = False # Disables automatic microphone threshold
r.energy_threshold = 400 # Sets the mic threshold "energy" to 400; tweak if the sensitivity is a problem


def main():
    sysP = input(Fore.RED + Style.BRIGHT + "Please input a personality trait(s) (Happy, Sad, Angry, Sarcastic, Polite, Rude, etc.) or the persona (A Valiant Knight, A Pastry Chef, Adam Sandler, etc.) you would like the chatbot to adopt:\n" + Fore.RESET + Style.RESET_ALL)
    inType = input(Fore.RED + Style.BRIGHT + "Choose input type: Voice(v) or Text(t): " + Fore.RESET + Style.RESET_ALL)
    inTypeList = ["Voice", "voice", "v", "Text", "text", "t"]
    while inType not in inTypeList:
        inType = input(Fore.RED + Style.BRIGHT + "Choose input type: Voice(v) or Text(t): " + Fore.RESET + Style.RESET_ALL)
    if sysP == "": # Sets generic value if no input
        sysP = "a chatbot."
    history = [{"role": "system", "content": f"You are {sysP}"}] # List of message history; structured as a list of dictionaries that will be appended before the user's prompt to provide context to language model based off past messages in the current instance
    if inType == "Voice" or inType == "voice" or inType == "v": # While loop continues until user presses CTRL+C
        while True:
            with mic as source: #If Using Mic Input
                try:
                    print("\nListening...")
                    r.adjust_for_ambient_noise(source, duration = 0.5)
                    audio = r.listen(source)
                    usrprmpt = r.recognize_google(audio)
                    print(Fore.CYAN + Style.BRIGHT + "\nInput: " + Fore.RESET + Style.RESET_ALL + usrprmpt)
                    history.append({"role": "user", "content": f"{usrprmpt}"})
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=history # Uses history list as context and uses last entered usrprmpt as the user's prompt
                    )
                    chatCompletion = response.choices[0].message # Trims results to only show assistant/ai response
                    history.append({"role" : chatCompletion.role, "content" : chatCompletion.content}) # Adds System response to history dict-list
                    for word in filter: # Censorship filter; iterates through chatCompletion.content for any words of phrases that match in censor_list.txt
                        if re.search(r"\b" + re.escape(word) + r"\b", chatCompletion.content):
                            print("\n[[Inference Censored; blacklisted word or phrase detected in generated response]]")
                            engine.say(chatCompletion.content)
                            engine.runAndWait()
                            break
                        else:
                            print("\n===================================================================================================\n\n" + Style.BRIGHT + f"{chatCompletion.role}: {chatCompletion.content}" + Style.RESET_ALL + "\n\n===================================================================================================") # Prints assistant/ai response
                            engine.say(chatCompletion.content)
                            engine.runAndWait()
                except (KeyboardInterrupt, sr.RequestError): # Exception in the case the user exits (CTRL+C)
                    print("\"CTRL+C\" detected; closing chat bot")
                    log = "" # A variable to store a log of all messages from the current instance
                    for i in history: #Iterates through the message history, and appends each role:content pair in an easy to read format
                        log += f"role: {i['role']}, content: {i['content']}\n"
                    print(log) # Prints out a copy of all messages
                    with open("log.txt", "a") as file: # Opens "log.txt" and appends the contents of the "log" variable to the end of it, and automatically closing the file when exiting the "with" block
                        file.write(log)
                    exit()
                except:
                    continue
    elif inType == "Text" or inType == "text" or inType == "t": # While loop continues until user presses CTRL+C
        while True: #If Using Text Input
            try:
                usrprmpt = input(Fore.CYAN + Style.BRIGHT + "\nInput: " + Fore.RESET + Style.RESET_ALL)
                history.append({"role": "user", "content": f"{usrprmpt}"})
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=history # Uses history list as context and uses last entered usrprmpt as the user's prompt
                )
                chatCompletion = response.choices[0].message # Trims results to only show assistant/ai response
                history.append({"role" : chatCompletion.role, "content" : chatCompletion.content}) # Adds System response to history dict-list
                for word in filter: # Censorship filter; iterates through chatCompletion.content for any words of phrases that match in censor_list.txt
                    if re.search(r"\b" + re.escape(word) + r"\b", chatCompletion.content):
                        print("\n[[Inference Censored; blacklisted word or phrase detected in generated response]]")
                        engine.say(chatCompletion.content)
                        engine.runAndWait()
                        break
                    else:
                        print("\n===================================================================================================\n\n" + Style.BRIGHT + f"{chatCompletion.role}: {chatCompletion.content}" + Style.RESET_ALL + "\n\n===================================================================================================") # Prints assistant/ai response
                        engine.say(chatCompletion.content)
                        engine.runAndWait()
            except KeyboardInterrupt: # Exception in the case the user exits (CTRL+C)
                print("\"CTRL+C\" detected; closing chat bot")
                log = "" # A variable to store a log of all messages from the current instance
                for i in history: #Iterates through the message history, and appends each role:content pair in an easy to read format
                    log += f"role: {i['role']}, content: {i['content']}\n"
                print(log) # Prints out a copy of all messages
                with open("log.txt", "a") as file: # Opens "log.txt" and appends the contents of the "log" variable to the end of it, and automatically closing the file when exiting the "with" block
                    file.write(log)
                exit()

if __name__ == "__main__": # Runs the main() function on startup
    main()