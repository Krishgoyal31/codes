import tkinter as tk
from pynput import keyboard
from tkinter import scrolledtext
from tkinter import messagebox
import threading
import google.generativeai as genai
import os
import pyperclip 
GEMINI_API_KEY = ""

if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
    print("WARNING: Gemini API Key not set. Please update the GEMINI_API_KEY variable in the code.")
    print("Or set it as an environment variable named GEMINI_API_KEY.")
    # You might want to disable Gemini functionality if the key is missing.

# Configure the generative AI model
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('models/gemini-1.5-flash-001') # Using 1.5 Flash as requested
    gemini_ready = True
except Exception as e:
    gemini_ready = False
    print(f"ERROR: Could not configure Gemini API. Please check your API key and internet connection: {e}")
    messagebox.showerror("Gemini API Error", f"Could not configure Gemini API. Please check your API key and internet connection.\nError: {e}")

class DisappearingChatbotGUI:
    def __init__(self, master):
        self.master = master
        master.title("Disappearing Gemini Chatbot")
        master.geometry("600x500")
        master.resizable(True, True)

        master.withdraw()

        # --- Chat Interface Elements ---

        # Button to get question from clipboard
        self.clipboard_button = tk.Button(master, text="Get Question from Clipboard",
                                          command=self.get_question_from_clipboard,
                                          font=("Arial", 12), bg="#4CAF50", fg="white",
                                          activebackground="#45a049", activeforeground="white",
                                          relief=tk.FLAT) # Flat look
        self.clipboard_button.pack(pady=15, padx=20, fill='x')


        self.conversation_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, state='disabled', font=("Arial", 11),
                                                            bg="#f0f0f0", fg="#333333", spacing2=5) # Added styling
        self.conversation_area.pack(pady=10, padx=10, expand=True, fill='both')

        self.status_label = tk.Label(master, text="Ready.", fg="gray", font=("Arial", 9))
        self.status_label.pack(pady=5, fill='x')

        # --- Control Buttons ---
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=(0, 10))

        self.clear_button = tk.Button(self.button_frame, text="Clear Chat", command=self.clear_conversation, font=("Arial", 10))
        self.clear_button.pack(side='left', padx=5)

        self.close_button = tk.Button(self.button_frame, text="Close App", command=master.quit, font=("Arial", 10))
        self.close_button.pack(side='left', padx=5)

        # Set up a global hotkey listener
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()

        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Check if Gemini is ready and update status
        if not gemini_ready:
            self.status_label.config(text="Gemini API not configured. Chatbot functionality limited.", fg="red")
            self.clipboard_button.config(state='disabled') # Disable button if API not ready
        else:
            self.status_label.config(text="Gemini API Ready. Copy text and click 'Get Question from Clipboard'!", fg="darkgreen")


    def get_question_from_clipboard(self):
        try:
            user_question = pyperclip.paste().strip()
            if not user_question:
                self.status_label.config(text="Clipboard is empty or contains no text.", fg="red")
                return

            self.display_message(f"You: {user_question}", "blue")

            # Disable button and show thinking status
            self.clipboard_button.config(state='disabled')
            self.clear_button.config(state='disabled') # Also disable clear during processing
            self.status_label.config(text="Bot is thinking...", fg="orange")

            # Start a new thread for the Gemini API call
            threading.Thread(target=self.get_gemini_response_threaded, args=(user_question,)).start()

        except pyperclip.PyperclipException as e:
            self.status_label.config(text=f"Error accessing clipboard: {e}. Please ensure you have a clipboard utility installed (e.g., xclip/xsel on Linux).", fg="red")
            messagebox.showerror("Clipboard Error", f"Could not access clipboard: {e}\n\nPlease ensure you have a clipboard utility installed (e.g., xclip or xsel on Linux, usually built-in on Windows/macOS).")
        except Exception as e:
            self.status_label.config(text=f"An unexpected error occurred: {e}", fg="red")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")


    def get_gemini_response_threaded(self, user_question):
        """Runs the Gemini API call in a separate thread."""
        try:
            if not gemini_ready:
                bot_response = "Error: Gemini API not configured. Cannot answer."
            else:
                response = model.generate_content(user_question)
                bot_response = response.text
        except Exception as e:
            print(f"Gemini API Error: {e}")
            bot_response = f"I'm sorry, I encountered an error communicating with Gemini. Please try again. ({e})"
        finally:
            # Schedule the update back on the main Tkinter thread
            self.master.after(0, self.update_gui_after_response, bot_response)

    def update_gui_after_response(self, bot_response):
        """Updates the GUI with the bot's response and re-enables input."""
        self.display_message(f"Bot: {bot_response}", "green")

        # Re-enable button and reset status
        self.clipboard_button.config(state='normal')
        self.clear_button.config(state='normal')
        self.status_label.config(text="Ready. Copy text and click 'Get Question from Clipboard'!", fg="gray")

    def display_message(self, message, color="black"):
        self.conversation_area.config(state='normal')
        self.conversation_area.insert(tk.END, message + "\n\n") # Add extra newline for spacing
        self.conversation_area.tag_config("blue", foreground="#00008B") # Darker blue
        self.conversation_area.tag_config("green", foreground="#228B22") # Forest green
        self.conversation_area.tag_config("red", foreground="red")
        self.conversation_area.tag_config("orange", foreground="orange")


        if "You:" in message:
            self.conversation_area.tag_add("blue", "end-2c linestart", "end-2c lineend") # Adjust for extra newline
        elif "Bot:" in message:
            self.conversation_area.tag_add("green", "end-2c linestart", "end-2c lineend") # Adjust for extra newline

        self.conversation_area.see(tk.END)
        self.conversation_area.config(state='disabled')

    def clear_conversation(self):
        self.conversation_area.config(state='normal')
        self.conversation_area.delete(1.0, tk.END)
        self.conversation_area.config(state='disabled')
        self.status_label.config(text="Chat cleared. Copy text and click 'Get Question from Clipboard'!", fg="gray")


    def on_key_press(self, key):
        try:
            if key == keyboard.KeyCode.from_char('h'):
                if self.master.winfo_exists():
                    if self.master.state() == 'withdrawn':
                        self.master.deiconify()
                        self.master.lift()
                        self.master.focus_force()
                        # No question_entry to focus on now
                    else:
                        self.master.withdraw()
        except AttributeError:
            pass

    def on_closing(self):
        self.listener.stop()
        self.master.destroy()

def main():
    root = tk.Tk()
    app = DisappearingChatbotGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
