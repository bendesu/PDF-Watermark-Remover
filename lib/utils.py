import tkinter as tk

def get_screen_size():
  tk_root = tk.Tk()
  screen_width = tk_root.winfo_screenwidth()
  screen_height = tk_root.winfo_screenheight()
  tk_root.destroy()
  return (screen_width, screen_height)

def get_central_pos(window_size, screen_size):
  screen_width, screen_height = screen_size
  width, height = window_size
  pos_x, pos_y = round((screen_width - width) / 2), round((screen_height - height) / 2)
  return (pos_x, pos_y)