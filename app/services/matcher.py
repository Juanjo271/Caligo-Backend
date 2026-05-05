import cv2
import numpy as np
import os
from typing import Tuple, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_IMAGES_DIR = os.path.join(BASE_DIR, "app", "static", "ref_images")


class ORBMatcher:
    def __init__(self):
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        self.descriptors_cache = {}
        self.orb = cv2.ORB_create(nfeatures=500)

    def load_reference_image(self, image_filename: str) -> Optional[np.ndarray]:
        image_path = os.path.join(REF_IMAGES_DIR, image_filename)
        if not os.path.exists(image_path):
            print(f"Imagen de referencia no encontrada: {image_path}")
            return None
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        return image

    def compute_descriptor(self, image: np.ndarray) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        if image is None:
            return None
        keypoints, descriptor = self.orb.detectAndCompute(image, None)
        return keypoints, descriptor

    def compute_descriptor_from_image(self, image: np.ndarray) -> Optional[np.ndarray]:
        if image is None:
            return None
        _, descriptor = self.orb.detectAndCompute(image, None)
        return descriptor

    def match(self, descriptor1: np.ndarray, descriptor2: np.ndarray) -> float:
        if descriptor1 is None or descriptor2 is None:
            return 0.0

        descriptor1 = descriptor1.astype(np.uint8)
        descriptor2 = descriptor2.astype(np.uint8)

        matches = self.matcher.match(descriptor1, descriptor2)
        if not matches:
            return 0.0

        matches = sorted(matches, key=lambda x: x.distance)

        num_good_matches = len(matches)
        if num_good_matches < 10:
            return float(num_good_matches) / 50.0

        score = float(num_good_matches) / 50.0
        return min(score, 1.0)

    def verify(self, image_bytes: bytes, expected_filename: str) -> Tuple[bool, float]:
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

        if image is None:
            return False, 0.0

        image_resized = cv2.resize(image, (640, 480))

        ref_image = self.load_reference_image(expected_filename)
        if ref_image is None:
            return False, 0.0

        ref_resized = cv2.resize(ref_image, (640, 480))

        query_descriptor = self.compute_descriptor_from_image(image_resized)
        ref_descriptor = self.compute_descriptor_from_image(ref_resized)

        if query_descriptor is None or ref_descriptor is None:
            return False, 0.0

        score = self.match(ref_descriptor, query_descriptor)

        match = score >= 0.50

        return match, score


_orb_matcher = ORBMatcher()


def get_orb_matcher() -> ORBMatcher:
    return _orb_matcher
