from slack_bolt import App
import config, requests, io, csv,os
from threading import Thread
from services.keyword_manager import parse_input, clean_keywords
from services.db_manager import save_keywords, save_clusters, supabase
from services.embeddings import make_clusters
from services.outline_generator import generate_outline_with_idea
import pandas as pd
from services.pdf_report import make_pdf

app = App(token=config.SLACK_BOT_TOKEN, signing_secret=config.SLACK_SIGNING_SECRET)


@app.command("/upload_keywords")
def upload_keywords_all(ack, respond, command):
    ack()
    user = command["user_id"]
    text = command.get("text", "").strip()
    respond("🚀 Starting upload + cluster pipeline...")

    def work():
        try:
            if text:
                raw = parse_input(text)
            else:
                try:
                    respond("Detected CSV upload, reading file...")
                    file_info = command["files"][0]
                    url = file_info["url_private_download"]
                    headers = {"Authorization": f"Bearer {config.SLACK_BOT_TOKEN}"}
                    r = requests.get(url, headers=headers, timeout=15)
                    r.raise_for_status()
                
                    df = pd.read_csv(io.StringIO(r.text), header=None, dtype=str)

                    vals = df.fillna("").astype(str).values.flatten().tolist()
                    vals = [v.strip() for v in vals if v and v.strip()!=""]
                    csv_text = ", ".join(vals)

                    raw = parse_input(csv_text)

                except Exception as e:
                    respond(f"File read error: {e}")
                    return


   
            cleaned = clean_keywords(raw)
            save_keywords(user, raw, cleaned)
            respond(f"✅ Step 1: Uploaded!\nRaw: {len(raw)} | Cleaned: {len(cleaned)}\n{cleaned}")

            # ---------- STEP 3: CLUSTER ----------
            respond("Step 2: Clustering keywords")
            groups = make_clusters(cleaned)
            save_clusters(user, groups)

            msg = "✅ Step 2: Clusters created:\n"
            for g, words in groups.items():
                msg += f"*{g}:* {', '.join(words)}\n"
            respond(msg)

        except Exception as e:
            respond(f"Error: {e}")

    Thread(target=work).start()


@app.command("/generate_outline")
def generate_outline_cmd(ack,respond,command):
    ack()
    user=command["user_id"]
    respond("generating outlines + ideas")

    def work():
        # res=supabase.table("keywords").select("clusters").eq("user_id",user).order("id",desc=True).limit(1).execute()
        res = supabase.table("keywords").select("raw_keywords, cleaned_keywords, clusters").eq("user_id",user).order("id",desc=True).limit(1).execute()
        if len(res.data)==0:
            respond("no clusters found. run /cluster_keywords first")
            return
        clusters=res.data[0]["clusters"]
        from services.outline_generator import generate_outline_with_idea
        outlines=generate_outline_with_idea(clusters)
        supabase.table("keywords").update({"outlines":outlines}).eq("user_id",user).execute()
        msg="✅ Outlines + Ideas generated:\n"
        for c,o in outlines.items():
            msg+=f"*{c}*\nIntro: {o['intro']}\nSections: {', '.join(o['sections'])}\nConclusion: {o['conclusion']}\n💡Idea: {o['idea']}\n\n"
        respond(msg)

    from threading import Thread
    t=Thread(target=work)
    t.start()


@app.command("/generate_report")
def generate_report_cmd(ack, respond, command):
    ack()
    user = command["user_id"]
    respond("📄 generating report... please wait 10 sec")

    def work():
        res = supabase.table("keywords").select("raw_keywords, cleaned_keywords, clusters, outlines").eq("user_id",user).order("id",desc=True).limit(1).execute()

        if len(res.data) == 0 or not res.data[0].get("outlines"):
            respond("No complete data (outlines/ideas) found for a report. Run /generate_outline first.")
            return
        data = {
            "raw_keywords": res.data[0].get("raw_keywords",[]),
            "cleaned_keywords": res.data[0].get("cleaned_keywords",[]),
            "clusters": res.data[0].get("clusters",{}),
            "outlines": res.data[0].get("outlines",{})
        }
        try:
            pdf_path=make_pdf(user,data)
            with open(pdf_path,"rb") as f:
                app.client.files_upload_v2(
                    channel=command["channel_id"],
                    title="Content Pipeline Report",
                    file=f,
                    filename=os.path.basename(pdf_path),
                    initial_comment="Here’s your detailed report with all keywords, clusters, outlines & ideas 👇"
                )
            respond("Report generation and upload complete!")
        except Exception as e:
            respond(f"PDF generation/upload error: {e}")

    from threading import Thread
    t=Thread(target=work)
    t.start()
