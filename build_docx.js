// Build Smart_Farming_Term_Paper_v4.docx using docx-js (per docx skill rules)
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, Header, Footer, AlignmentType, LevelFormat, HeadingLevel,
  BorderStyle, WidthType, ShadingType, PageNumber, PageBreak, ExternalHyperlink
} = require("docx");

const IMG = (p, w, h) => new ImageRun({
  type: "png", data: fs.readFileSync(p),
  transformation: { width: w, height: h },
  altText: { title: p, description: p, name: p }
});

const body = [];

// Title block
body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [
  new TextRun({ text: "AI-Based Crop Yield Prediction and Crop Recommendation for Smart Agriculture", bold: true, size: 32, font: "Arial" })
]}));
body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: [
  new TextRun({ text: "A Machine-Learning Framework with Explainable Advisory", italics: true, size: 24, font: "Arial" })
]}));
body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [
  new TextRun({ text: "[Your Name] · [Roll No.] · [Department] · [College Name]", size: 20, font: "Arial" })
]}));

// Section helper
function h1(t){ return new Paragraph({ heading: HeadingLevel.HEADING_1, spacing:{before:240,after:120}, children:[new TextRun({text:t, font:"Arial"})] }); }
function h2(t){ return new Paragraph({ heading: HeadingLevel.HEADING_2, spacing:{before:160,after:80}, children:[new TextRun({text:t, font:"Arial"})] }); }
function p(t, opts={}){ return new Paragraph({ alignment: opts.center?AlignmentType.CENTER:AlignmentType.JUSTIFIED, spacing:{after:120}, children:[new TextRun({text:t, size:20, font:"Arial"})] }); }
function bullet(t){ return new Paragraph({ numbering:{reference:"bullets",level:0}, spacing:{after:60}, children:[new TextRun({text:t, size:20, font:"Arial"})] }); }
function numbered(t){ return new Paragraph({ numbering:{reference:"numbers",level:0}, spacing:{after:60}, children:[new TextRun({text:t, size:20, font:"Arial"})] }); }

// Abstract
body.push(h1("Abstract"));
body.push(p("Accurate, pre-harvest estimation of crop yield is a cornerstone of food security and of the economic resilience of smallholder farmers, particularly in developing agrarian economies where access to agronomic expertise is scarce. Recent comprehensive reviews of machine learning (ML) in precision agriculture emphasize a pronounced shift from process-based crop-growth simulation toward data-driven learning, yet most deployed tools remain inaccessible to resource-constrained farmers. This paper proposes an integrated, low-cost decision-support framework that (i) predicts crop yield (tons per hectare) from crop identity, soil type, and environmental parameters—rainfall, temperature, humidity, soil pH, and macronutrient levels (N, P, K); (ii) evaluates crop–soil suitability; (iii) quantifies prediction confidence; (iv) generates explainable yield-improvement advisories; and (v) ranks the three most productive crops for a given soil profile. Seven regression algorithms are trained and benchmarked on a real, publicly available multi-crop agricultural dataset of 186,323 records spanning 104 crops. Results show that the K-Nearest-Neighbours regressor attains the strongest generalization (R² = 0.783, RMSE = 510.53). A model-agnostic feature-importance analysis (permutation importance) is further performed to interpret the drivers of prediction, and a hybrid ML–rule advisory layer is introduced to keep recommendations actionable. The framework demonstrates that transparent, explainable artificial intelligence can deliver practical yield guidance to rural farmers through a lightweight web interface."));
body.push(new Paragraph({ spacing:{before:80, after:160}, children:[ new TextRun({text:"Index Terms: ", bold:true, size:20, font:"Arial"}), new TextRun({text:"crop yield prediction, precision agriculture, machine learning, regression, explainable AI, decision-support system, crop recommendation, feature importance.", size:20, font:"Arial"}) ] }));

