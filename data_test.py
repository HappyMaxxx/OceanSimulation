import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import ast

class FunctionGrapher:
    def __init__(self, root):
        self.root = root
        self.root.title("Function Grapher")
        self.root.geometry("1000x550")
        
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.pack(fill="both", expand=True)
        
        self.left_frame = ttk.Frame(self.top_frame)
        self.left_frame.pack(side="left", fill="y", padx=(0, 10))
        
        ttk.Label(self.left_frame, text="Function (lambda x,...):").pack(pady=(0, 5))
        self.formula_entry = tk.Text(self.left_frame, height=2, width=40)
        self.formula_entry.pack()
        self.formula_entry.bind('<KeyRelease>', self.update_graph)
        
        self.limits_frame = ttk.Frame(self.left_frame)
        self.limits_frame.pack(pady=10)
        
        ttk.Label(self.limits_frame, text="X min:").grid(row=0, column=0, padx=5)
        self.xmin_entry = ttk.Entry(self.limits_frame, width=10)
        self.xmin_entry.grid(row=0, column=1)
        self.xmin_entry.insert(0, "0.0")
        self.xmin_entry.bind('<KeyRelease>', self.update_graph)
        
        ttk.Label(self.limits_frame, text="X max:").grid(row=1, column=0, padx=5)
        self.xmax_entry = ttk.Entry(self.limits_frame, width=10)
        self.xmax_entry.grid(row=1, column=1)
        self.xmax_entry.insert(0, "1.0")
        self.xmax_entry.bind('<KeyRelease>', self.update_graph)
        
        ttk.Label(self.limits_frame, text="Step:").grid(row=2, column=0, padx=5)
        self.step_entry = ttk.Entry(self.limits_frame, width=10)
        self.step_entry.grid(row=2, column=1)
        self.step_entry.insert(0, "0.1")
        self.step_entry.bind('<KeyRelease>', self.update_graph)

        ttk.Label(self.limits_frame, text="X label:").grid(row=3, column=0, padx=5)
        self.xlabel_entry = ttk.Entry(self.limits_frame, width=15)
        self.xlabel_entry.grid(row=3, column=1)
        self.xlabel_entry.insert(0, "x") 
        self.xlabel_entry.bind('<KeyRelease>', self.update_graph)
        
        ttk.Label(self.limits_frame, text="Y label:").grid(row=4, column=0, padx=5)
        self.ylabel_entry = ttk.Entry(self.limits_frame, width=15)
        self.ylabel_entry.grid(row=4, column=1)
        self.ylabel_entry.insert(0, "f(x)")
        self.ylabel_entry.bind('<KeyRelease>', self.update_graph)
        
        self.error_label = ttk.Label(self.left_frame, text="", foreground="red")
        self.error_label.pack(pady=5)
        
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.top_frame)
        self.canvas.get_tk_widget().pack(side="right", fill="both", expand=True)
        
        self.bottom_frame = ttk.Frame(self.main_frame)
        self.bottom_frame.pack(fill="x", pady=(30, 0))
        
        self.table_canvas = tk.Canvas(self.bottom_frame)
        self.table_scrollbar = ttk.Scrollbar(self.bottom_frame, orient="horizontal", command=self.table_canvas.xview)
        self.table_canvas.configure(xscrollcommand=self.table_scrollbar.set)
        
        self.table_scrollbar.pack(side="bottom", fill="x")
        self.table_canvas.pack(side="top", fill="x", expand=True)
        
        self.table_frame = ttk.Frame(self.table_canvas)
        self.table_canvas.create_window((0, 0), window=self.table_frame, anchor="nw")
        
        self.update_graph()

    def get_variables(self, lambda_str):
        try:
            lambda_str = lambda_str.strip()
            if not lambda_str:
                return ['x']
            if not lambda_str.startswith('lambda'):
                lambda_str = f"lambda x: {lambda_str}"
            tree = ast.parse(lambda_str)
            if isinstance(tree.body[0], ast.Lambda):
                vars = [arg.arg for arg in tree.body[0].args.args]
                return vars if vars else ['x']
            return ['x']
        except Exception as e:
            self.error_label.config(text=f"Parse error: {str(e)}")
            return ['x']

    def update_graph(self, event=None):
        self.ax.clear()
        formula = self.formula_entry.get("1.0", tk.END).strip()
        
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        
        try:
            if not formula:
                self.error_label.config(text="Enter a formula")
                self.ax.set_xlabel(self.xlabel_entry.get())
                self.ax.set_ylabel(self.ylabel_entry.get())
                self.ax.grid(True)
                self.canvas.draw()
                self.update_table([], [])
                return
            
            if not formula.startswith('lambda'):
                formula = f"lambda x: {formula}"
            
            variables = self.get_variables(formula)
            if not variables:
                raise ValueError("No variables detected")
            
            xmin = float(self.xmin_entry.get())
            step = float(self.step_entry.get())
            xmax = float(self.xmax_entry.get()) + step
            
            if xmin >= xmax:
                raise ValueError("X min must be less than X max")
            if step <= 0:
                raise ValueError("Step must be positive")
            if step > (xmax - xmin):
                raise ValueError("Step must be smaller than range")
            
            func = eval(formula, {"np": np, "x": None})
            x = np.arange(xmin, xmax, step)
            y = [func(x_val) for x_val in x]
            
            self.ax.plot(x, y)
            self.ax.set_xlabel(self.xlabel_entry.get())
            self.ax.set_ylabel(self.ylabel_entry.get())
            self.ax.grid(True)
            self.error_label.config(text="")
            
            self.update_table(x, y)
            
        except Exception as e:
            self.error_label.config(text=f"Error: {str(e)}")
            self.update_table([], [])
        
        self.canvas.draw()

    def update_table(self, x_values, y_values):
        ttk.Label(self.table_frame, text="x", font=("bold")).grid(row=0, column=0, padx=5, pady=2)
        ttk.Label(self.table_frame, text="y", font=("bold")).grid(row=1, column=0, padx=5, pady=2)
        
        for i, (x, y) in enumerate(zip(x_values, y_values)):
            ttk.Label(self.table_frame, text=f"{x:.3f}").grid(row=0, column=i+1, padx=5, pady=2)
            ttk.Label(self.table_frame, text=f"{y:.3f}").grid(row=1, column=i+1, padx=5, pady=2)
        
        self.table_frame.update_idletasks()
        self.table_canvas.config(scrollregion=self.table_canvas.bbox("all"))

if __name__ == "__main__":
    root = tk.Tk()
    app = FunctionGrapher(root)
    root.mainloop()