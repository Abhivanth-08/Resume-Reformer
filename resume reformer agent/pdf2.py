import fitz  # PyMuPDF
from pdf2image import convert_from_path
import cv2
import numpy as np


def detect_lines_and_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=800, maxLineGap=10)

    line_list = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            line_list.append(((x1, y1), (x2, y2)))
    return line_list, img


def average_line_color(img, p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    length = int(np.hypot(x2 - x1, y2 - y1))
    if length == 0:
        return (255, 255, 255)
    colors = []
    for i in range(length):
        x = int(x1 + (x2 - x1) * i / length)
        y = int(y1 + (y2 - y1) * i / length)
        colors.append(img[y, x])  # BGR
    avg_color = np.mean(colors, axis=0)
    # Convert BGR to RGB normalized 0-1 for fitz
    col = tuple((avg_color[::-1] / 255).tolist())
    return col


def lines_too_close(line1, line2, threshold=3):
    def dist(a, b):
        return np.linalg.norm(np.array(a) - np.array(b))
    dists = [
        dist(line1[0], line2[0]),
        dist(line1[0], line2[1]),
        dist(line1[1], line2[0]),
        dist(line1[1], line2[1]),
    ]
    return min(dists) < threshold


def pdf_to_image(pdf_path, dpi=300):
    images = convert_from_path(
        pdf_path,
        dpi=dpi,
        poppler_path=r"C:\Users\abhiv\OneDrive\Desktop\agentic ai\resume reformer agent\poppler-24.08.0\Library\bin"
    )
    image_paths = []
    for i, img in enumerate(images):
        img_path = f"design_page_{i}.png"
        img.save(img_path)
        image_paths.append(img_path)
    return image_paths


def transfer_design_to_pdf(design_pdf_path, base_pdf_path, output_pdf_path, dpi=300):
    design_images = pdf_to_image(design_pdf_path, dpi=dpi)
    base_doc = fitz.open(base_pdf_path)
    new_doc = fitz.open()

    scale = 72 / dpi
    num_pages = min(len(design_images), len(base_doc))

    for i in range(num_pages):
        lines, img = detect_lines_and_image(design_images[i])
        base_page = base_doc[i]
        new_page = new_doc.new_page(width=base_page.rect.width, height=base_page.rect.height)

        # Step 1: Copy original content
        new_page.show_pdf_page(new_page.rect, base_doc, i)

        # Step 2: Re-draw design lines
        drawn_lines = []
        for (p1, p2) in lines:
            if any(lines_too_close((p1, p2), dl) for dl in drawn_lines):
                continue

            p1_pdf = (p1[0] * scale, p1[1] * scale)
            p2_pdf = (p2[0] * scale, p2[1] * scale)
            color = average_line_color(img, p1, p2)
            new_page.draw_line(p1_pdf, p2_pdf, color=color, width=1)
            drawn_lines.append((p1, p2))

        # Step 3: Transfer link annotations
        for annot in base_page.annots(types=[fitz.PDF_ANNOT_LINK]) or []:
            info = annot.info
            rect = annot.rect

            if "uri" in info:  # external link
                new_page.insert_link({
                    "kind": fitz.LINK_URI,
                    "from": rect,
                    "uri": info["uri"]
                })
            elif "page" in info:  # internal document link
                new_page.insert_link({
                    "kind": fitz.LINK_GOTO,
                    "from": rect,
                    "page": info["page"]
                })

    new_doc.save(output_pdf_path)
    new_doc.close()
    base_doc.close()
    print(f"✅ New PDF saved with design + links: {output_pdf_path}")


