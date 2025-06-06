import io
from flask import Flask, request, send_file, abort, render_template
import barcode
from barcode.writer import ImageWriter

app = Flask(__name__)

# PNG endpoint: /barcode.png?code=<value>&type=<symbology>
@app.route("/barcode.png")
def barcode_png():

    text = request.args.get("code", "").strip()
    sym = request.args.get("type", "code128").strip().lower()

    if not text:
        return abort(400, "No code found")

    # code128 handles arbitrary input.
    BARCLASSES = {
        "code128": barcode.get_barcode_class("code128"),
        "ean13":   barcode.get_barcode_class("ean13"),
        "ean8":    barcode.get_barcode_class("ean8"),
        "upca":    barcode.get_barcode_class("upca"),
    }

    if sym not in BARCLASSES:
        return abort(400, f"Unsupported symbology '{sym}'")

    try:
        # retrieve barcode class with given symbology
        cls = BARCLASSES[sym]
        # create the barcode object passing in the text data and using ImageWriter() to get PNG file
        bc = cls(text, writer=ImageWriter())

        # Render Imagefile to buffer:
        buf = io.BytesIO()
        bc.write(buf, {"module_width": 0.2, "module_height": 15.0})

        buf.seek(0)
        # Return raw PNG
        return send_file(buf, mimetype="image/png")

    except barcode.errors.IllegalCharacterError:
        return abort(400, f"Text '{text}' contains illegal characters for {sym}")
    except barcode.errors.NumberOfDigitsError:
        return abort(400, f"Text '{text}' length is invalid for {sym}")
    except Exception as e:
        return abort(500, f"Error generating barcode: {e}")


# get endpoint serves index.html, post endpoint processes the submitted data
@app.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        # grab barcode values from the submitted form
        raw = request.form.get("barcodes", "").strip()
        if not raw:
            return render_template("index.html", error="Enter at least one barcode.")

        # splits into different barcodes based on newline or comma
        chunks = raw.replace(",", "\n").splitlines()
        # clean up each line and filter out nulls
        barcodes = [c.strip() for c in chunks if c.strip()]
        if not barcodes:
            return render_template("index.html", error="No valid barcodes found.")

        # grab the chosen endbyte from the form
        ending_choice = request.form.get("ending", "None")
        # map the ending byte form names to their actual byte values
        term_map = {"None": "", "CR": "\r", "LF": "\n", "CR+LF": "\r\n"}
        endByte = term_map.get(ending_choice, "")

        try:
            # grab the interval value from the form
            interval_ms = int(request.form.get("interval", "500"))
            if interval_ms < 50:
                raise ValueError
        except ValueError:
            return render_template("index.html", error="Interval must be integer ≥ 50.")

        # create new list with codes + endByte
        flash_list = []
        for b in barcodes:
            display_label = b + endByte
            url = f"/barcode.png?code={b}&type=code128"
            # create json list
            flash_list.append({"label": display_label, "img_url": url})

        return render_template(
            "flash.html",
            flash_list=flash_list,
            interval_ms=interval_ms
        )

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
