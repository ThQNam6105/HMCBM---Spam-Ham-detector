# Spam Email Classification Using Machine Learning - University Thesis Demonstration

A full-stack, localhost demonstration web application for classifying email messages (`.eml`) as **SPAM** or **HAM** using machine learning models trained on the **SpamAssassin Public Corpus**.

The application loads four pre-trained model artifacts directly from the `models/` directory, executes the pre-processing pipeline, extracts TF-IDF sparse features, and computes real-time predictions with probability scores.

> **Important Note:** This application is designed exclusively for **inference and demonstration**. It does **NOT** retrain models, fit new TF-IDF vectorizers, or alter any weights.

---

## 1. System Architecture

```
                                  [ Uploaded .eml Files ]
                                             │
                                             ▼
                             [ MIME Email Parser (email.parser) ]
                                 Extract Subject & Body Text
                                             │
                                             ▼
                          [ Preprocessing Pipeline (TextPreprocessor) ]
                      • Lowercase
                      • HTML Tag Removal
                      • URL & Email Address Removal
                      • Special Character Cleaning
                      • Whitespace Normalization
                      • NLTK English Stopwords Removal
                      • Word Tokenization
                                             │
                                             ▼
                        [ Sparse TF-IDF Vectorizer Transform ]
                         tfidf_vectorizer.transform([processed_text])
                        (~168,495 vocabulary features - Sparse Matrix)
                                             │
                                             ▼
                            [ Machine Learning Classifiers ]
                  ┌──────────────────────────┼──────────────────────────┐
                  ▼                          ▼                          ▼
          [ Naive Bayes ]                 [ KNN ]                [ Decision Tree ]
         MultinomialNB              KNeighborsClassifier       DecisionTreeClassifier
                  │                          │                          │
                  └──────────────────────────┼──────────────────────────┘
                                             ▼
                                  [ Results Dashboard UI ]
```

---

## 2. Project Folder Structure

```
demo/
│
├── models/
│   ├── naive_bayes_model.pkl    # Multinomial Naive Bayes trained model
│   ├── knn_model.pkl            # K-Nearest Neighbors trained model
│   ├── decision_tree_model.pkl  # Decision Tree trained model
│   └── tfidf_vectorizer.pkl     # TF-IDF vectorizer (vocabulary: ~168,495)
│
├── preprocessing/
│   ├── __init__.py
│   └── text_preprocessor.py     # Preprocessing pipeline matching training
│
├── email_parser/
│   ├── __init__.py
│   └── parser.py                # EML parser (Subject, Body, Plain/HTML)
│
├── classifier/
│   ├── __init__.py
│   └── predictor.py             # Model loader & inference predictor
│
├── templates/
│   └── index.html               # Thesis Demonstration UI
│
├── static/
│   ├── css/
│   │   └── style.css            # Responsive dashboard styling & theme
│   └── js/
│       └── app.js               # Interactive frontend JS logic
│
├── sample_emails/               # Sample .eml files for quick demo
│   ├── spam_offer.eml
│   ├── ham_meeting.eml
│   └── spam_lottery.eml
│
├── uploads/
│   └── .gitkeep                 # Upload directory placeholder
│
├── app.py                       # Main Flask web application backend
├── run.py                       # Alternative entrypoint script
├── test_app.py                  # Integration verification script
├── requirements.txt             # Python dependencies
├── README.md                    # Documentation
└── .gitignore                   # Git ignore settings
```

---

## 3. Environment & Prerequisites

- **Python Version:** `Python 3.10+` (Tested on Python 3.14)
- **OS:** Windows / macOS / Linux

---

## 4. Installation & Setup

### Step 1: Clone or navigate to project directory
```bash
cd demo
```

### Step 2: Create a Virtual Environment (Recommended)
**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

## 5. NLTK Setup

The preprocessing module automatically downloads required NLTK resources (`stopwords`, `punkt`, `punkt_tab`) on startup. If you are operating in an offline environment, you can pre-download them via Python:

```python
import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')
```

---

## 6. Model File Placement

Ensure the following 4 `.pkl` files exist in the `models/` folder:
- `models/naive_bayes_model.pkl`
- `models/knn_model.pkl`
- `models/decision_tree_model.pkl`
- `models/tfidf_vectorizer.pkl`

Do **NOT** rename or overwrite these files.

---

## 7. How to Run the Application

Start the Flask development server:

```bash
python app.py
```
*or:*
```bash
python run.py
```

The application will start on:
```
http://127.0.0.1:5000
```

Open your web browser and navigate to `http://127.0.0.1:5000`.

---

## 8. Classification Workflow & Demonstration Flow

1. **Open Application:** Navigate to `http://127.0.0.1:5000`.
2. **Select Email Files:**
   - Drag & drop `.eml` files into the drop zone, or click **Browse Files**.
   - You can also use the sample emails in `sample_emails/`.
3. **Choose Classification Model(s):**
   - Select individual models (`Naive Bayes`, `KNN`, `Decision Tree`) or choose `All Models` to run an ensemble comparison.
4. **Click "Analyze Emails":**
   - View batch statistics (Total Emails, Total Spam, Total Ham, Model Agreement).
   - Inspect individual predictions and confidence percentages.
5. **Inspect Detailed Pipeline:**
   - Click any email row to open the **Email Detail View**.
   - Expand **View Processed Text** to demonstrate the preprocessed output string before vectorization.

---

## 9. Running Tests

To run the automated integration test suite:

```bash
python test_app.py
```

---

## 10. Troubleshooting

- **ModuleNotFoundError:** Ensure your virtual environment is active and run `pip install -r requirements.txt`.
- **Model Load Errors:** Verify all 4 `.pkl` files exist in `demo/models/`.
- **NLTK Download Warning:** If NLTK fail to download automatically due to proxy settings, run the explicit Python download commands in Section 5.
