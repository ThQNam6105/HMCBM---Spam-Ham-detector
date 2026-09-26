import os
import json
from app import app

def test_flask_app():
    print("Testing Flask app endpoints...")
    client = app.test_client()

    # 1. Test index page
    res_index = client.get('/')
    assert res_index.status_code == 200, f"Index failed: {res_index.status_code}"
    print("[OK] GET / returned 200 OK")

    spam_path = os.path.join('sample_emails', 'spam_offer.eml')
    ham_path = os.path.join('sample_emails', 'ham_meeting.eml')
    lottery_path = os.path.join('sample_emails', 'spam_lottery.eml')

    # 2. Test All Models
    with open(spam_path, 'rb') as f1, open(ham_path, 'rb') as f2, open(lottery_path, 'rb') as f3:
        data = {
            'files': [
                (f1, 'spam_offer.eml'),
                (f2, 'ham_meeting.eml'),
                (f3, 'spam_lottery.eml')
            ],
            'models': ['all']
        }
        res_post = client.post('/api/classify', data=data, content_type='multipart/form-data')
        assert res_post.status_code == 200
        res_json = res_post.get_json()
        assert len(res_json['results']) == 3
        for r in res_json['results']:
            assert 'naive_bayes' in r['predictions']
            assert 'knn' in r['predictions']
            assert 'decision_tree' in r['predictions']
        print("[OK] All models classification verified.")

    # 3. Test Naive Bayes only
    with open(spam_path, 'rb') as f1:
        data = {
            'files': [(f1, 'spam_offer.eml')],
            'models': ['naive_bayes']
        }
        res_post = client.post('/api/classify', data=data, content_type='multipart/form-data')
        assert res_post.status_code == 200
        res_json = res_post.get_json()
        preds = res_json['results'][0]['predictions']
        assert 'naive_bayes' in preds
        assert 'knn' not in preds
        assert 'decision_tree' not in preds
        print("[OK] Naive Bayes selection verified.")

    # 4. Test KNN only
    with open(spam_path, 'rb') as f1:
        data = {
            'files': [(f1, 'spam_offer.eml')],
            'models': ['knn']
        }
        res_post = client.post('/api/classify', data=data, content_type='multipart/form-data')
        assert res_post.status_code == 200
        res_json = res_post.get_json()
        preds = res_json['results'][0]['predictions']
        assert 'knn' in preds
        assert 'naive_bayes' not in preds
        assert 'decision_tree' not in preds
        print("[OK] KNN selection verified.")

    # 5. Test Decision Tree only
    with open(spam_path, 'rb') as f1:
        data = {
            'files': [(f1, 'spam_offer.eml')],
            'models': ['decision_tree']
        }
        res_post = client.post('/api/classify', data=data, content_type='multipart/form-data')
        assert res_post.status_code == 200
        res_json = res_post.get_json()
        preds = res_json['results'][0]['predictions']
        assert 'decision_tree' in preds
        assert 'naive_bayes' not in preds
        assert 'knn' not in preds
        print("[OK] Decision Tree selection verified.")

    # 6. Test Error Handling for invalid file type
    with open(spam_path, 'rb') as f1:
        data = {
            'files': [(f1, 'invalid_file.txt')],
            'models': ['naive_bayes']
        }
        res_post = client.post('/api/classify', data=data, content_type='multipart/form-data')
        assert res_post.status_code == 200
        res_json = res_post.get_json()
        assert 'error' in res_json['results'][0]
        print("[OK] Invalid file type error handling verified.")

    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    test_flask_app()
