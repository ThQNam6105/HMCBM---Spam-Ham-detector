import os
import joblib
import warnings
import numpy as np

# Suppress scikit-learn version mismatch warnings on unpickling
warnings.filterwarnings('ignore', category=UserWarning)

from preprocessing.text_preprocessor import preprocess_email_text

class ModelPredictor:
    """
    Model Predictor class that loads saved scikit-learn models and TF-IDF vectorizer ONCE.
    Performs inference on preprocessed text without re-training or altering models.
    """

    MODEL_FILES = {
        'naive_bayes': 'naive_bayes_model.pkl',
        'knn': 'knn_model.pkl',
        'decision_tree': 'decision_tree_model.pkl',
        'vectorizer': 'tfidf_vectorizer.pkl'
    }

    def __init__(self, models_dir: str = 'models'):
        self.models_dir = models_dir
        self.models = {}
        self.vectorizer = None
        self.is_loaded = False
        self.load_models()

    def load_models(self):
        """Load vectorizer and machine learning models from .pkl files."""
        print("Loading machine learning models and vectorizer...")
        
        vec_path = os.path.join(self.models_dir, self.MODEL_FILES['vectorizer'])
        if not os.path.exists(vec_path):
            raise FileNotFoundError(f"TF-IDF vectorizer file not found at: {vec_path}")
        self.vectorizer = joblib.load(vec_path)

        for key in ['naive_bayes', 'knn', 'decision_tree']:
            path = os.path.join(self.models_dir, self.MODEL_FILES[key])
            if not os.path.exists(path):
                raise FileNotFoundError(f"Model file '{key}' not found at: {path}")
            self.models[key] = joblib.load(path)

        self.is_loaded = True
        print("All machine learning models successfully loaded into memory!")

    def _normalize_label(self, raw_pred) -> str:
        """
        Normalize model output prediction to 'spam' or 'ham'.
        Handles int (0/1), str ('0'/'1', 'ham'/'spam'), numpy types.
        """
        val = str(raw_pred).strip().lower()
        if val in ['1', 'spam', 'true', '1.0']:
            return 'spam'
        elif val in ['0', 'ham', 'false', '0.0']:
            return 'ham'
        return 'spam' if 'spam' in val else ('ham' if 'ham' in val else val)

    def predict(self, text: str, selected_models: list[str]) -> dict:
        """
        Preprocess text, transform with TF-IDF vectorizer (sparse), and run inference
        with specified models.

        selected_models: list of model keys e.g. ['naive_bayes', 'knn', 'decision_tree']
        """
        if not self.is_loaded:
            raise RuntimeError("Models are not loaded.")

        if 'all' in selected_models:
            selected_models = ['naive_bayes', 'knn', 'decision_tree']

        valid_keys = [m for m in selected_models if m in self.models]
        if not valid_keys:
            valid_keys = ['naive_bayes', 'knn', 'decision_tree']

        # Step 1: Preprocess text
        processed_text = preprocess_email_text(text)

        # Step 2: Transform to TF-IDF sparse matrix (DO NOT convert to dense array!)
        sparse_tfidf = self.vectorizer.transform([processed_text])

        predictions = {}

        for model_key in valid_keys:
            model = self.models[model_key]
            
            raw_pred = model.predict(sparse_tfidf)[0]
            label = self._normalize_label(raw_pred)

            model_res = {
                "label": label
            }

            # Check probability support
            if hasattr(model, "predict_proba"):
                try:
                    proba_array = model.predict_proba(sparse_tfidf)[0]
                    classes = list(getattr(model, "classes_", [0, 1]))
                    normalized_classes = [self._normalize_label(c) for c in classes]
                    
                    if label in normalized_classes:
                        idx = normalized_classes.index(label)
                        conf = float(proba_array[idx])
                    else:
                        conf = float(np.max(proba_array))

                    model_res["probability"] = round(conf, 4)
                except Exception:
                    pass

            predictions[model_key] = model_res

        return {
            "processed_text": processed_text,
            "predictions": predictions
        }