// 1 Introduction
body.push(h1("1. Introduction"));
body.push(p("Agriculture sustains a large share of the global population, yet yield outcomes are acutely sensitive to the congruence between crop, soil, and environment [1]. Conventional yield forecasting has long depended on process-based crop-growth models such as DSSAT and ORYZA, which encode physiological mechanisms but demand meticulous, locality-specific calibration that smallholders cannot supply [2]. In parallel, the proliferation of digital data—from sensors, satellites, weather stations, and farm equipment—has positioned agriculture as a canonical “big data” domain spanning volume, variety, velocity, and veracity [3]."));
body.push(p("A 2024 comprehensive review of ML approaches for precision farming documents this transition explicitly: it reports deep learning (61 mentions) and IoT (49 mentions) as the dominant themes, with support-vector machines (19), neural networks (41), CNNs (28), and KNN (10) constituting the principal methodological toolkit, while yield prediction appears as a recurrent application thread (11 mentions) [1]. The review further catalogs ML applications across crop yield prediction, disease detection, and resource optimization, and stresses that interpretability and field-level validation remain open frontiers [1]."));
body.push(p("Against this backdrop, the motivation of the present work is twofold. First, to enable any farmer—irrespective of formal agronomic training—to obtain an estimate of expected yield and a ranking of suitable crops from only readily observable parameters, via a simple web interface. Second, to do so transparently: the advisory output (e.g., nutrient remediation) must be interpretable rather than a black box, addressing the “explainability frontier” flagged by the literature [1]."));
body.push(h2("Principal Contributions"));
numbered("A reproducible pipeline that ingests a real multi-crop yield dataset, cleans it, and trains and benchmarks seven regression models under a fixed protocol.");
numbered("A model-agnostic feature-importance analysis (permutation importance) that interprets the drivers of yield prediction—addressing the interpretability gap noted in recent reviews [1].");
numbered("A deployed web application returning yield prediction, crop–soil suitability, confidence, and agronomic suggestions, augmented with a top-three crop-recommendation mode.");
numbered("A hybrid ML–rule advisory layer that fuses data-driven prediction with domain knowledge for actionable, field-ready guidance.");
body.push(p("The remainder is organized as follows. Section 2 reviews related work. Section 3 describes the dataset and pre-processing. Section 4 presents the methodology, including the advisory layer. Section 5 reports experimental results and the importance analysis. Section 6 discusses applications, limitations, and social impact. Section 7 concludes."));

// 2 Related Work
body.push(h1("2. Related Work"));
body.push(p("Crop yield prediction has evolved from statistical regression toward learning-based paradigms. Process-based models (DSSAT, ORYZA, APSIM) simulate crop physiology but require laborious local calibration [2]. Data-driven models circumvent this by learning input–output mappings directly from observations."));
body.push(p("A representative study developed a crop-yield estimation model from soil and environmental parameters (temperature, humidity, rainfall, pH, pesticide usage) on a ten-year tea-plantation dataset, employing an ensemble of neural networks and reporting R² = 0.946 [2]. Other work fused soil microscopy imagery with portable X-ray fluorescence spectrometry and auxiliary variables through Random Forest, improving soil-fertility prediction (R² = 0.70–0.88) [4]. At the systems level, agricultural data warehousing has been proposed as the foundation for decision-support and recommendation under the precision-agriculture paradigm [3]."));
body.push(p("More recent efforts broaden the toolkit. Quantile random forests have been applied to probabilistic crop-yield forecasting, explicitly modeling weather uncertainty [5]. A study analyzing Indian yields (1997–2020) benchmarked Naïve Bayes against Random Forest, underscoring the value of classical learners on national statistics [6]. The “digital twin” paradigm—coupling weather APIs, GPS, and NPK soil sensing—has been shown to support optimal-yield crop recommendation within Agriculture 4.0 [7]. Remote sensing combined with deep learning (e.g., CNN-based canopy analysis) is increasingly used for scalable, pre-harvest yield estimation [8]."));
body.push(p("Relative to these efforts, the present work targets a broader, multi-crop setting (104 crops) on an open dataset, foregrounds deployability through a lightweight web interface, and uniquely couples prediction with an explainable recommendation and advisory layer. Whereas [1] surveys the field and [2], [4]–[8] advance individual estimators, our contribution is an integrated, publicly reproducible decision-support artifact with explicit interpretability."));

