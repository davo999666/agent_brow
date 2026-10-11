
import re
import queue
import tkinter as tk
import webbrowser
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText


class AgentPanel:
    def __init__(self, on_start, on_stop):
        self.root = tk.Tk()
        self.root.title("AI Browser Agent")
        self.root.geometry("480x850+100+100")
        self.root.minsize(360, 500)
        self.root.attributes("-topmost", True)

        self.on_start = on_start
        self.on_stop = on_stop
        self.events = queue.Queue()
        self.link_count = 0
        self.streaming = False

        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Website URL").pack(anchor="w")

        self.domain = ttk.Entry(frame)
        self.domain.pack(fill="x", pady=(5, 10))

        ttk.Label(frame, text="Agent Conversation").pack(anchor="w")

        self.chat = ScrolledText(
            frame,
            wrap="word",
            state="disabled",
            font=("Segoe UI", 10),
            bg="#171717",
            fg="#eeeeee",
            insertbackground="white",
            relief="flat",
            padx=12,
            pady=12,
        )
        self.chat.pack(fill="both", expand=True, pady=5)

        self.chat.tag_configure("user", foreground="#70a5ff", font=("Segoe UI", 10, "bold"))
        self.chat.tag_configure("agent", foreground="#80d4a5", font=("Segoe UI", 10, "bold"))
        self.chat.tag_configure("tool", foreground="#d6b87c")
        self.chat.tag_configure("error", foreground="#ff7777")

        ttk.Label(frame, text="Your Prompt").pack(anchor="w", pady=(10, 0))

        self.prompt = tk.Text( frame, height=4, wrap="word",  font=("Segoe UI", 10))
        self.prompt.pack(fill="x", pady=5)

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=8)

        self.start_button = ttk.Button( buttons,  text="Send / Start", command=self.start)
        self.start_button.pack(side="left", fill="x", expand=True, padx=(0, 5))

        ttk.Button( buttons, text="Stop", command=self.stop ).pack(side="left", fill="x", expand=True)

        self.status = tk.StringVar(value="Ready")
        ttk.Label( frame, textvariable=self.status ).pack(anchor="w", pady=(5, 0))

        self.root.after(50, self.process_events)

    def emit(self, kind, value=""):
        """Safe to call from the LangGraph worker thread."""
        self.events.put((kind, str(value)))

    def process_events(self):
        try:
            while True:
                kind, value = self.events.get_nowait()

                if kind == "token":
                    if not self.streaming:
                        self.write("\nAgent:\n", "agent")
                        self.streaming = True
                    self.write(value)

                elif kind == "message":
                    self.streaming = False
                    self.write(f"\n{value}\n")

                elif kind == "tool":
                    self.streaming = False
                    self.write(f"\nTool: {value}\n", "tool")

                elif kind == "result":
                    self.streaming = False
                    self.write(f"\nFinal result:\n{value}\n", "agent")
                    self.status.set("Completed")

                elif kind == "status":
                    self.status.set(value)
                    if value in ("Completed", "Stopped", "Error"):
                        self.streaming = False

                elif kind == "error":
                    self.streaming = False
                    self.write(f"\nError: {value}\n", "error")
                    self.status.set("Error")

        except queue.Empty:
            pass

        self.root.after(50, self.process_events)

    def write(self, text, tag=None):
        self.chat.configure(state="normal")

        start = self.chat.index("end-1c")

        if tag:
            self.chat.insert("end", text, tag)
        else:
            self.chat.insert("end", text)

        self.make_links(start, self.chat.index("end-1c"))

        self.chat.see("end")
        self.chat.configure(state="disabled")

    def make_links(self, start, end):
        content = self.chat.get(start, end)

        for match in re.finditer(r"https?://[^\s<>\"']+", content):
            url = match.group(0).rstrip(".,;!?)")
            if not url:
                continue

            self.link_count += 1
            tag = f"link_{self.link_count}"

            link_start = self.chat.index(f"{start}+{match.start()}c")
            link_end = self.chat.index(f"{link_start}+{len(url)}c")

            self.chat.tag_add(tag, link_start, link_end)
            self.chat.tag_configure( tag, foreground="#60a5fa", underline=True)
            self.chat.tag_bind(  tag,  "<Button-1>",  lambda event, link=url: webbrowser.open(link) )
            self.chat.tag_bind(  tag, "<Enter>", lambda event: self.chat.config(cursor="hand2") )
            self.chat.tag_bind( tag,  "<Leave>",  lambda event: self.chat.config(cursor=""))

    def start(self):
        domain = self.domain.get().strip()
        prompt = self.prompt.get("1.0", "end").strip()

        if not prompt:
            self.status.set("Enter a prompt")
            return

        self.write(f"\nYou:\n{prompt}\n", "user")
        self.prompt.delete("1.0", "end")
        self.status.set("Running...")

        self.on_start(domain, prompt)

    def stop(self):
        self.on_stop()
        self.status.set("Stop requested...")

    def run(self):
        self.root.mainloop()
