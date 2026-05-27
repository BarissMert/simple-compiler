import tkinter as tk
from ui import CompilerUI

def main():
    root = tk.Tk()
    app = CompilerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()