// 3 Dataset
body.push(h1("3. Dataset and Pre-processing"));
body.push(h2("3.1 Data Provenance"));
body.push(p("The study employs a real, publicly available agricultural statistics dataset [9] comprising Indian state- and district-level crop records with the attributes: State, District, Crop Year, Season, Crop, Area, Production, annual rainfall, measured yield, Soil Type, and Soil pH. After cleaning, 186,323 records covering 104 distinct crops were retained. Critically, the target variable is a measured quantity (Production ÷ Area, in tons per hectare), not a synthetically generated label."));
body.push(h2("3.2 Feature Schema and Farmer-Practical Input Design"));
body.push(p("Inputs were mapped to the ten-field project schema. A smallholder cannot measure pH, NPK, temperature, humidity, or rainfall in the field, and the app cannot infer their region by magic. Therefore the interface requires only Crop and Soil Type—both farmer-known. Region is captured explicitly via two complementary mechanisms: (i) a State selector (authoritative, like every government agri portal—mKisan, IMD), and (ii) an optional GPS “Use my location” button that reads browser/phone coordinates and maps them to the nearest state centroid (offline, no API). Each selected state’s real, dataset-derived average rainfall auto-fills the weather default. The remaining soil parameters are auto-filled from real regional/typical per-crop values (derived from dataset [10]); pH/N/P/K stand in for the government Soil Health Card, and rainfall/temperature/humidity for IMD open data. A farmer who possesses their own Soil Health Card may override any default for a plot-specific prediction. Yield remains the model’s output, never an input."));
body.push(p("Limitation (stated explicitly). The auto-filled parameters are district/state-level aggregates, not farm-level measurements; GPS→state uses coarse centroids. They represent a regional expectation of yield, not plot-level truth; accuracy improves when a farmer supplies their own soil-test values."));
body.push(h2("3.3 Pre-processing"));
body.push(p("Records with missing or non-positive values were removed; all features were coerced to numeric type; the categorical fields Crop and Soil_Type were label-encoded. For computational tractability a 40,000-row random subsample (random_state = 42) was used for model training, preserving the real distribution."));

// 4 Methodology
body.push(h1("4. Methodology"));
body.push(h2("4.1 Benchmarked Models"));
numbered("Linear Regression (LR)"); numbered("Decision Tree (DT)"); numbered("Random Forest (RF)"); numbered("Gradient Boosting (GB)"); numbered("K-Nearest-Neighbours (KNN)"); numbered("XGBoost (XGB)");
body.push(p("Support Vector Regression was excluded at this scale owing to its superlinear training cost on large samples—consistent with the observation in [1] that tree/neighbor methods dominate practical agriculture deployments."));
body.push(h2("4.2 Evaluation Protocol"));
body.push(p("A stratified 80/20 train–test split (random_state = 42) was used. Models were scored by coefficient of determination (R²), mean absolute error (MAE), and root-mean-square error (RMSE). The model with the highest test R² was serialized (joblib) and deployed."));
body.push(h2("4.3 Explainable Feature-Importance Analysis"));
body.push(p("To address the interpretability frontier identified in [1], we computed permutation importance on the held-out test set for the best model: each feature is shuffled independently and the resulting increase in RMSE quantifies its predictive contribution. This model-agnostic procedure yields a ranking of drivers that a farmer or agronomist can scrutinize."));
body.push(h2("4.4 Hybrid ML–Rule Advisory Layer"));
bullet("A crop–soil compatibility table flags unsuitable pairings.");
bullet("Soil pH outside [5.0, 8.5] triggers liming or acidification advice.");
bullet("Deficient N, P, or K trigger specific fertilizer recommendations.");
bullet("Rainfall extremes trigger irrigation or drainage guidance.");
body.push(p("This preserves explainability for non-technical end users while grounding suggestions in both data and agronomy."));
body.push(h2("4.5 Crop Recommendation"));
body.push(p("For a given soil and condition profile, the system predicts the yield of every known crop and returns the three with the highest predicted yield, functioning as a crop-selection advisor (Fig. 3)."));

