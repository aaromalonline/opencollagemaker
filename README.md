# OpenCollage Maker

A modern, interactive Python application for creating professional-grade image collages. **OpenCollage Maker** combines high-performance image processing via OpenCV with a fluid, responsive user interface to make grid-based design effortless.

---

## 🛠 Tools & Modules
The project is built using a robust stack of Python libraries:
* **OpenCV (`cv2`):** Handles high-speed image transformations, rotations, and color space management.
* **NumPy:** Powers the canvas as a multi-dimensional array for pixel-perfect precision.
* **Tkinter:** Drives the GUI, utilizing `ttk` for modern styling and `colorchooser` for theme customization.
* **OS & Base Modules:** Manages file I/O and path operations for batch image loading.

---

## ⚙️ Image Processing Pipeline
When you generate or modify a collage, each image slot undergoes the following automated pipeline:

1.  **Normalization:** Images are opened and converted to a uniform BGR color space to ensure consistent rendering.
2.  **Affine Scaling:** Initial per-image scale factors are applied using **Lanczos resampling** to preserve sharpness.
3.  **Rotation:** Images are rotated using an Affine matrix. The bounding box dynamically adjusts to prevent clipping.
4.  **Smart Cover-Crop:** To prevent letterboxing or stretching, the system computes the optimal scale to fill the cell entirely and then center-crops to the exact target dimensions.
5.  **Composition:** Processed segments are stitched onto the master NumPy canvas with user-defined gutters and margins.

---

## Functional Overview

### 1. Dynamic Layout & Proportions
* **Grid Control:** Spinboxes to adjust the number of **Rows** and **Columns** (up to a 10x10 grid).
* **Aspect Ratio Engine:** A dropdown to switch between standard photography and cinematic ratios (**1:1, 4:3, 3:4, 16:9**).
* **Smart Center-Cropping:** Automatically calculates the optimal crop for every uploaded image so they fill the grid cell perfectly without stretching.

### 2. Live Preview & Real-Time Feedback
* **Variable Tracing:** Uses `trace_add` logic on all UI variables (Grid, Sliders, Title) to trigger an instant re-render the moment a value changes.
* **Zero-Latency Updates:** Every micro-adjustment to spacing, margins, or text is reflected immediately in the preview window.
* **Adaptive Text Contrast:** The caption color automatically flips between **Black** and **White** based on the background color's luminance.

### 3. Responsive UI & Auto-Scaling
* **Dynamic Canvas Fitting:** The preview automatically calculates the available window space (`winfo_width`/`height`) and scales the collage to fit perfectly.
* **Window Resize Support:** The `update_idletasks` logic ensures the collage scales smoothly when resizing the application window.

### 4. High-Precision Drag & Drop
* **Canvas-Layered Dragging:** A "ghost" thumbnail follows your cursor with 1:1 precision, decoupled from the background to prevent lag.
* **Target Highlighting:** A blue dashed box appears over the destination slot during a drag, showing exactly where the swap will occur.
* **Automatic Swapping:** Releasing an image over another instantly swaps their positions in the sequence.

### 5. Contextual Image Editing (Right-Click)
* **Surgical Position Control:** Shift images **Left, Right, Up, or Down** via a context menu.
* **Independent Rotation:** Rotate a single selected image by **90° clockwise** without affecting global settings.
* **Targeted Removal:** A **"Remove Image"** option that deletes the specific photo and collapses the grid to fill the gap.

### 6. Professional Aesthetics & Handling
* **Lanczos4 Resampling:** High-quality interpolation ensures the final exported file remains sharp.
* **Modern Footer UI:** Icons and labels are baseline-aligned for a clean, mobile-app-inspired aesthetic.
* **System Integration:** Standard file dialogs for batch adding and saving, plus a dedicated system color picker for the background.

---

## 🖥 GUI Overview
Driven by the **Tkinter** module with modern **ttk styling**, the interface is designed to maximize screen real estate and ease of use.

* **Live Preview (Main Canvas):** A responsive `tk.Canvas` that displays a real-time downscaled thumbnail of your work.
* **Main Control Menu (Footer):** A sleek, baseline-aligned footer containing all tools. This "mobile-first" layout keeps controls within reach while you focus on the preview.
* **Contextual Menu (Right-Click):** A right-click menu system that allows for surgical, per-image edits without cluttering the main screen.

---

## 📦 Installation

Ensure you have Python 3.7+ installed. Follow these steps to get started:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/opencollage-maker.git](https://github.com/yourusername/opencollage-maker.git)
   cd opencollage-maker
2. **Install required dependencies:**
      ```bash
   pip install -r ./requirements.txt
3. **Launch the Application:**
      ```bash
   python3 ./cmaker.py

## Usage

**1. Import Your Photos** Click the **Add** button to select multiple images. The **Live Preview** renders them immediately.

**2. Configure Your Layout**
* Set your grid size and choose an aspect ratio.
* Adjust **INNER** (gutters) and **MARGIN** (outer frame) sliders for the perfect spacing.

**3. Arrange via Drag & Drop** Click and hold any photo to drag it. Release over another slot to swap images.

**4. Surgical Edits (Right-Click)** Right-click any photo to **Rotate, Shift, or Remove** it from the layout.

**5. Style & Save** Pick a custom **BG** color, enter a **TITLE**, and click **Save** to export your high-resolution masterpiece.
