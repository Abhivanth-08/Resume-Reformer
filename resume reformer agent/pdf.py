import fitz  # PyMuPDF
import json

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255
    return (r, g, b)

def create_pdf_from_json(json_path, output_pdf_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    doc = fitz.open()

    for page_index, page_data in enumerate(data.get("pages", [])):
        width = page_data.get("size", {}).get("width", 595.5)
        height = page_data.get("size", {}).get("height", 842.25)
        page = doc.new_page(width=width, height=height)

        for block in page_data.get("blocks", []):
            for line in block.get("lines", []):
                if not line:
                    continue
                for span in line:
                    text = span.get("text", "")
                    size = span.get("size", 11)
                    fontname = span.get("font", "").lower()
                    color = hex_to_rgb(span.get("color", "#000000"))

                    x = span["bbox"][0]
                    y = span["bbox"][1]

                    # Detect style
                    if "bold" in fontname:
                        font = "Times-Bold"
                    elif "italic" in fontname:
                        font = "Times-Italic"
                    else:
                        font = "Times-Roman"

                    # Draw the text
                    page.insert_text(
                        (x, y),
                        text,
                        fontsize=size,
                        fontname=font,
                        color=color,
                        overlay=True
                    )

                    # Add link annotation if present in span
                    link = span.get("link")
                    if link:
                        # span bbox
                        rect = fitz.Rect(span["bbox"])

                        if link.get("type") == "external" and "uri" in link:
                            # external URI link
                            page.insert_link({
                                "kind": fitz.LINK_URI,
                                "from": rect,
                                "uri": link["uri"]
                            })
                        elif link.get("type") == "internal" and "page" in link:
                            # internal page link (0-based page index)
                            target_page = link["page"]
                            if 0 <= target_page < doc.page_count:
                                page.insert_link({
                                    "kind": fitz.LINK_GOTO,
                                    "from": rect,
                                    "page": target_page
                                })

        # Drawings
        for drawing in page_data.get("drawings", []):
            draw_type = drawing.get("type", "")
            rect = drawing.get("rect", [0, 0, 0, 0])
            points = drawing.get("points", [])
            width = drawing.get("width", 1.0)
            color = hex_to_rgb(drawing.get("color", "#000000")) if drawing.get("color") else None
            fill = hex_to_rgb(drawing.get("fill", "#000000")) if drawing.get("fill") else None

            # Skip empty/dummy shapes
            if rect == [0, 0, 0, 0] and not points:
                continue

            if draw_type in ["rect", "f", "s"]:
                r = fitz.Rect(rect)
                if fill and not color:
                    page.draw_rect(r, fill=fill, color=None)
                elif color and not fill:
                    page.draw_rect(r, color=color, width=width)
                elif color and fill:
                    page.draw_rect(r, color=color, fill=fill, width=width)

            elif draw_type == "line" and len(points) >= 2:
                p1 = fitz.Point(*points[0])
                p2 = fitz.Point(*points[1])
                page.draw_line(p1, p2, color=color, width=width)

            elif draw_type == "curve" and len(points) >= 4:
                path = page.new_shape()
                path.move_to(*points[0])
                path.curve_to(*points[1], *points[2], *points[3])
                path.finish(color=color, width=width)
                path.commit()

            elif draw_type in ["polyline", "polygon"] and len(points) >= 2:
                shape = page.new_shape()
                shape.move_to(*points[0])
                for pt in points[1:]:
                    shape.line_to(*pt)
                if draw_type == "polygon":
                    shape.close()
                shape.finish(color=color, fill=fill, width=width)
                shape.commit()

    doc.save(output_pdf_path)
    doc.close()
    print(f"✅ PDF recreated with designs and links: {output_pdf_path}")


create_pdf_from_json("old_det2.json","suma.pdf")