from PIL import Image
import os
import sys

def stack_images_vertically(top_image_path, bottom_image_path, output_path):
    """
    Combines two images by stacking the second one below the first one.

    Args:
        top_image_path (str): Path to the first image (will be on top).
        bottom_image_path (str): Path to the second image (will be on bottom).
        output_path (str): Path to save the combined image.
    """
    try:
        # 1. Open the images
        img1 = Image.open('brown1.png').convert("RGBA")
        img2 = Image.open('brown2.png').convert("RGBA")
        
        # 2. Ensure images have the same width
        width1, height1 = img1.size
        width2, height2 = img2.size
        
        if width1 != width2:
            print(f"⚠️ Warning: Images have different widths. ")
            print(f"   Image 1: {width1}px, Image 2: {width2}px.")
            print("   Resizing the narrower image to match the wider one.")
            
            new_width = max(width1, width2)
            
            # Function to resize while maintaining aspect ratio, or just resize
            def resize_image(img, target_width):
                if img.width == target_width:
                    return img
                
                # For simplicity, we'll just resize to the target width
                # This may distort the image if aspect ratio isn't maintained, 
                # but ensures the stack works.
                new_height = int(img.height * (target_width / img.width))
                return img.resize((target_width, new_height))

            img1 = resize_image(img1, new_width)
            img2 = resize_image(img2, new_width)
            
            width, height1 = img1.size # Recalculate dimensions
            _, height2 = img2.size
        else:
            width = width1
            
        # 3. Create a new blank image with the combined height
        total_height = height1 + height2
        
        # Create a blank image. "RGBA" supports transparency.
        # We fill it with transparent black (0, 0, 0, 0)
        combined_img = Image.new('RGBA', (width, total_height), (0, 0, 0, 0))
        
        # 4. Paste the images onto the blank canvas
        # Top image goes at (0, 0)
        combined_img.paste(img1, (0, 0))
        
        # Bottom image goes at (0, height1)
        combined_img.paste(img2, (0, height1))
        
        # 5. Save the final image
        combined_img.save(output_path)
        
        print(f"\n✅ Success!")
        print(f"   Input 1 (Top): {top_image_path} ({img1.size[0]}x{img1.size[1]})")
        print(f"   Input 2 (Bottom): {bottom_image_path} ({img2.size[0]}x{img2.size[1]})")
        print(f"   Output file saved to: {output_path} ({combined_img.size[0]}x{combined_img.size[1]})")

    except FileNotFoundError:
        print(f"\n❌ Error: One or both input files were not found.")
        print(f"   Check paths: '{top_image_path}' and '{bottom_image_path}'.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    # --- Configuration ---
    # The file that will be on the TOP
    TOP_FILE = "image1.png" 
    
    # The file that will be on the BOTTOM
    BOTTOM_FILE = "image2.png" 
    
    # The name of the resulting stacked file
    OUTPUT_FILE = "combined_stacked_image.png" 
    # ---------------------
    
    # For a more robust command-line script, you can use sys.argv to take 
    # file paths as arguments when running the script (e.g., python stacker.py fileA.png fileB.png output.png)
    if len(sys.argv) == 4:
        TOP_FILE = sys.argv[1]
        BOTTOM_FILE = sys.argv[2]
        OUTPUT_FILE = sys.argv[3]
    elif len(sys.argv) != 1:
        print("Usage:")
        print(f"  To use default files: python {os.path.basename(__file__)}")
        print(f"  To specify files:    python {os.path.basename(__file__)} <top_file.png> <bottom_file.png> <output_file.png>")
        sys.exit(1)

    stack_images_vertically(TOP_FILE, BOTTOM_FILE, OUTPUT_FILE)
