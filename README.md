# CrickHigh – AI‑Powered Automated Cricket Highlights Generator

CrickHigh is an intelligent platform that automates the production of cricket highlights from full‑length match broadcasts. It combines computer vision, OCR, and large‑language‑model technology to deliver a seamless, interactive experience, including highlight reels and a conversational chatbot for cricket statistics and insights.

---

## Features

### Cricket Highlights Generation

* **Frame extraction** with OpenCV.
* **Delivery detection** via an EfficientNet‑B0 CNN trained on 5 000 bowler run‑up images.
* **Scoreboard reading** with EasyOCR to capture runs, wickets, and overs.
* **Event detection** for fours, sixes, and wickets by comparing successive score frames.
* **Clip assembly** by matching CNN and OCR timestamps, then concatenating highlight segments.

### Chatbot and Insights

* **Knowledge base** built from 18 000 + Cricsheet matches (international, leagues, men’s and women’s).
* **Semantic search** using FAISS, with boosting for exact matches.
* **Natural‑language responses** generated through the Gemini API.

## Match‑Win Prediction 

**ODI Match‑Win Predictor** built on two LightGBM models.

| Stage | Purpose | Key Inputs |
|-------|---------|------------|
| **Pre‑Match Predictor** | Estimates the likely winner **before the first ball** using historical team strength, venue, and toss outcome. | Teams, venue, toss |
| **Ball‑by‑Ball Predictor** | Updates win probability **after every delivery** by ingesting live match features plus the pre‑match prediction. | Delivery‑level features, expected winner |

---

## Tech Stack

## Updated Tech Stack

| Layer / Function              | Key Technologies & Libraries                             |
| ----------------------------- | -------------------------------------------------------- |
| **Frontend**                  | React, Tailwind CSS                                      |
| **API Backend**               | Flask (Python 3.11)                                      |
| **Computer Vision**           | OpenCV, PyTorch, EfficientNet‑B0                         |
| **OCR**                       | EasyOCR                                                  |
| **Search / Retrieval**        | FAISS (semantic vectors with boosted exact matches)      |
| **LLM Integration**           | Gemini API                                               |
| **Video Editing**             | FFmpeg                                                   |
| **Match‑Win Prediction**      | LightGBM, scikit‑learn, pandas                           |
| **Data Processing**           | pandas, NumPy                                            |
| **Containerisation / DevOps** | Docker (optional: Docker Compose, GitHub Actions for CI) |
| **Environment & Tooling**     | Python virtual‑env / venv or conda, npm, Git             |

---

## System Requirements

* **GPU (recommended):** NVIDIA GTX 1060 or better, though the system can run on CPU‑only machines.
* **CPU:** A multi‑core processor will improve OCR and overall throughput.
* **Memory:** 8 GB RAM minimum.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/crickhigh.git
cd crickhigh
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```


---

## Running the Project

1. **Start the APIs**


   Open two terminal windows in the project root:

   ```bash
   # Terminal 1 – Highlights API
   python Cric_High.py
   ```

   ```bash
   # Terminal 2 – Chatbot API
   python Chatbot.py
   ```

2. **Start the frontend**

   ```bash
   npm run dev
   ```

   The application will be available at `http://localhost:5173`.

---

## Performance

* Generates highlights in approximately **40 – 60 percent** of the original video run time.
* Reduces GPU dependency by avoiding traditional, compute‑heavy ball‑tracking.
* Runs smoothly on standard consumer hardware.

---


## Future Work

* Real‑time streaming support.
* Enhanced match summary visualisations.
* Cloud deployment templates for AWS, GCP, and Azure.

---

Here’s a refined **Credits** section for your README:

---

## Credits

* **Cricsheet** – for providing structured match data used for training and chatbot knowledge base.
* **Open Source Tools** – thanks to the contributors of **OpenCV**, **EasyOCR**, **EfficientNet‑B0**, **FAISS**, and the **Gemini API** for enabling rapid development.
* **Project Contributors**:

  * **Shaikh Abdul Rafay**
  * **Rayyan Ahmed**
  * **Minaal Alam**

This project would not have been possible without the collective efforts of the team and the open-source community.

---

## License

Released under the MIT License.
