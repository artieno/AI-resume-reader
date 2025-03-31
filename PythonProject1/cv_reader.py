import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from tkinter.font import Font
import PyPDF2
import docx
import re
import spacy
import time
import random
from spellchecker import SpellChecker

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    messagebox.showerror("Error", "spaCy model 'en_core_web_sm' not found. Please install it.")
    exit()

# Initialize SpellChecker
spell = SpellChecker()

# Color scheme
BG_COLOR = "#f0f2f5"
PRIMARY_COLOR = "#1877f2"
SECONDARY_COLOR = "#42b72a"
TEXT_COLOR = "#1c1e21"
ERROR_COLOR = "#ff4444"
SUCCESS_COLOR = "#00C851"

# Fonts
TITLE_FONT = ("Segoe UI", 20, "bold")
HEADER_FONT = ("Segoe UI", 14, "bold")
BODY_FONT = ("Segoe UI", 12)
BUTTON_FONT = ("Segoe UI", 12, "bold")


# Text extraction functions
def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        return ''.join(page.extract_text() for page in reader.pages)


def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return '\n'.join(para.text for para in doc.paragraphs)


# Analysis functions
def check_sections(text):
    sections = ["Education", "Experience", "Skills", "Projects"]
    return [section for section in sections if re.search(fr'\b{section}\b', text, re.IGNORECASE)]


def analyze_spelling(text):
    return [f"Misspelled word: {word}" for word in spell.unknown(text.split())]


def analyze_grammar(text):
    doc = nlp(text)
    return [f"Passive voice detected: {sent.text}" for sent in doc.sents
            if ("was" in sent.text or "were" in sent.text) and sent.text.strip()]


def rate_cv(text):
    score = 10
    sections = check_sections(text)
    if len(sections) < 3: score -= 3
    if analyze_spelling(text): score -= 2
    if analyze_grammar(text): score -= 2
    return max(1, min(10, score))


def get_fun_rating(score):
    ratings = {
        10: ("CV Masterpiece! 🎨", "#4CAF50"),
        (7, 9): ("Almost Perfect! ✨", "#8BC34A"),
        (4, 6): ("Good, but needs work! 🛠", "#FFC107"),
        (1, 3): ("Let's start from scratch! 🚀", "#F44336")
    }
    for k, v in ratings.items():
        if (isinstance(k, tuple) and k[0] <= score <= k[1]) or score == k:
            return v
    return ("", "")


def generate_feedback(text):
    feedback = []
    missing = set(["Education", "Experience", "Skills", "Projects"]) - set(check_sections(text))
    if missing: feedback.append(f"Missing sections: {', '.join(missing)}")
    if analyze_spelling(text): feedback.append("Spelling issues detected")
    if analyze_grammar(text): feedback.append("Grammar issues detected")
    return "\n".join(feedback) or "Your CV looks great! No major issues found."


def get_random_tip():
    tips = [
        "Use action verbs like 'managed', 'developed', and 'achieved'",
        "Keep your CV to 1-2 pages maximum",
        "Tailor your CV to each job description",
        "Quantify achievements with numbers where possible",
        "Use a clean, professional font like Arial or Calibri"
    ]
    return random.choice(tips)


def save_score(name, score):
    with open("leaderboard.txt", "a") as file:
        file.write(f"{name}: {score}\n")


def show_leaderboard():
    try:
        with open("leaderboard.txt", "r") as file:
            scores = file.readlines()
        leaderboard = "🏆 Leaderboard 🏆\n\n" + "".join(scores)
        messagebox.showinfo("Leaderboard", leaderboard)
    except FileNotFoundError:
        messagebox.showinfo("Leaderboard", "No scores yet!")


# Modern UI Components
class RoundedButton(tk.Canvas):
    def __init__(self, master=None, text="", command=None, radius=25, **kwargs):
        super().__init__(master, **kwargs)
        self.command = command
        self.radius = radius
        self.text = text
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.draw_button()

    def draw_button(self, color=PRIMARY_COLOR):
        self.delete("all")
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()

        # Draw rounded rectangle
        self.create_round_rect(0, 0, width, height, radius=self.radius, fill=color)
        self.create_text(width / 2, height / 2, text=self.text, fill="white", font=BUTTON_FONT)

    def create_round_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1 + radius, y1, x1 + radius, y1,
                  x2 - radius, y1, x2 - radius, y1,
                  x2, y1, x2, y1 + radius,
                  x2, y1 + radius, x2, y2 - radius,
                  x2, y2 - radius, x2, y2,
                  x2 - radius, y2, x2 - radius, y2,
                  x1 + radius, y2, x1 + radius, y2,
                  x1, y2, x1, y2 - radius,
                  x1, y2 - radius, x1, y1 + radius,
                  x1, y1 + radius, x1, y1,
                  x1 + radius, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def _on_click(self, event):
        if self.command:
            self.command()

    def _on_enter(self, event):
        self.draw_button(color="#166fe5")  # Darker shade on hover

    def _on_leave(self, event):
        self.draw_button()