// 5 Results
body.push(h1("5. Experimental Results"));
body.push(h2("5.1 Model Benchmark"));
body.push(p("Table I reports test-set performance."));
// Table I
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const hdr = (t) => new TableCell({ borders, shading:{fill:"D5E8F0", type:ShadingType.CLEAR}, margins:{top:60,bottom:60,left:100,right:100}, width:{size:2340,type:WidthType.DXA}, children:[new Paragraph({children:[new TextRun({text:t, bold:true, size:20, font:"Arial"})]})] });
const cell = (t, b=false) => new TableCell({ borders, margins:{top:60,bottom:60,left:100,right:100}, width:{size:2340,type:WidthType.DXA}, children:[new Paragraph({alignment:AlignmentType.CENTER, children:[new TextRun({text:t, bold:b, size:20, font:"Arial"})]})] });
const rows = [
  new TableRow({ children:[hdr("Model"),hdr("R²"),hdr("MAE"),hdr("RMSE")] }),
  new TableRow({ children:[cell("Linear Regression"),cell("0.115"),cell("154.23"),cell("1030.23")] }),
  new TableRow({ children:[cell("Decision Tree"),cell("0.732"),cell("29.55"),cell("566.95")] }),
  new TableRow({ children:[cell("Random Forest"),cell("0.685"),cell("30.82"),cell("614.26")] }),
  new TableRow({ children:[cell("Gradient Boosting"),cell("0.643"),cell("44.35"),cell("654.21")] }),
  new TableRow({ children:[cell("KNN",true),cell("0.783",true),cell("30.08",true),cell("510.53",true)] }),
  new TableRow({ children:[cell("XGBoost"),cell("0.346"),cell("36.51"),cell("885.76")] }),
];
body.push(new Table({ width:{size:9360,type:WidthType.DXA}, columnWidths:[2340,2340,2340,2340], rows }));
body.push(new Paragraph({ spacing:{before:60, after:120}, children:[ new TextRun({text:"TABLE I. MODEL BENCHMARK (REAL DATA; n = 186,323 CLEANED; 40k TRAIN)", bold:true, size:18, font:"Arial"}) ] }));
body.push(new Paragraph({ children:[ IMG("fig2_benchmark.png", 520, 300) ] }));
body.push(new Paragraph({ alignment:AlignmentType.CENTER, spacing:{after:160}, children:[ new TextRun({text:"Fig. 2. Regression-model benchmark on real yield data. KNN (highlighted) attains the highest R².", italics:true, size:18, font:"Arial"}) ] }));

body.push(h2("5.2 Interpretation of the Benchmark"));
body.push(p("Measured yield is governed by numerous latent factors (pest pressure, sowing date, management practice) not represented in the available features; a moderate-but-honest R² ≈ 0.78 is therefore expected and acceptable for a decision-support tool. Tree- and neighbour-based methods substantially outperform linear regression and XGBoost on this dataset, consistent with the prevalence of tree/instance-based methods reported in the precision-agriculture literature [1]."));
body.push(h2("5.3 Feature-Importance Analysis"));
body.push(p("Permutation importance on the test set (RMSE increase when a feature is shuffled) yields the following driver ranking: Rainfall (667.2), Crop (441.8), Nitrogen (73.2), Phosphorus (22.1), Humidity (10.3), with Temperature, K, pH, and Soil Type contributing negligibly (≈ 0 or negative, i.e., noise). This aligns with agronomic intuition—seasonal rainfall and crop species dominate yield potential—and supplies the interpretability that recent reviews flag as essential [1]."));
body.push(h2("5.4 Illustrative Predictions and Recommendation"));
body.push(p("Sample deployed-model outputs (t/ha) exhibit plausible, crop-differentiated behaviour: Rice (Loamy, 1200 mm, pH 6.5) ≈ 1.40; Wheat (Loamy, 600 mm, pH 7.0) ≈ 2.40; Maize (Loamy, 800 mm, pH 6.5) ≈ 6.60; Cotton (Black, 700 mm, pH 7.8) ≈ 1.00. Under a Black-soil profile the recommendation mode ranked Tea, Tapioca, and Sweet Potato as the leading three, evidencing soil-aware ranking. The end-to-end architecture is summarized in Fig. 1 and the recommendation workflow in Fig. 3."));
body.push(new Paragraph({ children:[ IMG("fig1_architecture.png", 560, 320) ] }));
body.push(new Paragraph({ alignment:AlignmentType.CENTER, spacing:{after:160}, children:[ new TextRun({text:"Fig. 1. Proposed system architecture: real data → pre-processing → model training/benchmark → best model → Flask web app delivering prediction, recommendation, and advisory to the farmer.", italics:true, size:18, font:"Arial"}) ] }));
body.push(new Paragraph({ children:[ IMG("fig3_recommend.png", 560, 320) ] }));
body.push(new Paragraph({ alignment:AlignmentType.CENTER, spacing:{after:160}, children:[ new TextRun({text:"Fig. 3. Crop-recommendation workflow: for a soil+environment profile, predict every crop's yield, rank, and return the top three.", italics:true, size:18, font:"Arial"}) ] }));

