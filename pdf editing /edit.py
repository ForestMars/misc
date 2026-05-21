import pypdf
from PIL import Image

# 1. Convert PNG to a temporary PDF page
img = Image.open("image.png")
img.save("temp_page.pdf")

# 2. Merge them
pdf = pypdf.PdfReader("document.pdf")
image_page = pypdf.PdfReader("temp_page.pdf").pages[0]

# Overlay the image onto the first page
pdf.pages[0].merge_page(image_page)

writer = pypdf.PdfWriter()
writer.append_pages_from_reader(pdf)
with open("output.pdf", "wb") as f:
    writer.write(f)