# Main Application
class CVApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CV Rating AI 🤖")
        self.root.geometry("600x450")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)

        self.setup_ui()

    def setup_ui(self):
        # Header Frame
        header_frame = tk.Frame(self.root, bg=BG_COLOR)
        header_frame.pack(pady=20)

        self.title_label = tk.Label(
            header_frame,
            text="CV Rating AI",
            font=TITLE_FONT,
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        self.title_label.pack()

        self.subtitle_label = tk.Label(
            header_frame,
            text="Get instant feedback on your resume",
            font=BODY_FONT,
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        self.subtitle_label.pack(pady=5)

        # Main Content Frame
        content_frame = tk.Frame(self.root, bg=BG_COLOR)
        content_frame.pack(pady=10)

        # Upload Button
        self.upload_btn = RoundedButton(
            content_frame,
            text="Upload CV",
            command=self.upload_file,
            width=200,
            height=50,
            bg=BG_COLOR,
            highlightthickness=0
        )
        self.upload_btn.pack(pady=20)

        # Progress Bar
        self.progress = ttk.Progressbar(
            content_frame,
            orient="horizontal",
            length=300,
            mode="indeterminate"
        )

        # Timer Section
        timer_frame = tk.Frame(content_frame, bg=BG_COLOR)
        timer_frame.pack(pady=10)

        self.timer_label = tk.Label(
            timer_frame,
            text="⏱ Time left: 05:00",
            font=BODY_FONT,
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        self.timer_label.pack(side=tk.LEFT, padx=10)

        self.timer_btn = tk.Button(
            timer_frame,
            text="Start Timer",
            command=self.start_timer,
            font=BUTTON_FONT,
            bg=SECONDARY_COLOR,
            fg="white",
            relief=tk.FLAT,
            activebackground="#36a420",
            activeforeground="white"
        )
        self.timer_btn.pack(side=tk.LEFT)

        # Footer
        footer_frame = tk.Frame(self.root, bg=BG_COLOR)
        footer_frame.pack(pady=10)

        self.version_label = tk.Label(
            footer_frame,
            text="v1.0 • Made with ❤",
            font=("Segoe UI", 10),
            bg=BG_COLOR,
            fg="#65676b"
        )
        self.version_label.pack()

    def upload_file(self):
        file_path = filedialog.askopenfilename(
            title="Select your CV",
            filetypes=[("PDF Files", "*.pdf"), ("Word Documents", "*.docx")]
        )

        if not file_path:
            return

        self.progress.pack(pady=10)
        self.progress.start(10)
        self.root.update_idletasks()

        try:
            if file_path.endswith('.pdf'):
                text = extract_text_from_pdf(file_path)
            elif file_path.endswith('.docx'):
                text = extract_text_from_docx(file_path)
            else:
                messagebox.showerror("Error", "Please upload a PDF or Word document")
                return

            score = rate_cv(text)
            rating, color = get_fun_rating(score)
            feedback = generate_feedback(text)
            tip = get_random_tip()

            # Show results in a custom dialog
            result_window = tk.Toplevel(self.root)
            result_window.title("CV Rating Results")
            result_window.geometry("500x400")
            result_window.resizable(False, False)
            result_window.configure(bg=BG_COLOR)

            # Score display
            score_frame = tk.Frame(result_window, bg=color)
            score_frame.pack(fill=tk.X, padx=20, pady=20)

            tk.Label(
                score_frame,
                text=f"Your CV Score: {score}/10",
                font=("Segoe UI", 24, "bold"),
                bg=color,
                fg="white"
            ).pack(pady=10)

            tk.Label(
                score_frame,
                text=rating,
                font=("Segoe UI", 16),
                bg=color,
                fg="white"
            ).pack(pady=5)

            # Feedback section
            feedback_frame = tk.Frame(result_window, bg=BG_COLOR)
            feedback_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

            tk.Label(
                feedback_frame,
                text="📝 Feedback",
                font=HEADER_FONT,
                bg=BG_COLOR,
                fg=TEXT_COLOR
            ).pack(anchor=tk.W)

            feedback_text = tk.Text(
                feedback_frame,
                height=8,
                wrap=tk.WORD,
                font=BODY_FONT,
                bg="white",
                relief=tk.FLAT,
                padx=10,
                pady=10
            )
            feedback_text.pack(fill=tk.BOTH, pady=5)
            feedback_text.insert(tk.END, feedback)
            feedback_text.config(state=tk.DISABLED)

            # Tip section
            tip_frame = tk.Frame(result_window, bg=BG_COLOR)
            tip_frame.pack(fill=tk.X, padx=20, pady=10)

            tk.Label(
                tip_frame,
                text=f"💡 Tip: {tip}",
                font=BODY_FONT,
                bg=BG_COLOR,
                fg=TEXT_COLOR
            ).pack(anchor=tk.W)

            # Save score
            name = simpledialog.askstring("Save Score", "Enter your name to save your score:")
            if name:
                save_score(name, score)
                show_leaderboard()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.progress.stop()
            self.progress.pack_forget()

    def start_timer(self):
        for i in range(300, -1, -1):
            mins, secs = divmod(i, 60)
            self.timer_label.config(text=f"⏱ Time left: {mins:02}:{secs:02}")
            self.root.update()
            time.sleep(1)
        messagebox.showinfo("Time's Up!", "⏰ Time's up! How did you do?")


# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = CVApp(root)
    root.mainloop()