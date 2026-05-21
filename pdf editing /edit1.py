import pypdf
from PIL import Image
import io

# 1. Open the PDF and get dimensions of page 1
reader = pypdf.PdfReader("document.pdf")
first_page = reader.pages[0]
pdf_w = float(first_page.mediabox.width)
pdf_h = float(first_page.mediabox.height)

print(f"Detected PDF size: {pdf_w}w x {pdf_h}h pts")

# 2. Convert PNG to a PDF page in memory
img = Image.open("image.png")
img_w, img_h = img.size
img_pdf_buffer = io.BytesIO()
img.save(img_pdf_buffer, format="PDF")
img_pdf_buffer.seek(0)

# 3. Load the image-page and calculate scaling
image_reader = pypdf.PdfReader(img_pdf_buffer)
image_page = image_reader.pages[0]

# Calculate scale to fit (keeping aspect ratio)
scale = min(pdf_w / float(image_page.mediabox.width), 
            pdf_h / float(image_page.mediabox.height))

image_page.scale_by(scale)

# Calculate centering offsets
offset_x = (pdf_w - (float(image_page.mediabox.width) * scale)) / 2
offset_y = (pdf_h - (float(image_page.mediabox.height) * scale)) / 2

# 4. Merge the image onto the blank first page
first_page.merge_transformed_page(
    image_page, 
    pypdf.Transformation().translate(offset_x, offset_y)
)

# 5. Save the final file
writer = pypdf.PdfWriter()
writer.append_pages_from_reader(reader)
with open("finished_document.pdf", "wb") as f:
    writer.write(f)

print("Success! Created 'finished_document.pdf'")
