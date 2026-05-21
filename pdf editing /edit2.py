import pypdf
from PIL import Image
import io

# 1. Open the PDF
reader = pypdf.PdfReader("document.pdf")
page = reader.pages[0]

# Use cropbox if available, otherwise mediabox
target_box = page.cropbox
pdf_w = float(target_box.width)
pdf_h = float(target_box.height)

print(f"Targeting visible area: {pdf_w}w x {pdf_h}h pts")

# 2. Convert PNG to PDF page
img = Image.open("image.png")
img_pdf_buffer = io.BytesIO()
img.save(img_pdf_buffer, format="PDF")
img_pdf_buffer.seek(0)

# 3. Load the image-page
image_reader = pypdf.PdfReader(img_pdf_buffer)
image_page = image_reader.pages[0]
img_w = float(image_page.mediabox.width)
img_h = float(image_page.mediabox.height)

# 4. Calculate scaling to STRETCH to fit exactly
# (Remove 'min' logic to force a perfect fill if aspect ratios differ)
scale_x = pdf_w / img_w
scale_y = pdf_h / img_h

# 5. Merge with explicit transformation
# This moves the image to the bottom-left of the visible cropbox
transformation = pypdf.Transformation().scale(sx=scale_x, sy=scale_y).translate(
    tx=float(target_box.left), 
    ty=float(target_box.bottom)
)

page.merge_transformed_page(image_page, transformation)

# 6. Save
writer = pypdf.PdfWriter()
writer.append_pages_from_reader(reader)
with open("finished_document.pdf", "wb") as f:
    writer.write(f)

print("Success! Created 'finished_document.pdf' with zero margins.")
