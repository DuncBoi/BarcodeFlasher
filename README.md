# Barcode Flasher

A small Flask-based web app that lets you enter one or more barcodes (with optional line-feed, carriage-return, or form-feed endings), choose a flash interval, and then “flash” them fullscreen one at a time. Includes “fast” and “insanely fast” scan-sequence modes and adjustable Motorola scanner volume presets.

---
## Table of Contents

1. [Directory Structure](#directory-structure)  
2. [Prerequisites](#prerequisites)  
3. [Quickstart Guide](#quickstart-guide)  
4. [Settings](#settings)  
5. [Adding Barcodes & Flash Sequence](#adding-barcodes--flash-sequence)  
6. [Configuration](#configuration)  
7. [Code Walkthrough](#code-walkthrough)  

---

## Directory Structure

```
barcode-flasher/
├── app.py
├── requirements.txt
├── static/
│   ├── illumination.png
│   ├── enablePresentation.png
│   ├── timeoutBetweenDecodes.png
│   ├── 0.png
│   ├── smallFOV.png
│   ├── defaults.png
│   ├── lowVolume.png
│   ├── mediumVolume.png
│   ├── highVolume.png
│   ├── disableBeep.png
│   ├── ui.png
│   └── enableBeep.png
└── templates/
    ├── index.html
    └── flash.html
```

---

## Prerequisites

- **Python 3.8+**
- **pip** (packaged with Python)  
- A POSIX-style shell


## Quickstart Guide

1. Clone the repo  
   ```bash
   git clone https://github.com/DuncBoi/BarcodeFlasher.git
   cd BarcodeFlasher
   ```

2. Create a virtual environment  
   ```bash
   python3 -m venv venv
   ```

3. Activate the virtual environment (choose the command that matches your shell)  
   **bash / zsh / sh**  
   ```bash
   source venv/bin/activate
   ```  
   **csh / tcsh**  
   ```csh
   source venv/bin/activate.csh
   ```  
   **fish**  
   ```fish
   source venv/bin/activate.fish
   ```

4. Install Python dependencies  
   ```bash
   pip install -r requirements.txt
   ```

5. Run the app
   ```bash
   python3 app.py
   ```
   
6. You should see something like:  
   ```  
   * Serving Flask app 'app'  
   * Debug mode: off  
   WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.  
   * Running on all addresses (0.0.0.0)  
   * Running on http://127.0.0.1:5000  
   * Running on http://10.15.57.104:5000  
   ```  
   Open one of those URLs in your browser and interact with the UI.
---

7. Now you should see something like this:
<img src="static/ui.png" alt="Barcode Flasher Home Screen" title="Barcode Flasher UI">

## Settings

**1. Reset to Defaults**  
Before making any changes, click **Reset Scanner to Default Settings**. The scanner will flash the `defaults.png` barcode. Scan this with the barcode reader to revert to factory parameters.

Scan one of the following barcodes to adjust the beep volume based on your preferences
- **Low Volume**: quiet beep, ideal for noise-sensitive environments.  
- **Medium Volume**: balanced feedback for general use.  
- **High Volume**: loud beep to confirm scans in loud areas.  
- **Disable Beep**: turns off all audio feedback.  
- **Enable Beep**: restores the beep after it has been disabled.  

**3. Fast Mode (Recommended for All Testing)**  
Scan these in order:  
1. **Illumination Always On** (`illumination.png`)  
   - Keeps the aimer LED and illumination lamp active at all times, eliminating warm-up delays and improving screen scan performance.  
2. **Presentation Mode** (`enablePresentation.png`)  
   - Projects a red aimer dot for precise on-screen targeting.  

**4. Insanely Fast Mode**  
Only use this if you want to really stress test the functionality.  
*Fast Mode must be scanned before Insanely Fast Mode will work.* Once Fast Mode is enabled, scan these in sequence to remove all inter-scan delays and reduce processing overhead:  
1. **Timeout Between Decodes, Same Symbol** (`timeoutBetweenDecodes.png`)  
2. **“0” Barcode** (`0.png`) – scan twice (it appears twice in the sequence).  
   - Sets the scanner’s internal delay between identical barcode scans to 0 ms (default is 400 ms).    
3. **Small Field of View** (`smallFOV.png`)  
   - Narrows the sensor’s active area, reducing processing time per scan.

---

## Adding Barcodes & Flash Sequence

On the **Index** page you can build an arbitrary sequence of barcodes, each with an optional “ending” control character. When you click **Start Flash**, the app will cycle through your list on the **Flash** page, showing each barcode fullscreen for a brief moment, then pausing until the next one.

### 1. Building your sequence

1. **Add a row**: click **+ Add Barcode** to append a new input row.  
2. **Enter your code**: in the text box, type the exact barcode data (e.g. `1234567`).  
3. **Select an ending**: choose one of:
   - **None** — no extra byte  
   - **Line Feed (\\n)** — appends ASCII 10  
   - **Carriage Return (\\r)** — appends ASCII 13  
   - **Form Feed (\\f)** — appends ASCII 12  
4. **Remove if needed**: click **Remove** on any row to delete it.  

> empty barcode fields are disallowed — you’ll get an alert if you try to submit with blank rows.

### 2. Setting the flash interval

- The **Interval** input (in milliseconds) controls the length of time between subsequent flashes in your sequence, the actual barcode itself is only flashed for 0.4 seconds.  
- **Boundaries**: must be an integer ≥ 50. If you enter less than 50, the server will reject it with an error.  

## Configuration

- **Port & Host**: default is `0.0.0.0:5000`. Change in `app.py` or set via environment if using a WSGI server.  
- **Flash GIFs / Images**: put any extra `.png` files under `static/`. Filenames must match the JS arrays in `index.html`/`flash.html`.  
- **Interval Limits**: minimum 50 ms between barcode starts. Change in both client-side validation (`min="50"`) and server (`if interval_ms < 50`).  

---

## Code Walkthrough

### app.py

1. Imports & Setup  
- Flask, request, send_file, abort, render_template  
- barcode + ImageWriter for PNGs  
- io.BytesIO() for buffer  
- app = Flask(__name__)

2. /barcode.png  
- Reads code & type params  
- Validates code, maps type via BARCLASSES  
- Generates barcode PNG into buffer and returns with send_file  
- Error handling returns 400 or 500 on failure

3. /  
- GET: renders index.html  
- POST:  
  - Retrieves barcodes[] & endings[], maps control chars, filters empties  
  - Validates at least one pair and interval_ms ≥ 50  
  - Builds flash_list of {label,img_url}  
  - Renders flash.html with context

### templates/index.html

- Dynamic barcode rows via makeRow()  
- Form with volume select, interval input, buttons (Add, Clear, Fast, Insane, Reset, Start Flash)  
- Overlays for volume and fast modes  
- JS handles row management, validation, localStorage persistence, and overlays

### templates/flash.html

- Preloads flash_list images  
- showFlash(): displays each barcode + label for 400 ms  
- clearAndCountdown(): clears image, shows countdown, then schedules next showFlash()  
- Loops through flash_list; Stop button returns to index

### static/

- Contains all PNG assets for volume presets, fast/insane modes, defaults; filenames must match above


