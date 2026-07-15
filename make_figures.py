"""make_figures.py — generates publishable figures for the term paper.
Fig 1: System architecture (data -> ML pipeline -> web app -> farmer).
Fig 2: Model benchmark bar chart (R2 of 7 models, real data).
Fig 3: Workflow of the recommendation engine.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({"font.family": "serif", "font.size": 10})

# ---------- FIG 1: Architecture ----------
fig, ax = plt.subplots(figsize=(7.2, 3.4))
boxes = [
    (0.02, 0.38, 0.20, 0.24, "Real Agricultural\nDataset\n(186,323 recs,\n104 crops)", "#2e7d32"),
    (0.27, 0.38, 0.20, 0.24, "Pre-processing\nClean · Encode\nFeature schema", "#1565c0"),
    (0.52, 0.55, 0.20, 0.24, "Model Training\n7 regressors\nbenchmarked", "#6a1b9a"),
    (0.52, 0.20, 0.20, 0.24, "Best Model\n(KNN, R2=0.783)\njoblib", "#ad1457"),
    (0.78, 0.38, 0.20, 0.24, "Flask Web App\nPredict · Recommend\nAdvise", "#ef6c00"),
]
for x, y, w, h, label, c in boxes:
    ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=c, alpha=0.85,
                              edgecolor="black", linewidth=1.0))
    ax.text(x + w/2, y + h/2, label, ha="center", va="center",
            color="white", fontsize=8.5, weight="bold")
# arrows
arrows = [((0.22,0.50),(0.27,0.50)), ((0.47,0.50),(0.52,0.67)),
          ((0.47,0.50),(0.52,0.32)), ((0.72,0.50),(0.78,0.50))]
for (x1,y1),(x2,y2) in arrows:
    ax.annotate("", xy=(x2,y2), xytext=(x1,y1),
                arrowprops=dict(arrowstyle="->", color="black", lw=1.3))
ax.text(0.40, 0.86, "Farmer input: Crop, Soil, Rainfall, Temp, Humidity, pH, NPK",
         ha="center", fontsize=8, style="italic", color="#333")
ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
ax.set_title("Fig. 1. Proposed system architecture for AI-based crop yield prediction.",
             fontsize=10, weight="bold", pad=6)
plt.tight_layout()
plt.savefig("fig1_architecture.png", dpi=200, bbox_inches="tight")
plt.close()

# ---------- FIG 2: Benchmark ----------
models = ["Linear\nReg","Decision\nTree","Random\nForest","Gradient\nBoost","KNN","XGBoost"]
r2 = [0.115, 0.732, 0.685, 0.643, 0.783, 0.346]
colors = ["#b0bec5","#4db6ac","#4db6ac","#4db6ac","#e53935","#b0bec5"]
fig, ax = plt.subplots(figsize=(7.2, 3.2))
bars = ax.bar(models, r2, color=colors, edgecolor="black", linewidth=0.8)
bars[4].set_color("#c62828")  # highlight best
for b, v in zip(bars, r2):
    ax.text(b.get_x()+b.get_width()/2, v+0.01, f"{v:.3f}",
            ha="center", va="bottom", fontsize=8.5, weight="bold")
ax.set_ylim(0, 0.9)
ax.set_ylabel("Test R\u00b2 (higher is better)")
ax.set_title("Fig. 2. Regression-model benchmark on real yield data (n=186,323).",
             fontsize=10, weight="bold")
ax.axhline(0.783, ls="--", color="#c62828", lw=1, alpha=0.6)
ax.text(4.4, 0.80, "Best: KNN (R\u00b2=0.783)", color="#c62828",
         fontsize=8, weight="bold")
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig("fig2_benchmark.png", dpi=200, bbox_inches="tight")
plt.close()

# ---------- FIG 3: Recommendation workflow ----------
fig, ax = plt.subplots(figsize=(7.2, 2.6))
steps = ["Soil + Env\nInputs","For each crop:\npredict yield","Rank by\npredicted yield","Top-3\nrecommended\ncrops"]
x0 = 0.05
for i, s in enumerate(steps):
    ax.add_patch(plt.Rectangle((x0+i*0.24, 0.3), 0.19, 0.4,
                               facecolor="#2e7d32", alpha=0.85,
                               edgecolor="black", lw=1))
    ax.text(x0+i*0.24+0.095, 0.5, s, ha="center", va="center",
            color="white", fontsize=8.5, weight="bold")
    if i < 3:
        ax.annotate("", xy=(x0+(i+1)*0.24, 0.5), xytext=(x0+i*0.24+0.19, 0.5),
                    arrowprops=dict(arrowstyle="->", color="black", lw=1.3))
ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
ax.set_title("Fig. 3. Crop-recommendation workflow (top-3 by predicted yield).",
             fontsize=10, weight="bold", pad=6)
plt.tight_layout()
plt.savefig("fig3_recommend.png", dpi=200, bbox_inches="tight")
plt.close()

print("Figures generated: fig1_architecture.png, fig2_benchmark.png, fig3_recommend.png")
