import tkinter as tk
from tkinter import ttk, scrolledtext
import sys
import os
import webbrowser
import re
from io import StringIO
import contextlib

# --- allow importing from parent folder (where main.py is) ---
sys.path.append(os.path.abspath(".."))

from main import show_serious_events  # your existing function


def fetch_and_display(hours):
    """Fetch events and display them with clickable URLs."""
    text_box.config(state="normal")
    text_box.delete("1.0", tk.END)

    buffer = StringIO()
    with contextlib.redirect_stdout(buffer):
        show_serious_events(hours)

    text = buffer.getvalue()
    insert_with_links(text)
    text_box.config(state="disabled")


def insert_with_links(text):
    """
    Insert text into the text box and make URLs clickable.
    """
    pattern = r"(\/aktuellt\/[^\s]+)"
    last_end = 0

    for match in re.finditer(pattern, text):
        start, end = match.span()
        url = match.group(1)
        full_url = f"https://polisen.se{url}"

        # Insert text before the link
        text_box.insert(tk.END, text[last_end:start])

        # Insert clickable link
        tag_name = f"link_{start}"
        text_box.insert(tk.END, url, tag_name)
        text_box.tag_config(
            tag_name,
            foreground="blue",
            underline=True
        )
        text_box.tag_bind(tag_name, "<Button-1>", lambda e, url=full_url: webbrowser.open(url))

        last_end = end

    # Insert the rest of the text
    text_box.insert(tk.END, text[last_end:])


# --- GUI setup ---
root = tk.Tk()
root.title("Polisens Händelser")
root.geometry("900x700")
root.minsize(700, 500)

# --- Top frame for controls ---
control_frame = ttk.Frame(root)
control_frame.pack(fill="x", pady=10)

ttk.Label(control_frame, text="Visa händelser från:").pack(side="left", padx=(10, 5))

hours_var = tk.StringVar(value="3")
hours_dropdown = ttk.Combobox(
    control_frame, textvariable=hours_var, state="readonly",
    values=["3", "6", "12", "24", "Alla"]
)
hours_dropdown.pack(side="left")

ttk.Button(
    control_frame, text="Ladda Händelser",
    command=lambda: fetch_and_display(None if hours_var.get() == "Alla" else int(hours_var.get()))
).pack(side="left", padx=10)

# --- Scrollable text box ---
text_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", 11))
text_box.pack(fill="both", expand=True, padx=10, pady=10)

root.mainloop()
