import speech_recognition as sr
import os
import webbrowser
import datetime
import random
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk # Import ttk for themed widgets
import threading
import time
import subprocess
import requests # For making HTTP requests to Ollama API
import json     # For working with JSON data for Ollama API

class VenomAssistantGUI:
    def __init__(self, master):
        self.master = master
        master.title("VENOM A.I. Assistant")
        master.geometry("800x720")
        master.resizable(True, True)
        master.configure(bg='#000000') # Pure black background

        # --- Ollama Configuration ---
        self.ollama_api_url = "http://localhost:11434/api/chat"
        self.ollama_model_name = "llama3.2" # Ensure this matches your pulled model
        self.ollama_chat_history = []

        # --- Theme Colors (Deep Black and Cyberpunk Green/Red Accents) ---
        self.bg_pure_black = '#000000'         # Absolute black
        self.bg_dark_panel = '#0a0a0a'         # Very dark gray for panels/text areas
        self.fg_light = '#f0f0f0'             # Near-white for general text
        self.accent_cyber_green = '#00ff41'    # Neon/Cyberpunk Green for primary actions
        self.accent_glow_green = '#39ff14'     # Slightly softer green for hover/active
        self.venom_cyber_red = '#ff073a'       # Neon/Cyberpunk Red for Venom's responses
        self.info_cyber_blue = '#00aeff'       # Neon/Cyberpunk Blue for info messages
        self.button_normal_black = '#1c1c1c'   # Dark button background
        self.button_hover_black = '#2c2c2c'    # Lighter button hover
        self.border_cyber_gray = '#333333'     # Subtle dark border

        # Apply the black theme to the root window (Tkinter palette might not apply to ttk widgets)
        self.master.tk_setPalette(background=self.bg_pure_black, foreground=self.fg_light,
                                  activeBackground=self.button_hover_black, activeForeground=self.fg_light)

        self.is_listening = False
        self.listening_thread = None
        self.say_process = None

        # --- Tkinter.ttk Style Configuration ---
        self.style = ttk.Style()
        # Choose a theme that respects custom styling more reliably on macOS
        # 'clam' and 'alt' are often good choices for custom dark themes.
        self.style.theme_use('clam')

        button_font = ("Consolas", 11, "bold")
        button_padding = 10 # Control vertical padding via style

        # --- Define Button Styles ---
        # Base style for all buttons to inherit common properties
        self.style.configure('TButton',
                             font=button_font,
                             relief='flat',
                             borderless=True, # Helps to remove macOS native button look
                             focusthickness=0, # Removes the focus outline
                             padding=[20, button_padding]) # [horizontal_padding, vertical_padding]

        # Style for the Green "START LISTENING" button
        self.style.configure('Green.TButton',
                             background=self.accent_cyber_green,
                             foreground=self.bg_pure_black) # Text color should be black
        self.style.map('Green.TButton',
                       background=[('active', self.accent_glow_green),
                                   ('pressed', self.accent_glow_green)],
                       foreground=[('active', self.bg_pure_black),
                                   ('pressed', self.bg_pure_black)])

        # Style for the Red "STOP LISTENING" and "CLOSE" buttons
        self.style.configure('Red.TButton',
                             background=self.venom_cyber_red,
                             foreground=self.fg_light) # Text color should be light
        self.style.map('Red.TButton',
                       background=[('active', '#cc002c'),
                                   ('pressed', '#cc002c')],
                       foreground=[('active', self.fg_light),
                                   ('pressed', self.fg_light)])

        # Style for the Orange "STOP SPEAKING" button
        self.style.configure('Orange.TButton',
                             background='#ff8800',
                             foreground=self.fg_light)
        self.style.map('Orange.TButton',
                       background=[('active', '#ffaa44'),
                                   ('pressed', '#ffaa44')],
                       foreground=[('active', self.fg_light),
                                   ('pressed', self.fg_light)])

        # Style for the Dark "CLEAR CHAT" button
        self.style.configure('Dark.TButton',
                             background=self.button_normal_black,
                             foreground=self.fg_light)
        self.style.map('Dark.TButton',
                       background=[('active', self.button_hover_black),
                                   ('pressed', self.button_hover_black)],
                       foreground=[('active', self.fg_light),
                                   ('pressed', self.fg_light)])

        # Style for the Blue "SEND" button
        self.style.configure('Blue.TButton',
                             background=self.info_cyber_blue,
                             foreground=self.fg_light)
        self.style.map('Blue.TButton',
                       background=[('active', '#00c0ff'),
                                   ('pressed', '#00c0ff')],
                       foreground=[('active', self.fg_light),
                                   ('pressed', self.fg_light)])

        # --- Header ---
        self.header_frame = tk.Frame(master, bg=self.bg_dark_panel, relief=tk.FLAT, bd=0)
        self.header_frame.pack(fill=tk.X, pady=(0, 10))

        self.title_label = tk.Label(self.header_frame, text="VENOM A.I. Assistant",
                                    font=("Orbitron", 18, "bold"), fg=self.fg_light, bg=self.bg_dark_panel)
        self.title_label.pack(side=tk.LEFT, padx=30, pady=10)

        # --- Main Content Frame ---
        self.main_frame = tk.Frame(master, bg=self.bg_pure_black, padx=20, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.status_label = tk.Label(self.main_frame, text=f"Status: Initializing...",
                                      font=("Consolas", 12), fg=self.info_cyber_blue, bg=self.bg_pure_black)
        self.status_label.pack(pady=(0, 10), anchor=tk.W)

        # --- Output Text Box ---
        self.output_text = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, height=18,
                                                     font=("Consolas", 11),
                                                     bg=self.bg_dark_panel, # Explicitly set dark background
                                                     fg=self.fg_light,     # Explicitly set light foreground
                                                     insertbackground=self.accent_cyber_green, # Cursor color
                                                     selectbackground=self.button_hover_black, # Selection highlight color
                                                     relief=tk.SOLID, bd=1, highlightbackground=self.border_cyber_gray, highlightcolor=self.accent_cyber_green)
        self.output_text.pack(pady=10, padx=0, fill=tk.BOTH, expand=True)
        self.output_text.tag_config('user', foreground=self.accent_cyber_green)
        self.output_text.tag_config('venom', foreground=self.venom_cyber_red)
        self.output_text.tag_config('info', foreground=self.info_cyber_blue)

        # Frame for control buttons
        self.voice_control_frame = tk.Frame(self.main_frame, bg=self.bg_pure_black)
        self.voice_control_frame.pack(pady=10)

        # --- Buttons (now using ttk.Button with custom styles) ---
        self.start_button = ttk.Button(self.voice_control_frame, text="START LISTENING",
                                      command=self.start_listening_gui, style='Green.TButton')
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(self.voice_control_frame, text="STOP LISTENING",
                                     command=self.stop_listening_gui, style='Red.TButton', state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.stop_speaking_button = ttk.Button(self.voice_control_frame, text="STOP SPEAKING",
                                               command=self.stop_speaking_gui, style='Orange.TButton', state=tk.DISABLED)
        self.stop_speaking_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = ttk.Button(self.voice_control_frame, text="CLEAR CHAT",
                                       command=self.clear_output, style='Dark.TButton')
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.close_button = ttk.Button(self.voice_control_frame, text="CLOSE",
                                       command=self.on_closing, style='Red.TButton')
        self.close_button.pack(side=tk.LEFT, padx=5)

        # --- Text Input Elements ---
        self.input_frame = tk.Frame(self.main_frame, bg=self.bg_pure_black)
        self.input_frame.pack(pady=(10, 20), fill=tk.X)

        self.input_entry = tk.Entry(self.input_frame, font=("Consolas", 12),
                                    bg=self.bg_dark_panel, # Explicitly set dark background
                                    fg=self.fg_light,     # Explicitly set light foreground
                                    insertbackground=self.accent_cyber_green, # Cursor color
                                    relief=tk.SOLID, bd=1,
                                    highlightthickness=1, highlightbackground=self.border_cyber_gray, highlightcolor=self.accent_cyber_green)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.input_entry.bind("<Return>", self.process_typed_command_event)

        self.send_button = ttk.Button(self.input_frame, text="SEND",
                                     command=self.process_typed_command, style='Blue.TButton')
        self.send_button.pack(side=tk.RIGHT)

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Initial greeting with status update
        self.master.after(100, lambda: self.status_label.config(text=f"Status: Ready (Model: {self.ollama_model_name})", fg=self.info_cyber_blue))
        self.master.after(500, lambda: self.say(f"VENOM A.I. activated, powered by {self.ollama_model_name}. How can I assist you today?"))

    def display_message(self, message, tag='info'):
        self.output_text.insert(tk.END, message + "\n", tag)
        self.output_text.see(tk.END)

    def query_ollama(self, prompt):
        self.status_label.config(text="Status: Querying Ollama...", fg=self.info_cyber_blue)
        self.display_message("Sending prompt to Ollama...", 'info')
        try:
            self.ollama_chat_history.append({"role": "user", "content": prompt})

            headers = {'Content-Type': 'application/json'}
            payload = {
                "model": self.ollama_model_name,
                "messages": self.ollama_chat_history,
                "stream": False
            }

            response = requests.post(self.ollama_api_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()

            data = response.json()
            ollama_response_content = data.get("message", {}).get("content", "No response content.")

            self.ollama_chat_history.append({"role": "assistant", "content": ollama_response_content})

            self.display_message(f"Ollama Response:\n{ollama_response_content}", 'venom')
            self.say(ollama_response_content)

            if not os.path.exists("Ollama_Responses"):
                os.mkdir("Ollama_Responses")
            filename = f"Ollama_Responses/prompt-{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1, 1000)}.txt"
            with open(filename, "w") as f:
                f.write(f"Ollama response for prompt: {prompt} \n ******************************* \n\n{ollama_response_content}")

        except requests.exceptions.ConnectionError:
            error_message = "Error: Could not connect to Ollama. Is Ollama running and is the model loaded?"
            self.display_message(error_message, 'venom')
            self.say("I'm sorry, I couldn't connect to Ollama right now.")
            messagebox.showerror("Ollama Connection Error", error_message)
        except requests.exceptions.RequestException as e:
            error_message = f"Error during Ollama API call: {e}"
            self.display_message(error_message, 'venom')
            self.say("I'm sorry, there was an issue communicating with Ollama.")
            messagebox.showerror("Ollama API Error", error_message)
        except json.JSONDecodeError:
            error_message = "Error: Invalid JSON response from Ollama. Check Ollama server logs."
            self.display_message(error_message, 'venom')
            self.say("I received an unreadable response from Ollama.")
            messagebox.showerror("Ollama JSON Error", error_message)
        except Exception as e:
            error_message = f"An unexpected error occurred with Ollama: {e}"
            self.display_message(error_message, 'venom')
            self.say("An unexpected error occurred while processing your request with Ollama.")
            messagebox.showerror("Ollama Runtime Error", error_message)
        finally:
            self.status_label.config(text=f"Status: Ready (Model: {self.ollama_model_name})", fg=self.info_cyber_blue)
            self._check_say_process()

    def say(self, text):
        self.display_message(f"Speaking: {text}", 'info')
        self.stop_speaking_gui()
        try:
            self.say_process = subprocess.Popen(['say', text])
            self.stop_speaking_button.config(state=tk.NORMAL)
            self._check_say_process()
        except Exception as e:
            self.display_message(f"Error starting speech: {e}", 'venom')
            self.stop_speaking_button.config(state=tk.DISABLED)
            self.say_process = None

    def _check_say_process(self):
        if self.say_process and self.say_process.poll() is None:
            self.master.after(100, self._check_say_process)
        else:
            self.stop_speaking_button.config(state=tk.DISABLED)
            self.say_process = None

    def stop_speaking_gui(self):
        if self.say_process and self.say_process.poll() is None:
            self.say_process.terminate()
            time.sleep(0.1)
            if self.say_process.poll() is None:
                self.say_process.kill()
            self.display_message("Speech stopped.", 'info')
        self.stop_speaking_button.config(state=tk.DISABLED)
        self.say_process = None

    def takeCommand(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.status_label.config(text="Status: Listening...", fg=self.accent_cyber_green)
            self.display_message("Listening for command...", 'info')
            r.pause_threshold = 1
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source)

        try:
            self.status_label.config(text="Status: Recognizing...", fg=self.info_cyber_blue)
            self.display_message("Recognizing speech...", 'info')
            query = r.recognize_google(audio, language="en-in")
            self.display_message(f"User said: {query}", 'user')
            return query
        except sr.UnknownValueError:
            self.display_message("Could not understand audio", 'venom')
            return ""
        except sr.RequestError as e:
            error_message = f"Could not request results from Google Speech Recognition service; {e}"
            self.display_message(error_message, 'venom')
            messagebox.showerror("Speech Recognition Error", error_message)
            return ""
        finally:
            self.status_label.config(text=f"Status: Ready (Model: {self.ollama_model_name})", fg=self.info_cyber_blue)

    def process_command(self, query):
        if not query:
            return

        self.display_message(f"Processing command: {query}", 'info')
        found_command = False

        apps = {
            "safari": "Safari", "pages": "Pages", "numbers": "Numbers",
            "keynote": "Keynote", "mail": "Mail", "calendar": "Calendar",
            "notes": "Notes", "reminders": "Reminders", "messages": "Messages",
            "photos": "Photos", "music": "Music", "app store": "App Store",
            "system settings": "System Settings", "terminal": "Terminal",
            "activity monitor": "Activity Monitor", "chrome": "Google Chrome",
            "brave": "Brave Browser", "firefox": "Firefox", "vscode": "Visual Studio Code"
        }
        for app_keyword, app_name in apps.items():
            if f"open {app_keyword}" in query:
                os.system(f"open -a '{app_name}'")
                self.say(f"Opening {app_name}.")
                found_command = True
                break
        if found_command: return

        folders = {
            "downloads": os.path.expanduser("~/Downloads"),
            "documents": os.path.expanduser("~/Documents"),
            "desktop": os.path.expanduser("~/Desktop"),
            "applications": "/Applications",
            "pictures": os.path.expanduser("~/Pictures")
        }
        for folder_keyword, folder_path in folders.items():
            if f"open {folder_keyword} folder" in query or f"go to {folder_keyword}" in query:
                if os.path.exists(folder_path):
                    os.system(f'open "{folder_path}"')
                    self.say(f"Opening {folder_keyword} folder.")
                else:
                    self.say(f"Sorry, I can't find the {folder_keyword} folder.")
                found_command = True
                break
        if found_command: return

        if "increase volume" in query:
            subprocess.run(["osascript", "-e", "set volume output volume ((get volume settings)'s output volume + 10)"])
            self.say("Volume increased.")
            found_command = True
        elif "decrease volume" in query:
            subprocess.run(["osascript", "-e", "set volume output volume ((get volume settings)'s output volume - 10)"])
            self.say("Volume decreased.")
            found_command = True
        elif "set volume to" in query:
            try:
                volume_level = int(''.join(filter(str.isdigit, query)))
                if 0 <= volume_level <= 100:
                    subprocess.run(["osascript", "-e", f"set volume output volume {volume_level}"])
                    self.say(f"Volume set to {volume_level}.")
                else:
                    self.say("Please specify a volume level between 0 and 100.")
            except ValueError:
                self.say("Please tell me a valid volume level.")
            found_command = True
        elif "mute volume" in query or "unmute volume" in query or "toggle mute" in query:
            subprocess.run(["osascript", "-e", "set volume with output muted"])
            self.say("Volume toggled.")
            found_command = True
        if found_command: return

        elif "sleep computer" in query or "put computer to sleep" in query:
            self.say("Putting your computer to sleep.")
            os.system("pmset sleepnow")
            found_command = True
        elif "restart computer" in query:
            if messagebox.askyesno("Confirm Restart", "Are you sure you want to restart? This will close all open applications."):
                self.say("Restarting your computer now.")
                os.system("sudo shutdown -r now")
            else:
                self.say("Restart cancelled.")
            found_command = True
        elif "shutdown computer" in query:
            if messagebox.askyesno("Confirm Shutdown", "Are you sure you want to shut down? This will close all open applications."):
                self.say("Shutting down your computer now.")
                os.system("sudo shutdown -h now")
            else:
                self.say("Shutdown cancelled.")
            found_command = True
        if found_command: return

        elif "search for" in query:
            search_term = query.replace("search for", "").strip()
            if search_term:
                self.say(f"Searching for {search_term}.")
                self.display_message(f"Please manually open Spotlight (Cmd+Space) and type '{search_term}'.", 'info')
            else:
                self.say("What would you like me to search for?")
            found_command = True
        if found_command: return

        sites = [
            ["youtube", "https://www.youtube.com"],
            ["wikipedia", "https://www.wikipedia.com"],
            ["google", "https://www.google.com"],
            ["instagram", "https://www.instagram.com"],
            ["facebook", "https://www.facebook.com"],
            ["twitter", "https://www.twitter.com"],
            ["linkedin", "https://www.linkedin.com"],
            ["amazon", "https://www.amazon.in"]
        ]
        for site in sites:
            if f"open {site[0]}" in query:
                self.say(f"Opening {site[0]}")
                webbrowser.open(site[1])
                found_command = True
                break
        if found_command: return

        elif "play local music" in query:
            musicPath = os.path.expanduser("/Users/krishgoyal/Downloads/palpal.mp3") # *** IMPORTANT: Adjust this path! ***
            if os.path.exists(musicPath):
                os.system(f'open "{musicPath}"')
                self.say("Playing local music.")
            else:
                self.say("Sorry, I can't find the specified music file. Please check the path in the code.")
            found_command = True
        if found_command: return

        elif "the time" in query:
            strfTime = datetime.datetime.now().strftime("%I:%M %p")
            self.say(f"The time is {strfTime}")
            found_command = True
        if found_command: return

        if "venom" in query:
            conversation_query = query.replace("venom", "").strip()
            if conversation_query:
                self.query_ollama(prompt=conversation_query)
            else:
                self.say("Yes, how can I help you?")
            found_command = True
        if found_command: return

        elif "exit" in query or "quit" in query or "stop" in query or "bye bye" in query:
            self.say("Goodbye! Have a great day.")
            found_command = True
            self.stop_listening_gui()
            self.master.after(1000, self.master.destroy)
            return

        if not found_command:
            self.query_ollama(prompt=query)

    def listen_loop(self):
        while self.is_listening:
            query = self.takeCommand().lower()
            if query:
                threading.Thread(target=self.process_command, args=(query,), daemon=True).start()
            time.sleep(0.1)

    def start_listening_gui(self):
        if not self.is_listening:
            self.is_listening = True
            # When using ttk, configuration is done via style or directly on widget.
            # State change for ttk.Button is usually done with .state()
            self.start_button.state(['disabled']) # Disable the start button
            self.stop_button.state(['!disabled']) # Enable the stop button
            self.status_label.config(text="Status: Listening...", fg=self.accent_cyber_green)
            self.display_message("Starting listening thread...", 'info')
            self.listening_thread = threading.Thread(target=self.listen_loop, daemon=True)
            self.listening_thread.start()

    def stop_listening_gui(self):
        if self.is_listening:
            self.is_listening = False
            self.start_button.state(['!disabled']) # Enable the start button
            self.stop_button.state(['disabled']) # Disable the stop button
            self.status_label.config(text=f"Status: Ready (Model: {self.ollama_model_name})", fg=self.info_cyber_blue)
            self.display_message("Stopped listening.", 'info')

    def clear_output(self):
        self.output_text.delete(1.0, tk.END)
        self.ollama_chat_history = []
        self.display_message("Chat history cleared. Ready for a new conversation.", 'info')

    def process_typed_command(self):
        command = self.input_entry.get().strip()
        if command:
            self.display_message(f"Typed command: {command}", 'user')
            self.input_entry.delete(0, tk.END)
            threading.Thread(target=self.process_command, args=(command.lower(),), daemon=True).start()
        else:
            self.display_message("Please type a command.", 'info')

    def process_typed_command_event(self, event):
        self.process_typed_command()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit VENOM A.I.?"):
            self.is_listening = False
            self.stop_speaking_gui()
            if self.listening_thread and self.listening_thread.is_alive():
                self.display_message("Stopping background tasks...", 'info')
                # Give the thread a moment to finish, but don't block indefinitely
                self.listening_thread.join(timeout=1)
            self.master.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = VenomAssistantGUI(root)
    root.mainloop()
