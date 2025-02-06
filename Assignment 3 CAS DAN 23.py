#  GROUP CAS/DAN23
# ARYAN RAYAMAJHI [s385826]
# MEENU DEVI MEENU DEVI [s383485]
# RIWAJ ADHIKARI [s385933]
# SAKAR KHADKA [s385095]

import cv2
import tkinter as tk
from tkinter import filedialog, messagebox 
from PIL import Image, ImageTk
import numpy as np

root = tk.Tk()

def main_menu_task():
    print("YOUR WORK IS DONE..")

# Creating Main Menu
menu=tk.Menu(root)
root.config(menu=menu)

submenu=tk.Menu(menu)

menu.add_cascade(label="File",menu=submenu)

# Adding options to file
submenu.add_cascade(label="Open Nen File")
submenu.add_command(label="Share File",command=main_menu_task)
submenu.add_command(label="Print",command=main_menu_task)
submenu.add_command(label="Properties",command=main_menu_task)
submenu.add_command(label="Exit",command=exit)
submenu.add_separator()

helpmenu=tk.Menu(menu)
menu.add_cascade(label="Help",menu=helpmenu,command=main_menu_task)
helpmenu.add_command(label="Contact Us",command=main_menu_task)

class EnhancedImageProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("IMAGE EDITOR APP")
        self.root.geometry("1000x800")
        self.root.configure(bg="light green")

        # Image references
        self.original_image = None       # Full size original
        self.modified_image = None       # Cropped portion
        self.history = []               # For undo
        self.redo_stack = []

        # For cropping on original
        self.crop_mode = False
        self.rect_start = None
        self.rect_end = None
        self.crop_rect_id = None

        # Build the UI
        self.create_gui()
        self.add_shortcuts()

    def create_gui(self):
        # Main frame for application
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas
        canvas_frame = tk.Frame(frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        # Original canvas
        self.original_canvas = tk.Canvas(canvas_frame, width=500, height=400, bg="light gray")
        self.original_canvas.pack(side=tk.LEFT, padx=10, pady=10)

        # Modified canvas
        self.modified_canvas = tk.Canvas(canvas_frame, width=500, height=400, bg="light gray")
        self.modified_canvas.pack(side=tk.RIGHT, padx=10, pady=10)

        # Edit buttons for control
        control_frame = tk.Frame(frame, bg='dark grey', pady=10)
        control_frame.pack(fill=tk.X, side="top")

        load_image_button = tk.Button(frame, text="Load Image", command=self.load_image) # load image button
        load_image_button.pack(side=tk.LEFT, padx=10)

        save_image_button = tk.Button(frame, text="Save Image", command=self.save_image) # save image button
        save_image_button.pack(side=tk.LEFT, padx=10)

        undo_button = tk.Button(frame, text="Undo Changes", command=self.undo)  # undo changes button
        undo_button.pack(side=tk.LEFT, padx=10)

        redo_button = tk.Button(frame, text="Redo Changes", command=self.redo)  #redo changes button
        redo_button.pack(side=tk.LEFT, padx=10)

        crop_button = tk.Button(frame, text="Crop Image", command=self.toggle_crop_mode)  # crop mode button
        crop_button.pack(side=tk.LEFT, padx=10)

        gray_button = tk.Button(frame, text="Grayscale Image", command=self.apply_grayscale)  # apply grayscale button
        gray_button.pack(side=tk.LEFT, padx=10)

        rotate_button = tk.Button(frame, text="Rotate Image", command=self.rotate_image)   # rotate button
        rotate_button.pack(side=tk.LEFT, padx=10)

        blur_button = tk.Button(frame, text="Blur Image", command=self.blur_image)   # blur image button
        blur_button.pack(side=tk.LEFT, padx=10)

        edge_button = tk.Button(frame, text="Edge Detect", command=self.edge_detection)   # edge detection button
        edge_button.pack(side=tk.LEFT, padx=10)

        # Resize Image slider
        self.resize_scale = tk.Scale(frame, label="Resize Image", from_=10, to=200, orient=tk.HORIZONTAL)
        self.resize_scale.set(100)
        self.resize_scale.pack(side=tk.LEFT, padx=10)
        self.resize_scale.bind("<Motion>", self.preview_resize)


    
    def add_shortcuts(self):
        # Shortcuts
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        self.root.bind("<Control-s>", lambda e: self.save_image())

    # Load Image function
    def load_image(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        image = cv2.imread(file_path)
        if image is None:
            messagebox.showerror("Error", "Invalid image file!")
            return
        self.original_image = image  # keep original
        # Clear any existing image
        self.modified_image = None
        self.history = []
        self.redo_stack = []
        # Show both in  canvases
        self.show_original()
        self.modified_canvas.delete("all")  # clear the right side

    # Show Image in screen
    def show_original(self):
       
        if self.original_image is None:
            self.original_canvas.delete("all")
            return
        # Converting Image
        rgb = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)
        pil_img.thumbnail((500, 450))  # fit to canvas area
        self.displayed_orig_width, self.displayed_orig_height = pil_img.size

        tk_img = ImageTk.PhotoImage(pil_img)
        self.original_canvas.delete("all")
        self.original_canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)
        # Keeping reference so image doesn't get garbage-collected
        self.original_canvas.image = tk_img


    def show_modified(self, image):
        
        if image is None:
            self.modified_canvas.delete("all")
            return
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)
        pil_img.thumbnail((500, 450))
        tk_img = ImageTk.PhotoImage(pil_img)
        self.modified_canvas.delete("all")
        self.modified_canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)
        self.modified_canvas.image = tk_img

  
    # Cropping Original Image
    def toggle_crop_mode(self):
        
        self.crop_mode = not self.crop_mode
        if self.crop_mode:
            # Bind to original canvas
            self.original_canvas.bind("<ButtonPress-1>", self.on_crop_start)
            self.original_canvas.bind("<B1-Motion>", self.on_crop_drag)
            self.original_canvas.bind("<ButtonRelease-1>", self.on_crop_release)
        else:
            # Unbind
            self.original_canvas.unbind("<ButtonPress-1>")
            self.original_canvas.unbind("<B1-Motion>")
            self.original_canvas.unbind("<ButtonRelease-1>")
            # Clear if any rectangle
            if self.crop_rect_id:
                self.original_canvas.delete(self.crop_rect_id)
                self.crop_rect_id = None
            self.rect_start = None
            self.rect_end = None
    
    # Start crop
    def on_crop_start(self, event):
        self.rect_start = (event.x, event.y)
        self.rect_end = None

    def on_crop_drag(self, event):
        if self.rect_start is None:
            return
        # Remove old rectangle if needed
        if self.crop_rect_id:
            self.original_canvas.delete(self.crop_rect_id)
        self.rect_end = (event.x, event.y)
        # Draw new rectangle
        x1, y1 = self.rect_start
        x2, y2 = self.rect_end
        self.crop_rect_id = self.original_canvas.create_rectangle(
            x1, y1, x2, y2, outline="red", dash=(4, 2)
        )

    def on_crop_release(self, event):
        """Finalize the cropping on the original image, display result on the right."""
        if not self.rect_start or not self.rect_end:
            return
        x1, y1 = self.rect_start
        x2, y2 = self.rect_end
        x1, x2 = sorted((x1, x2))
        y1, y2 = sorted((y1, y2))

        # Basic sanity check
        if (x2 - x1) < 2 or (y2 - y1) < 2:
            return

        # Map from canvas coords to actual original image coords
        H, W, _ = self.original_image.shape
        if self.displayed_orig_width == 0 or self.displayed_orig_height == 0:
            return
        scale_x = W / float(self.displayed_orig_width)
        scale_y = H / float(self.displayed_orig_height)

        x1_img = int(x1 * scale_x)
        x2_img = int(x2 * scale_x)
        y1_img = int(y1 * scale_y)
        y2_img = int(y2 * scale_y)

        # Clamp
        x1_img = max(0, min(x1_img, W))
        x2_img = max(0, min(x2_img, W))
        y1_img = max(0, min(y1_img, H))
        y2_img = max(0, min(y2_img, H))

        if (x2_img <= x1_img) or (y2_img <= y1_img):
            messagebox.showerror("Crop Error", "Invalid crop area selected.")
            return

        # Crop from the original image
        crop = self.original_image[y1_img:y2_img, x1_img:x2_img].copy()
        # This becomes our new "modified_image"
        self.modified_image = crop
        # Also push to history for undo
        self.history.append(self.modified_image.copy())
        self.redo_stack.clear()

        # Show it on the right
        self.show_modified(self.modified_image)

        # Optionally turn off crop mode
        self.toggle_crop_mode()

    #Gray scale function
    def apply_grayscale(self):
        if self.modified_image is None:
            return
        self.push_undo()
        gray = cv2.cvtColor(self.modified_image, cv2.COLOR_BGR2GRAY)
        self.modified_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        self.show_modified(self.modified_image)
    
    # Rotate image 90 degree function
    def rotate_image(self):
        if self.modified_image is None:
            return
        self.push_undo()
        self.modified_image = cv2.rotate(self.modified_image, cv2.ROTATE_90_CLOCKWISE)
        self.show_modified(self.modified_image)
    
    # Blur image function
    def blur_image(self):
        if self.modified_image is None:
            return
        self.push_undo()
        self.modified_image = cv2.GaussianBlur(self.modified_image, (15, 15), 0)
        self.show_modified(self.modified_image)
    
    # Edge detection function
    def edge_detection(self):
        if self.modified_image is None:
            return
        self.push_undo()
        gray = cv2.cvtColor(self.modified_image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        self.modified_image = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        self.show_modified(self.modified_image)

    #Resize preview function
    def preview_resize(self, event):

        if self.modified_image is None:
            return
        scale_percent = self.resize_scale.get()  # 10..200
        factor = scale_percent / 100.0
        h, w = self.modified_image.shape[:2]
        new_w = int(w * factor)
        new_h = int(h * factor)
        preview = cv2.resize(self.modified_image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        self.show_modified(preview)

    # History for undo function
    def push_undo(self):
        """Push current state onto history for undo."""
        if self.modified_image is not None:
            self.history.append(self.modified_image.copy())
            self.redo_stack.clear()
    
    # Undo function
    def undo(self, event=None):
        if len(self.history) > 1:
            # current state => redo stack
            current = self.history.pop()
            self.redo_stack.append(current)
            self.modified_image = self.history[-1].copy()
            self.show_modified(self.modified_image)
    
    # Redo function
    def redo(self, event=None):
        if self.redo_stack:
            # last undone => history
            undone = self.redo_stack.pop()
            self.history.append(undone)
            self.modified_image = undone
            self.show_modified(self.modified_image)
 
    # Save Image function 
    def save_image(self):

        if self.modified_image is None:
            messagebox.showerror("Error", "No modified image to save.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")]
        )
        if file_path:
            cv2.imwrite(file_path, self.modified_image)
            messagebox.showinfo("Saved", f"Image saved to: {file_path}")


app = EnhancedImageProcessor(root)
root.mainloop()

