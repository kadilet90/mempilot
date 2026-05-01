
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
import pandas as pd
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt

app = FastAPI()

@app.get("/")
def home():
    return {"message": "MemPilot AI online server is running"}

@app.get("/app", response_class=HTMLResponse)
def app_ui():
    return """
    <html>
    <head>
        <title>MemPilot AI</title>
    </head>
    <body style="font-family:Arial; text-align:center; margin-top:90px; background:#f5f5f5;">
        <h1 style="font-size:44px;">🚀 MemPilot AI</h1>
        <p style="font-size:18px;">Find hidden GPU inefficiencies and reduce AI costs</p>

        <div style="background:white; padding:40px; width:430px; margin:auto; border-radius:14px;">
            <form action="/analyze" enctype="multipart/form-data" method="post">
                <input name="file" type="file" required>
                <br><br>
                <button type="submit" style="padding:13px 26px; background:black; color:white; border:none; border-radius:7px; font-weight:bold;">
                    Analyze & Save Money
                </button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)

    avg_used = df["used_mb"].mean()
    avg_reserved = df["reserved_mb"].mean()
    waste = avg_reserved - avg_used
    waste_percent = (waste / avg_reserved) * 100 if avg_reserved > 0 else 0
    savings = 2000 * (waste_percent / 100)
    efficiency_score = 100 - waste_percent

    if waste_percent > 50:
        risk = "Critical"
    elif waste_percent > 30:
        risk = "High"
    elif waste_percent > 15:
        risk = "Medium"
    else:
        risk = "Low"

    # Create graph
    graph_file = "graph.png"
    plt.figure(figsize=(10, 5))
    plt.plot(df["used_mb"], label="Used Memory")
    plt.plot(df["reserved_mb"], label="Reserved Memory")
    plt.legend()
    plt.title("GPU Memory Usage")
    plt.xlabel("Step")
    plt.ylabel("Memory (MB)")
    plt.savefig(graph_file)
    plt.close()

    # Create PDF
    pdf_file = "mempilot_online_report.pdf"
    c = canvas.Canvas(pdf_file)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 800, "MemPilot AI - GPU Cost Optimization Report")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 760, "Executive Summary")

    c.setFont("Helvetica", 11)
    c.drawString(50, 735, f"Average Used Memory: {round(avg_used, 2)} MB")
    c.drawString(50, 715, f"Average Reserved Memory: {round(avg_reserved, 2)} MB")
    c.drawString(50, 695, f"Detected Inefficiency: {round(waste_percent, 1)}%")

    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, 660, f"Estimated Monthly Cost Reduction: ${round(savings, 0)}+")
    c.drawString(50, 640, f"Efficiency Score: {round(efficiency_score, 1)}/100")
    c.drawString(50, 620, f"Risk Level: {risk}")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 585, "AI Recommendations")

    c.setFont("Helvetica", 11)
    c.drawString(50, 560, "- Enable FP16 / half precision where accuracy allows")
    c.drawString(50, 540, "- Increase batch size to improve GPU utilization")
    c.drawString(50, 520, "- Monitor reserved vs used GPU memory continuously")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 485, "Business Impact")

    c.setFont("Helvetica", 11)
    c.drawString(50, 460, "- Paying for unused GPU capacity")
    c.drawString(50, 440, "- Lower AI workload efficiency")
    c.drawString(50, 420, "- Higher infrastructure costs")

    c.drawImage(graph_file, 50, 150, width=500, height=240)

    c.save()

    return FileResponse(
        pdf_file,
        media_type="application/pdf",
        filename="mempilot_report.pdf"
    )