// 6 Discussion
body.push(h1("6. Discussion: Applications, Limitations, and Social Impact"));
body.push(h2("6.1 Applications and Social Impact"));
body.push(p("The framework is a low-cost, data-driven decision-support instrument for smallholder and rural farmers with limited access to agronomic counsel. Concrete benefits include: (i) identification of soil-appropriate crops via the top-three recommendation feature; (ii) avoidance of wasted inputs and lost growing seasons through a pre-sowing check; (iii) advance income estimation to inform crop comparison; (iv) free, specific soil advisories (e.g., “apply urea”, “add lime”) that otherwise require scarce paid soil-testing; (v) delivery through a simple web interface usable at a village smartphone or extension centre; and (vi) reduction of dependence on potentially biased input-seller advice."));
body.push(h2("6.2 Limitations"));
numbered("Regional, not farm-level, inputs. The auto-filled parameters are district-level aggregates (IMD, Soil Health Card, NBSS&LUP), not plot-specific measurements. Accuracy improves when a farmer supplies their own Soil Health Card values, and future work includes farm-level IoT soil sensing.");
numbered("Moderate absolute accuracy. R² ≈ 0.78 reflects missing latent factors (pest pressure, sowing date, management); the tool is a decision aid, not a substitute for field agronomy.");
numbered("Prototype scope. The build uses aggregated real data; genuine village deployment needs local/regional training data, a multilingual mobile interface, and offline operation.");
body.push(p("These limitations double as a research agenda and are stated explicitly to meet the scrutiny called for in recent ML-validation guidance [11]."));

// 7 Conclusion
body.push(h1("7. Conclusion and Future Work"));
body.push(p("This paper demonstrated that machine learning can predict crop yield from real soil and rainfall data with moderate-but-useful accuracy and furnish actionable, explainable farmer guidance. The deployed KNN model (R² = 0.783) confirms that a lightweight, interpretable approach yields meaningful decision support; the top-three recommendation mode and the hybrid ML–rule advisory further equip the system as a crop-selection advisor. A permutation-importance analysis supplied the interpretability absent in many field tools."));
body.push(p("Future directions: (a) integration of a unified dataset with all ten fields measured jointly; (b) recommendation ranking informed by empirical per-crop/per-soil mean yields; (c) a multilingual, mobile-first interface; (d) offline capability for low-connectivity regions; (e) incorporation of seasonal weather forecasts and pest-risk signals; and (f) extension to probabilistic (quantile) yield forecasting as in [5]."));

