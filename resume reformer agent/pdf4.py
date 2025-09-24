import fitz  # PyMuPDF
import json
import base64
import os

def get_color_hex(color):
    if isinstance(color, (tuple, list)):
        # Assume floats 0-1
        r = int(color[0] * 255)
        g = int(color[1] * 255)
        b = int(color[2] * 255)
    elif isinstance(color, int):
        r = (color >> 16) & 255
        g = (color >> 8) & 255
        b = color & 255
    else:
        # Unknown format — fallback black
        r, g, b = 0, 0, 0
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def rect_to_list(rect):
    if hasattr(rect, "rect"):  # rare nested case
        rect = rect.rect
    if hasattr(rect, "__iter__") and not isinstance(rect, str):
        # Rect or list-like object
        return [float(coord) for coord in rect]
    return [0, 0, 0, 0]  # fallback

def points_to_list(points):
    result = []
    for p in points:
        if hasattr(p, "x") and hasattr(p, "y"):
            result.append([float(p.x), float(p.y)])
        elif hasattr(p, "__iter__") and len(p) == 2:
            result.append([float(p[0]), float(p[1])])
    return result

def rects_intersect(rect1, rect2):
    # rect = [x0, y0, x1, y1]
    # Check if two rectangles overlap
    return not (rect1[2] < rect2[0] or rect1[0] > rect2[2] or rect1[3] < rect2[1] or rect1[1] > rect2[3])

def extract_pdf_details(pdf_path, json_path):
    doc = fitz.open(pdf_path)
    pdf_data = {
        "metadata": doc.metadata,
        "page_count": len(doc),
        "pages": []
    }

    output_dir = "extracted_images"
    os.makedirs(output_dir, exist_ok=True)

    for page_num in range(len(doc)):
        page = doc[page_num]
        page_info = {
            "page_number": page_num + 1,
            "size": {"width": page.rect.width, "height": page.rect.height},
            "blocks": [],
            "images": [],
            "annotations": [],
            "links": [],
            "drawings": []
        }

        links = page.get_links()

        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                block_data = {
                    "bbox": list(block["bbox"]),  # rect to list
                    "lines": []
                }
                for line in block["lines"]:
                    spans = []
                    for span in line["spans"]:
                        span_bbox = list(span["bbox"])

                        # Try to find link overlapping this span bbox
                        span_link = None
                        for link in links:
                            # link bbox may be under key 'from' or 'bbox'
                            link_rect = None
                            if "from" in link:
                                link_rect = link["from"]  # (x0, y0, x1, y1)
                            elif "bbox" in link:
                                link_rect = link["bbox"]

                            if link_rect and rects_intersect(span_bbox, link_rect):
                                if link.get("uri"):
                                    span_link = {"type": "external", "uri": link["uri"]}
                                elif link.get("page") is not None:
                                    span_link = {"type": "internal", "page": link["page"]}
                                break  # stop after first matching link

                        spans.append({
                            "text": span["text"],
                            "font": span["font"],
                            "size": span["size"],
                            "color": get_color_hex(span["color"]),
                            "bbox": span_bbox,
                            "alignment": "center" if abs(span_bbox[0] - (page.rect.width / 2)) < 20 else "left" if
                            span_bbox[0] < (page.rect.width / 2) else "right",
                            **({"link": span_link} if span_link else {})  # Add link if found
                        })
                    block_data["lines"].append(spans)
                page_info["blocks"].append(block_data)

        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            image_ext = base_image["ext"]
            image_filename = f"{output_dir}/page{page_num+1}_img{img_index+1}.{image_ext}"
            with open(image_filename, "wb") as img_file:
                img_file.write(image_bytes)

            image_base64 = base64.b64encode(image_bytes).decode("utf-8")

            page_info["images"].append({
                "xref": xref,
                "width": img[2],
                "height": img[3],
                "bpc": img[4],
                "base64": image_base64,
                "filename": image_filename
            })

        # Annotations
        for annot in page.annots() or []:
            page_info["annotations"].append(annot.info)

        # Links (page-level summary)
        for link in links:
            if link.get("uri"):
                page_info["links"].append({"type": "external", "uri": link["uri"]})
            elif link.get("page") is not None:
                page_info["links"].append({"type": "internal", "page": link["page"]})

        # Drawings (lines, rects, curves, polygons, etc)
        drawings = page.get_drawings(extended=True)
        for d in drawings:
            rect = rect_to_list(d.get("rect", []))
            points = points_to_list(d.get("points", []))

            # Filter out empty or invalid shapes
            if rect == [0.0, 0.0, 0.0, 0.0] and not points:
                continue  # Skip useless drawings

            drawing_obj = {
                "type": d.get("type", ""),
                "rect": rect,
                "points": points,
                "fill": get_color_hex(d.get("fill")) if d.get("fill") else None,
                "color": get_color_hex(d.get("color")) if d.get("color") else None,
                "width": d.get("width", 1),
                "fill_opacity": d.get("fill_opacity"),
                "stroke_opacity": d.get("stroke_opacity")
            }
            page_info["drawings"].append(drawing_obj)

        pdf_data["pages"].append(page_info)

    doc.close()

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(pdf_data, f, indent=4)

    print(f"\n✅ PDF details with drawings and embedded links saved to '{json_path}'")


extract_pdf_details(r"C:\Users\abhiv\OneDrive\Desktop\agentic ai\info-redaction agent\test_pdf.pdf","pii.json")

