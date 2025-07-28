
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import os
import sys

IMG_PATH = "temp/input_image.png"
MASK_PATH = "temp/manual_mask.png"
MAX_SIZE = (512, 512)

class MaskDrawer:
    def __init__(self, root):
        self.root = root
        self.root.title("Manual Mask Drawing")

        # Load and resize image if too large
        original = Image.open(IMG_PATH).convert("RGB")
        self.image = original.copy()
        if self.image.size[0] > MAX_SIZE[0] or self.image.size[1] > MAX_SIZE[1]:
            self.image.thumbnail(MAX_SIZE)

        self.mask = Image.new("L", self.image.size, 0)
        self.draw = ImageDraw.Draw(self.mask)

        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas = tk.Canvas(self.root, width=self.image.width, height=self.image.height)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<Button-1>", self.paint)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        save_btn = tk.Button(btn_frame, text="✅ Save Mask & Close", command=self.safe_exit)
        save_btn.pack()

        self.root.protocol("WM_DELETE_WINDOW", self.safe_exit)

    def paint(self, event):
        radius = 10
        x, y = event.x, event.y
        self.draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=255)
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="black", outline="black")

    def safe_exit(self):
        try:
            os.makedirs(os.path.dirname(MASK_PATH), exist_ok=True)
            self.mask.save(MASK_PATH)
            print(f"✅ Mask saved at: {MASK_PATH}")
        except Exception as e:
            print(f"❌ Failed to save mask: {e}")
        finally:
            try:
                self.root.quit()     # Stop the mainloop
                self.root.update()   # Process any remaining events
                self.root.destroy()  # Close the window
            except Exception as e:
                print(f"⚠️ Error while closing window: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MaskDrawer(root)
    try:
        root.mainloop()
    except Exception as e:
        print(f"❌ Mainloop error: {e}")
        sys.exit(1)