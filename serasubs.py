#oh my god/// why are you looking at my code omg BBBBAKA you're looking through
# a girl's personal things KYAAAA omgg/////

#okay i'm kidding but im so anxious about others looking at my code so
#if you've found your way here i guess i'll show you around
#because im an anxious wreck and also i love my script baby

#basically here we're importing the stuff we need like the language model
#and thing to create this user friendly ui and stuff
import sys
import site
import os
import threading
import whisper
import tkinter as tk
from tkinter import filedialog, ttk


#okay this is where global variables are supposed to go but
#i decided to just slap them in the class itself so now it's empty :<
#i'm gonna try to put a cute little cat here hold on

cat = """
 /\_/\
( °w° )
 )   (  )
(__(__)__)
"""

#okay back to business we're fixing the srt time format
#unrelated but this reminds me of like having to convert years to like
#seconds to solve stuff for physics class. anyway
def time_format(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

#then defining how to save the actual srt file
#the w is sending me bro is laughing. no thats overwrites existing file T_T
def save_srt(segments, path):
    with open(path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            start = time_format(seg["start"])
            end = time_format(seg["end"])
            text = seg["text"].strip()

            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(text + "\n\n")
            
#adding this guy in so fukcing late because i realized i need to bundle
#the damn whisper models into the app to make it completely offline

def resource_path(relative_path):
    base = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base, relative_path)

def load_bundled_models(model_name):
    model_dir = resource_path("models")
    return whisper.load_model(model_name, download_root=model_dir)

def get_ffmpeg_path():
    return os.path.join(os.path.abspath("."), "ffmpeg/bin", "ffmpeg.exe")

os.environ["PATH"] += os.pathsep + os.path.join(os.path.abspath("."), "ffmpeg")

if getattr(sys, 'frozen', False):    
    base_path = os.path.dirname(sys.executable)
    site_packages_path = os.path.join(sys._MEIPASS, 'Lib', 'site-packages')
    sys.path.append(site_packages_path)
    os.environ["PATH"] += os.pathsep + sys._MEIPASS
else:
    base_path = os.path.abspath(".")

class Main:
    def __init__(self, root):
        #initialization of the main process script
        self.root = root
        self.root.iconbitmap(resource_path("logo_256.ico"))
        self.root.title("SERAsubs")
        self.root.geometry("315x512")
        
        #initalizing input output variables in this part yeees i finally get 
        #to do it wooooo
        self.input_path = None
        self.output_path = None

        self.lang = tk.StringVar(value="Japanese")
        self.model = tk.StringVar(value="Balanced (Recommended)")
        self.burn = tk.BooleanVar()
        
        tk.Label(root, text="SERAsubs",
                 font=("Arial", 13, "bold")).pack(pady=10)

        #you select da boi here
        tk.Button(root, text="Select file",
                  command=self.select_input).pack()
        self.input_label = tk.Label(root, text="File not selected")
        self.input_label.pack(pady=5)
        
        #and this is where the finished product goes out :333
        tk.Button(root, text="Select Output Folder",
                  command=self.select_output).pack()
        self.output_label = tk.Label(self.root, text="Output folder not selected")
        self.output_label.pack(pady=5)
        
        #okay like theres a lot of options for which languages to put right
        #but i'll leave it as just jp and en rn bc at least i speak both
        tk.Label(root, text="Language").pack()
        ttk.Combobox(
            root,
            textvariable=self.lang,
            values=["Japanese", "English"],
            state="readonly"
        ).pack()

        #decided to just take the 3 lowest ones im not adding the heavy ones
        tk.Label(root, text="Model").pack()
        ttk.Combobox(
            root,
            textvariable=self.model,
            values=[
                "Fastest (Lower accuracy)", 
                "Balanced (Recommended)", 
                "Slowest (Higher accuracy)"
                ],
        ).pack()
        

        #let it rip!!!!
        tk.Button(
            root,
            text="Start",
            command=self.process,
        ).pack(pady=12)
    
        #just so u know this is the part that got me struggling
        self.status = tk.Label(root, text="")
        self.status.pack(pady=5)        
        
    #okay we're gonna start with the actual processes now with that outta
    #defining da magic to make it happen
    #starting with selecting input
    def select_input(self):
        path = filedialog.askopenfilename(
            filetypes=[("Media", "*.mp4 *.mkv *.mov *.wav *.mp3")])
        if path:
            self.input_path = path
            self.input_label.config(text=os.path.basename(path))
            
    #this also became a headache for me for some reason like it wouldnt
    #select the damn folder dude
    def select_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_path = path
            self.output_label.config(text=path)
            
    #the last thing i fixed btw lmfao it wouldnt UPDATE DUDEEEE
    def set_status(self,text):
        self.status.config(text=text)
        self.root.update()
        
    #remnant of a freature i rly wanted to include but decided not to for now
    def normalize(self, path):
        return os.path.abspath(os.path.normpath(path))
        
    #okay main process NOW
    def process(self):
        self.set_status("Ready...")
        if not self.input_path:
            self.status.config(text="Select a video first.")
            return
        if not self.output_path:
            self.status.config(text="Select an output folder.")
            return
        
        threading.Thread(target=self.deeper_process, daemon=True).start()
        
    #just kidding this is the deeper process that was just setting the stage
    def deeper_process(self):
        os.makedirs(self.output_path, exist_ok=True)

        name = os.path.splitext(os.path.basename(self.input_path))[0]
        srt_path = os.path.join(self.output_path, f"{name}_subs.srt")

        choice = self.model.get()
        
        if "Fastest" in choice:
             model_name = "base"
        elif "Balanced" in choice:
             model_name = "small"
        else:
             model_name = "large-v3"

        self.set_status("Loading model...")
        model = load_bundled_models(model_name)
        
        self.set_status("Processing audio...")
        lang = self.lang.get()

        lang = self.lang.get()
        
        if lang == "Japanese":
            result = model.transcribe(self.input_path, language="ja")
        
        elif lang == "English":
            result = model.transcribe(self.input_path, language="en")
        
        else:
            result = model.transcribe(self.input_path)
            
        save_srt(result["segments"], srt_path)
        
        self.set_status("Writing subtitles...")
        
        #between these points there used to be an option to burn the subs
        #directly into the video but... 
        #decided to scrap it for now because that wasnt the main intended
        #function of this project anyway, just an extra more convenient step
        #I'll try to improve the code more and more to get there
        #but for now, it will be released just like this.
        #i hope whoever is reading this can feel my frustration and saddness
        #at not being able to implement something i really wanted the program to have
        #I will come back for this
        #Mark my words
        
        self.set_status("Completed!")

#aaaaand that's showtime :>
if __name__ == "__main__":
    root = tk.Tk()
    Main(root)
    root.mainloop()
    
#if you actually did peek into my code and got this far im honestly a lil
#happy ?? like awww you wanted to see it ?? you want meee pien pien 
#anyway if you did read this dm me rn or approach me on discord
#i would love to know what you think hehe if my code is a goddamn mess