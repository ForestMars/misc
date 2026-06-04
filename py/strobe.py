import tkinter as tk
from PIL import Image, ImageTk
import sys
import os

class ImageStrober:
    def __init__(self, root, image_path, strobe_speed):
        self.root = root
        self.image_path = image_path
        self.strobe_speed = strobe_speed  # Speed in milliseconds
        self.visible = True
        
        # Load the image
        try:
            self.image = Image.open(image_path)
            self.photo = ImageTk.PhotoImage(self.image)
        except Exception as e:
            print(f"Error loading image: {e}")
            sys.exit(1)
        
        # Create canvas
        self.canvas = tk.Canvas(root, width=self.image.width, height=self.image.height)
        self.canvas.pack()
        
        # Create image item on canvas
        self.image_item = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        # Start the strobe effect
        self.strobe()
        
    def strobe(self):
        if self.visible:
            self.canvas.itemconfig(self.image_item, state='hidden')
        else:
            self.canvas.itemconfig(self.image_item, state='normal')
        
        self.visible = not self.visible
        self.root.after(self.strobe_speed, self.strobe)

def main():
    # Check if image path and speed are provided
    if len(sys.argv) != 3:
        print("Usage: python script.py <image_path> <strobe_speed_in_ms>")
        print("Example: python script.py image.jpg 500")
        sys.exit(1)
    
    image_path = sys.argv[1]
    try:
        strobe_speed = int(sys.argv[2])
        if strobe_speed <= 0:
            raise ValueError
    except ValueError:
        print("Strobe speed must be a positive integer (in milliseconds)")
        sys.exit(1)
    
    # Verify image file exists
    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}")
        sys.exit(1)
    
    # Create Tkinter window
    root = tk.Tk()
    root.title("Image Strober")
    
    # Initialize the strober
    app = ImageStrober(root, image_path, strobe_speed)
    
    # Run the application
    root.mainloop()

if __name__ == "__main__":
    main()
