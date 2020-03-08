from typing import List

import numpy as np

from src.classifier.dto.face_prediction import FacePrediction
from src.classifier.train import CLASSIFIER_VERSION
from src.facescanner._detector.constants import FaceLimit, DEFAULT_THRESHOLD_C
from src.facescanner._embedder.constants import CALCULATOR_VERSION
from src.facescanner._embedder.embedder import calculate_embeddings
from src.facescanner.dto.bounding_box import BoundingBox
from src.facescanner.dto.embedding import Embedding
from src.facescanner.facescanner import scan_faces
from src.storage.dto.embedding_classifier import EmbeddingClassifier
from src.storage.storage import get_storage


def predict_from_embedding(classifier: EmbeddingClassifier, embedding: Embedding,
                           face_box: BoundingBox) -> FacePrediction:
    probabilities = classifier.model.predict_proba([embedding.array])[0]
    top_class = np.argsort(-probabilities)[0]
    return FacePrediction(face_name=classifier.class_2_face_name[top_class],
                          probability=probabilities[top_class], box=face_box)


def predict_from_image_with_classifier(img, limit: FaceLimit, classifier: EmbeddingClassifier,
                                       detection_threshold_c: float = DEFAULT_THRESHOLD_C) -> List[FacePrediction]:
    cropped_faces = scan_faces(img, limit, detection_threshold_c)
    cropped_images = [face.img for face in cropped_faces]
    embeddings = calculate_embeddings(cropped_images)
    return [predict_from_embedding(classifier, embedding, face.box)
            for face, embedding in zip(cropped_faces, embeddings)]


def predict_from_image_with_api_key(img, limit: FaceLimit, api_key: str,
                                    detection_threshold_c: float = DEFAULT_THRESHOLD_C) -> List[FacePrediction]:
    classifier = get_storage(api_key).get_embedding_classifier(CLASSIFIER_VERSION, CALCULATOR_VERSION)
    return predict_from_image_with_classifier(img, limit, classifier, detection_threshold_c)
