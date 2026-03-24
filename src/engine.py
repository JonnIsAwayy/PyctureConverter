import os
from PIL import Image
import vtracer

def convert(selected_file_path, target_format):
    if not selected_file_path:
        raise ValueError("No file selected.")

    base_name = os.path.splitext(selected_file_path)[0]
    output_path = f"{base_name}_converted.{target_format.lower()}"

    if target_format == "SVG":
        vtracer.convert_image_to_svg_py(
            selected_file_path, 
            output_path,
            colormode='color',
            mode='spline',
            hierarchical='stacked',
            filter_speckle=4,
            color_precision=6
        )
    else:
        with Image.open(selected_file_path) as img:
            if target_format == "JPEG" and img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            img.save(output_path, format=target_format)

    return output_path
