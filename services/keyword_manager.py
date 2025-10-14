import re,io,csv

def parse_input(text):
    if isinstance(text,bytes):
        try:
            decoded = text.decode("utf-8")
            csv_text = ""
            for row in csv.reader(io.StringIO(decoded)):
                csv_text += ", ".join(row) + ", "
            text = csv_text
        except Exception as e:
            print("csv parse err:",e)
            text = ""
    kws = re.split(r"[\n,]+",text)
    return [k.strip() for k in kws if k.strip()]

def clean_keywords(keywords):
    seen = set()
    cleaned = []
    for k in keywords:
        k = k.strip().lower()
        k = re.sub(r"[^a-z0-9\s]", "", k)
        if k != "" and k not in seen:
            cleaned.append(k)
            seen.add(k)
    return cleaned


