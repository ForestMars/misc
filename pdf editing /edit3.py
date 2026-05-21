import pypdf
from PIL import Image
import io

# 1. Open the PDF and get the visible area
reader = pypdf.PdfReader("document.pdf")
page = reader.pages[0]

# The CropBox is the part of the PDF you actually see
target_box = page.cropbox
pdf_w = float(target_box.width)
pdf_h = float(target_box.height)

# 2. Get the PNG dimensions
img = Image.open("image.png")
img_w_px, img_h_px = img.size

# 3. Create a temporary PDF page from the image
img_pdf_buffer = io.BytesIO()
img.save(img_pdf_buffer, format="PDF")
img_pdf_buffer.seek(0)
image_reader = pypdf.PdfReader(img_pdf_buffer)
image_page = image_reader.pages[0]
img_w_pts = float(image_page.mediabox.width)
img_h_pts = float(image_page.mediabox.height)

# 4. Calculate scaling (Maintain Aspect Ratio)
scale = min(pdf_w / img_w_pts, pdf_h / img_h_pts)

# 5. Calculate centering offsets relative to the CropBox
# This ensures it's centered even if the PDF has internal offsets
scaled_w = img_w_pts * scale
scaled_h = img_h_pts * scale

offset_x = float(target_box.left) + (pdf_w - scaled_w) / 2
offset_y = float(target_box.bottom) + (pdf_h - scaled_h) / 2

# 6. Apply transformation
transformation = pypdf.Transformation().scale(sx=scale, sy=scale).translate(tx=offset_x, ty=offset_y)
page.merge_transformed_page(image_page, transformation)

# 7. Save
writer = pypdf.PdfWriter()
writer.append_pages_from_reader(reader)
with open("finished_document.pdf", "wb") as f:
    writer.write(f)

print(f"Done! Image scaled by {round(scale, 2)}x and centered.")
