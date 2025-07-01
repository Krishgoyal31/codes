import tkinter as tk
from tkinter import messagebox

class Calculator:
    def __init__(self, master):
        self.master = master
        master.title("Simple Calculator")
        master.geometry("300x400") # Set initial window size
        master.resizable(False, False) # Prevent resizing for simplicity

        # Configure grid weights to make cells expand proportionally
        for i in range(5): # 5 rows for buttons
            master.grid_rowconfigure(i, weight=1)
        for i in range(4): # 4 columns for buttons
            master.grid_columnconfigure(i, weight=1)

        # --- Display Entry ---
        self.equation = tk.StringVar()
        self.entry = tk.Entry(master, textvariable=self.equation, font=('Arial', 24), bd=10, insertwidth=4, width=14, borderwidth=4, justify='right')
        self.entry.grid(row=0, column=0, columnspan=4, pady=10, padx=10, sticky="nsew")
        self.entry.insert(0, "") # Initialize with empty string

        # --- Buttons ---
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+'
        ]
        row_val = 1
        col_val = 0

        for button_text in buttons:
            if button_text == '=':
                tk.Button(master, text=button_text, font=('Arial', 18, 'bold'),
                          command=self.evaluate_expression,
                          bg='#4CAF50', fg='white', relief=tk.RAISED, bd=5).grid(row=row_val, column=col_val, sticky="nsew", padx=5, pady=5)
            else:
                tk.Button(master, text=button_text, font=('Arial', 18),
                          command=lambda b=button_text: self.button_click(b),
                          bg='#e0e0e0', fg='black', relief=tk.RAISED, bd=5).grid(row=row_val, column=col_val, sticky="nsew", padx=5, pady=5)

            col_val += 1
            if col_val > 3:
                col_val = 0
                row_val += 1

        # --- Clear Button ---
        tk.Button(master, text='C', font=('Arial', 18, 'bold'),
                  command=self.clear_expression,
                  bg='#f44336', fg='white', relief=tk.RAISED, bd=5).grid(row=row_val, column=0, columnspan=4, sticky="nsew", padx=5, pady=5)


    def button_click(self, char):
        """Appends the clicked character to the display."""
        current_text = self.equation.get()
        self.equation.set(current_text + str(char))

    def clear_expression(self):
        """Clears the display."""
        self.equation.set("")

    def evaluate_expression(self):
        """Evaluates the expression in the display."""
        try:
            # Get the expression from the entry widget
            expression = self.equation.get()
            # Evaluate the expression
            result = str(eval(expression))
            # Set the result back to the entry widget
            self.equation.set(result)
        except ZeroDivisionError:
            messagebox.showerror("Error", "Cannot divide by zero!")
            self.equation.set("")
        except SyntaxError:
            messagebox.showerror("Error", "Invalid expression!")
            self.equation.set("")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.equation.set("")

# --- Main Application Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    my_calculator = Calculator(root)
    root.mainloop()
