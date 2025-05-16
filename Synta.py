from re import sub
import subprocess
from google import genai
from dotenv import load_dotenv
import os 

load_dotenv()

api_key=os.getenv("API_KEY")

if api_key:

    try:

        client = genai.Client(api_key=api_key)
        # User Query
        lol= input("Enter what you need to do :")
        query = f"{lol} Create a concise schedule. Include only start and end times. Prioritize tasks, and add breaks where needed. Keep the result compact and clear."
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=query,
        )

        try:

            # convert response into string
            file_response= str(response.text)
            #Store the response in a text file
            home_dir=os.path.expanduser("~")
            file_path=os.path.join(home_dir,"Synta_schedule.txt")
            with open(file_path,'w') as file: 
                file.write(file_response)

        except Exception as e:
            print(f"An error has occured : {e}")

    except Exception as e:
        # Log Files 
        print(f"An Error has occured : {e}")
else:
    # Log files
    print("API Key Not loaded")


# Action Library , Calling Rust files:
class Synta:
    def __init__(self) -> None:
        pass

    def delete_rust_files(self):
        #Executing rust binary created in delete_synta_respose
        subprocess.run(["~/murakon_dev/productivity_tool/delete_synta_respose/target/release/delete_synta_respose"])
    def regex_clean(self):
        # Cleans the markup asterics that comes from Gemini
        subprocess.run(["/home/murakon/murakon_dev/productivity_tool/clean_synta_response/target/release/clean_synta_response"])

    def display(self):
    # Displays the Final Schedule:
        self.regex_clean()
        subprocess.run(["/home/murakon/murakon_dev/productivity_tool/display_schedule/target/release/display_schedule"])

if __name__ == "__main__":
    lol= Synta()
    lol.display()
