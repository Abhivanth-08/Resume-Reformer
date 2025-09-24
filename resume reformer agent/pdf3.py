import fitz  # PyMuPDF

design_path = "R Abhivanth Resume.pdf"
target_path = "new3.pdf"

design_doc = fitz.open(design_path)
target_doc = fitz.open(target_path)

assert len(design_doc) == len(target_doc), "Mismatch in page count!"

for i in range(len(target_doc)):
    design_page = design_doc[i]
    target_page = target_doc[i]

    drawings = design_page.get_drawings()

    for item in drawings:
        stroke_color = item.get("stroke") or (0, 0, 0)
        fill_color = item.get("fill")
        width = item.get("width") or 1
        paths = item.get("items")

        for path in paths:
            op = path[0]
            pts = path[1:]

            if op == "l":  # line
                pt1 = pts[0]
                pt2 = pts[1] if len(pts) > 1 else fitz.Point(pt1.x + 1, pt1.y)
                target_page.draw_line(pt1, pt2, color=stroke_color, width=width)

            elif op == "c":  # Bezier curves → approximate with circle or skip
                pt = pts[-1]
                target_page.draw_circle(center=pt, radius=1, color=stroke_color, fill=fill_color)

# Save back into same file
target_doc.save(target_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
print(f"✅ Design from A added into B at: {target_path}")