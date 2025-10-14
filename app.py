from services.slack_handler import app

if __name__=="__main__":
    print("Slack bot running on port 3000 teen-hazar...")
    app.start(port=3000, path="/slack/events", host="0.0.0.0")

