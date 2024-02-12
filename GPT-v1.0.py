from openai import OpenAI
from dotenv import dotenv_values
from colorama import Fore, Style, just_fix_windows_console 
just_fix_windows_console() #enable colorama for Windows 10
config = dotenv_values(".env")["OPENAI_API_KEY"]
client = OpenAI(api_key=config)

def main():
    sysP = input(Fore.RED + Style.BRIGHT + "Please input a personality trait(s) (Happy, Sad, Angry, Sarcastic, Polite, Rude, etc.) or the persona (A Valiant Knight, A Pastry Chef, Adam Sandler, etc.) you would like the chatbot to adopt\n" + Fore.RESET + Style.RESET_ALL)
    if sysP == "": #Sets generic value if no input
        sysP = "a chatbot."
    history = [{"role": "system", "content": f"You are {sysP}"}] #List of message history; structured as a list of dictionaries that will be appended before the user's prompt to provide context to language model based off past messages in the current instance
    while True: #Runs until user presses CTRL+C
        try:
            usrprmpt = input(Fore.CYAN + Style.BRIGHT + "\nInput: " + Fore.RESET + Style.RESET_ALL)
            history.append({"role": "user", "content": f"{usrprmpt}"})
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=history # Uses history list as context/"training" and uses last entered usrprmpt as the user's prompt
            )
            chatCompletion = response.choices[0].message #Trims results to only show assistant/ai response
            history.append({"role" : chatCompletion.role, "content" : chatCompletion.content})
            print("\n===================================================================================================\n\n" + Style.BRIGHT + f"{chatCompletion.role}: {chatCompletion.content}" + Style.RESET_ALL + "\n\n===================================================================================================") #Prints assistant/ai response
        except KeyboardInterrupt: #Exception in the case the user exits
            print("\"CTRL+C\" detected; closing chat bot")
            log = "" # A variable to store a log of all messages from the current instance
            for i in history: #Iterates through the message history, and appends each role:content pair in an easy to read format
                log += f"role: {i['role']}, content: {i['content']}\n"
            print(log) #Prints out a copy of all messages
            with open("log.txt", "a") as file: # Opens "log.txt" and appends the contents of the "log" variable to the end of it, and automatically closing the file when exiting the "with" block
                file.write(log)
            exit()

if __name__ == "__main__": #Effectively runs the main() function on startup
    main()