// References
body.push(h1("References"));
const refs = [
  "[1] G. Mohyuddin, M. A. Khan, A. Haseeb, S. Mahpara, M. Waseem, and A. M. Saleh, “Evaluation of Machine Learning Approaches for Precision Farming in Smart Agriculture System: A Comprehensive Review,” IEEE Access, vol. 12, pp. 1–25, 2024, doi: 10.1109/ACCESS.2024.3390581.",
  "[2] A. Rehman et al., “Development of crop yield estimation model using soil and environmental parameters,” 2021. [Online]. Available: https://arxiv.org/abs/2102.05755",
  "[3] D. C. et al., “An efficient data warehouse for crop yield prediction,” in Proc. IEEE Int. Conf. Big Data, 2018. [Online]. Available: https://arxiv.org/abs/1807.00035",
  "[4] R. Das et al., “Prediction of soil fertility parameters using USB-microscope imagery and portable X-ray fluorescence spectrometry,” 2024. [Online]. Available: https://arxiv.org/abs/2404.12415",
  "[5] “Crop yield probability density forecasting via quantile random forest and Epanechnikov kernel function,” 2023. [Online]. Available: https://arxiv.org/abs/2304.05172",
  "[6] “Naïve Bayes and Random Forest for Crop Yield Prediction,” 2022. [Online]. Available: https://arxiv.org/abs/2206.12329",
  "[7] “Precision Agriculture Revolution: Integrating Digital Twins and Advanced Crop Recommendation for Optimal Yield,” 2024. [Online]. Available: https://arxiv.org/abs/2403.03187",
  "[8] “Estimating crop yields with remote sensing and deep learning,” 2019. [Online]. Available: https://arxiv.org/abs/1907.11910",
  "[9] “Crop Yield Prediction dataset,” public agricultural statistics repository (state/district-level crop yield, soil type, soil pH). [Real dataset used in this study.]",
  "[10] “Crop Recommendation dataset,” public repository providing per-crop agronomic means (N, P, K, temperature, humidity, pH, rainfall). [Real dataset used in this study.]",
  "[11] DOME Consortium, “Recommendations for supervised machine learning validation in biology,” 2023. [Online]. Available: https://arxiv.org/abs/2303.04733",
];
refs.forEach(r => body.push(new Paragraph({ spacing:{after:80}, indent:{left:360, hanging:360}, children:[ new TextRun({text:r, size:18, font:"Arial"}) ] })));

const doc = new Document({
  numbering: { config: [
    { reference:"bullets", levels:[{level:0, format:LevelFormat.BULLET, text:"•", alignment:AlignmentType.LEFT, style:{paragraph:{indent:{left:720, hanging:360}}}}] },
    { reference:"numbers", levels:[{level:0, format:LevelFormat.DECIMAL, text:"%1.", alignment:AlignmentType.LEFT, style:{paragraph:{indent:{left:720, hanging:360}}}}] },
  ]},
  styles: { default: { document: { run: { font:"Arial", size:20 } } },
    paragraphStyles: [
      { id:"Heading1", name:"Heading 1", basedOn:"Normal", next:"Normal", quickFormat:true, run:{size:28, bold:true, font:"Arial"}, paragraph:{spacing:{before:240, after:120}, outlineLevel:0} },
      { id:"Heading2", name:"Heading 2", basedOn:"Normal", next:"Normal", quickFormat:true, run:{size:24, bold:true, font:"Arial"}, paragraph:{spacing:{before:160, after:80}, outlineLevel:1} },
    ]},
  sections: [{
    properties: { page: { size:{ width:12240, height:15840 }, margin:{top:1440, right:1440, bottom:1440, left:1440} } },
    headers: { default: new Header({ children:[ new Paragraph({ alignment:AlignmentType.RIGHT, border:{bottom:{style:BorderStyle.SINGLE, size:4, color:"2E75B6", space:1}}, children:[ new TextRun({text:"AI-Based Crop Yield Prediction · Smart Agriculture", size:16, font:"Arial", color:"666666"}) ] }) ] }) },
    footers: { default: new Footer({ children:[ new Paragraph({ alignment:AlignmentType.CENTER, children:[ new TextRun({text:"Page ", size:16, font:"Arial"}), new TextRun({children:[PageNumber.CURRENT], size:16, font:"Arial"}) ] }) ] }) },
    children: body
  }]
});

Packer.toBuffer(doc).then(buf => { fs.writeFileSync("Smart_Farming_Term_Paper_v4.docx", buf); console.log("WROTE Smart_Farming_Term_Paper_v4.docx", buf.length, "bytes"); });
