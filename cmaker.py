import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk, Menu, colorchooser
import os

class OpenCollageMaker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OpenCollage Maker")
        self.geometry("1200x950")
        self.configure(bg="#f5f5f7")
        
        self.images = [] 
        self.result_bgr = None
        self.bg_color = (255, 255, 255) 
        self.ratios = {
            "1:1 Square": (1, 1),
            "4:3 Landscape": (4, 3),
            "3:4 Portrait": (3, 4),
            "16:9 Cinematic": (16, 9)
        }
        
        self.drag_idx = None
        self.right_clicked_idx = None
        self.image_rects = [] 
        
        self._setup_ui()
        self._create_context_menu()

    def _setup_ui(self):
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(self, bg="#f5f5f7", highlightthickness=0, cursor="arrow")
        self.canvas.grid(row=0, column=0, sticky="nsew", pady=20)
        
        # Interaction Bindings
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_stop)
        self.canvas.bind("<Button-3>", self.show_context_menu)
        # Auto-close menu on left click
        self.canvas.bind("<Button-1>", self.close_menu, add="+")

        footer = ttk.Frame(self, padding=15, style="White.TFrame")
        footer.grid(row=1, column=0, sticky="ew")
        
        style = ttk.Style()
        style.configure("White.TFrame", background="#ffffff")
        style.configure("Tool.TLabel", background="#ffffff", font=('Segoe UI', 8, 'bold'), foreground="#888")

        tool_hub = ttk.Frame(footer, style="White.TFrame")
        tool_hub.pack(expand=True)

        def create_unit(label):
            u = ttk.Frame(tool_hub, style="White.TFrame")
            u.pack(side="left", padx=12, anchor="s") 
            c = ttk.Frame(u, style="White.TFrame")
            c.pack(side="top", pady=(0, 4)) 
            l = ttk.Label(u, text=label, style="Tool.TLabel")
            l.pack(side="top", anchor="center")
            return c

        # 1. Grid Controls
        self.rows_var, self.cols_var = tk.IntVar(value=2), tk.IntVar(value=2)
        grid_c = create_unit("GRID")
        for v in [self.rows_var, self.cols_var]:
            v.trace_add("write", lambda *a: self.generate())
            tk.Spinbox(grid_c, from_=1, to=10, textvariable=v, width=3, bg="#f0f0f0", bd=0).pack(side="left", padx=2)

        # 2. Aspect Ratio Selector
        ratio_c = create_unit("RATIO")
        self.ratio_var = tk.StringVar(value="1:1 Square")
        ratio_dd = ttk.Combobox(ratio_c, textvariable=self.ratio_var, values=list(self.ratios.keys()), state="readonly", width=12)
        ratio_dd.pack()
        ratio_dd.bind("<<ComboboxSelected>>", lambda e: self.generate())

        # 3. Spacing Sliders
        slider_cfg = {"bg": "white", "troughcolor": "#e0e0e0", "showvalue": False, "highlightthickness": 0, "sliderlength": 15}
        self.inner_var = tk.IntVar(value=10)
        tk.Scale(create_unit("INNER"), from_=0, to=50, orient="horizontal", variable=self.inner_var, command=lambda x: self.generate(), length=70, **slider_cfg).pack()

        self.outer_var = tk.IntVar(value=20)
        tk.Scale(create_unit("MARGIN"), from_=0, to=100, orient="horizontal", variable=self.outer_var, command=lambda x: self.generate(), length=70, **slider_cfg).pack()

        # 4. BG Color Swatch
        color_c = create_unit("BG")
        color_frame = tk.Frame(color_c, width=22, height=22, bg="#cccccc", bd=1)
        color_frame.pack_propagate(False)
        color_frame.pack(pady=2)
        self.color_btn = tk.Button(color_frame, bg="white", relief="flat", command=self.pick_color, activebackground="#eeeeee", cursor="hand2")
        self.color_btn.pack(fill="both", expand=True)

        # 5. Title Entry
        self.caption_var = tk.StringVar(value="MY COLLAGE")
        self.caption_var.trace_add("write", lambda *a: self.generate())
        tk.Entry(create_unit("TITLE"), textvariable=self.caption_var, width=12, bg="#f0f0f0", bd=0).pack(ipady=3)

        # 6. Action Buttons
        act_c = create_unit("FILE")
        ttk.Button(act_c, text="Add", command=self.load_images).pack(side="left", padx=2)
        ttk.Button(act_c, text="Clear", command=self.clear_all).pack(side="left", padx=2)
        ttk.Button(act_c, text="Save", command=self.save_image).pack(side="left", padx=2)

    def _create_context_menu(self):
        self.menu = Menu(self, tearoff=0)
        self.menu.add_command(label="Rotate 90°", command=self.rotate_selected)
        self.menu.add_separator()
        self.menu.add_command(label="Move Left", command=lambda: self.shift_index(-1))
        self.menu.add_command(label="Move Right", command=lambda: self.shift_index(1))
        self.menu.add_command(label="Move Up", command=lambda: self.shift_index(-self.cols_var.get()))
        self.menu.add_command(label="Move Down", command=lambda: self.shift_index(self.cols_var.get()))
        self.menu.add_separator()
        self.menu.add_command(label="Remove Image", command=self.delete_selected, foreground="red")

    def show_context_menu(self, event):
        self.close_menu()
        for i, (x1, y1, x2, y2) in enumerate(self.image_rects):
            if x1 <= event.x <= x2 and y1 <= event.y <= y2 and i < len(self.images):
                self.right_clicked_idx = i
                self.menu.post(event.x_root, event.y_root)
                return
        self.right_clicked_idx = None

    def close_menu(self, event=None):
        self.menu.unpost()

    def shift_index(self, delta):
        if self.right_clicked_idx is not None:
            new_idx = self.right_clicked_idx + delta
            if 0 <= new_idx < len(self.images):
                self.images[self.right_clicked_idx], self.images[new_idx] = \
                    self.images[new_idx], self.images[self.right_clicked_idx]
                self.generate()

    def delete_selected(self):
        if self.right_clicked_idx is not None:
            self.images.pop(self.right_clicked_idx)
            self.generate()

    def rotate_selected(self):
        if self.right_clicked_idx is not None:
            self.images[self.right_clicked_idx] = cv2.rotate(self.images[self.right_clicked_idx], cv2.ROTATE_90_CLOCKWISE)
            self.generate()

    def clear_all(self):
        self.images = []
        self.result_bgr = None
        self.canvas.delete("all")
        self.generate()

    def pick_color(self):
        color = colorchooser.askcolor(title="Select Background Color")
        if color[1]: 
            self.color_btn.config(bg=color[1])
            r, g, b = [int(color[1][i:i+2], 16) for i in (1, 3, 5)]
            self.bg_color = (b, g, r) 
            self.generate()

    def center_crop_to_ratio(self, img, target_w, target_h):
        h, w = img.shape[:2]
        target_aspect = target_w / target_h
        current_aspect = w / h
        if current_aspect > target_aspect:
            new_w = int(h * target_aspect)
            offset = (w - new_w) // 2
            img = img[:, offset:offset+new_w]
        else:
            new_h = int(w / target_aspect)
            offset = (h - new_h) // 2
            img = img[offset:offset+new_h, :]
        return cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)

    def generate(self):
        if not self.images: 
            self.canvas.delete("all")
            return
        try:
            r, c = self.rows_var.get(), self.cols_var.get()
            base_dim = 450
            rw, rh = self.ratios[self.ratio_var.get()]
            cell_w, cell_h = int(base_dim * rw), int(base_dim * rh)
            inner, outer = self.inner_var.get(), self.outer_var.get()
            cap = self.caption_var.get().strip()
            f_h = 120 if cap else outer
            
            canvas_w = (outer * 2) + (c * cell_w) + ((c - 1) * inner)
            canvas_h = outer + (r * cell_h) + ((r - 1) * inner) + f_h
            canvas_bgr = np.full((canvas_h, canvas_w, 3), self.bg_color, dtype=np.uint8)
            raw_rects = []

            for i in range(min(len(self.images), r * c)):
                idx_r, idx_c = divmod(i, c)
                img = self.center_crop_to_ratio(self.images[i].copy(), cell_w, cell_h)
                y = outer + idx_r * (cell_h + inner)
                x = outer + idx_c * (cell_w + inner)
                canvas_bgr[y:y+cell_h, x:x+cell_w] = img
                raw_rects.append((x, y, x + cell_w, y + cell_h))

            if cap:
                font = cv2.FONT_HERSHEY_DUPLEX
                tw = cv2.getTextSize(cap, font, 1.5, 2)[0][0]
                lum = 0.299*self.bg_color[2] + 0.587*self.bg_color[1] + 0.114*self.bg_color[0]
                t_color = (255, 255, 255) if lum < 128 else (60, 60, 60)
                cv2.putText(canvas_bgr, cap, ((canvas_w - tw)//2, canvas_h - 50), font, 1.5, t_color, 2, cv2.LINE_AA)

            self.result_bgr = canvas_bgr
            self._render_to_canvas(canvas_bgr, raw_rects)
        except: pass

    def _render_to_canvas(self, bgr_img, raw_rects):
        h, w = bgr_img.shape[:2]
        self.update_idletasks()
        win_w, win_h = self.canvas.winfo_width(), self.canvas.winfo_height()
        scale = min(win_w / w, win_h / h) * 0.92
        nw, nh = int(w * scale), int(h * scale)
        rgb = cv2.cvtColor(cv2.resize(bgr_img, (nw, nh)), cv2.COLOR_BGR2RGB)
        ppm = f'P6 {nw} {nh} 255\n'.encode() + rgb.tobytes()
        self.preview_tk = tk.PhotoImage(data=ppm, format='PPM')
        self.canvas.delete("all")
        ox, oy = (win_w - nw) // 2, (win_h - nh) // 2
        self.canvas.create_image(win_w//2, win_h//2, image=self.preview_tk, tags="bg")
        self.image_rects = [(int(x1*scale)+ox, int(y1*scale)+oy, int(x2*scale)+ox, int(y2*scale)+oy) for (x1,y1,x2,y2) in raw_rects]

    def on_drag_start(self, event):
        self.close_menu()
        for i, (x1, y1, x2, y2) in enumerate(self.image_rects):
            if x1 <= event.x <= x2 and y1 <= event.y <= y2 and i < len(self.images):
                self.drag_idx = i
                thumb = cv2.resize(self.images[i], (120, 120))
                thumb_rgb = cv2.cvtColor(thumb, cv2.COLOR_BGR2RGB)
                ppm = f'P6 120 120 255\n'.encode() + thumb_rgb.tobytes()
                self.ghost_tk = tk.PhotoImage(data=ppm, format='PPM')
                self.canvas.create_image(event.x, event.y, image=self.ghost_tk, tags="ghost")
                break

    def on_drag_motion(self, event):
        if self.drag_idx is not None:
            self.canvas.coords(self.canvas.find_withtag("ghost")[0], event.x, event.y)
            self.canvas.delete("target")
            for i, (x1, y1, x2, y2) in enumerate(self.image_rects):
                if x1 <= event.x <= x2 and y1 <= event.y <= y2 and i != self.drag_idx:
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="#0078d4", width=3, dash=(4,2), tags="target")

    def on_drag_stop(self, event):
        if self.drag_idx is not None:
            drop_target = None
            for i, (x1, y1, x2, y2) in enumerate(self.image_rects):
                if x1 <= event.x <= x2 and y1 <= event.y <= y2: drop_target = i
            self.canvas.delete("ghost", "target")
            if drop_target is not None and drop_target != self.drag_idx and drop_target < len(self.images):
                self.images[self.drag_idx], self.images[drop_target] = self.images[drop_target], self.images[self.drag_idx]
                self.generate()
        self.drag_idx = None

    def load_images(self):
        files = filedialog.askopenfilenames()
        for f in files:
            img = cv2.imread(f)
            if img is not None: self.images.append(img)
        self.generate()

    def save_image(self):
        if self.result_bgr is not None:
            path = filedialog.asksaveasfilename(defaultextension=".jpg")
            if path: cv2.imwrite(path, self.result_bgr)

if __name__ == "__main__":
    app = OpenCollageMaker()
    app.mainloop()
