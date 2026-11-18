# -*- coding: utf-8 -*-
import os
from PySide6.QtGui import QPixmap
from config import RESOURCES_DIR, PLACEHOLDER_IMAGE

_PIXMAP_CACHE = {}


def load_cover(image_path):
    cache_key = image_path or "__placeholder__"
    if cache_key in _PIXMAP_CACHE:
        return _PIXMAP_CACHE[cache_key]

    if image_path:
        full_path = os.path.join(str(RESOURCES_DIR), image_path)
        if os.path.exists(full_path):
            pixmap = QPixmap(full_path)
            if not pixmap.isNull():
                _PIXMAP_CACHE[cache_key] = pixmap
                return pixmap

    placeholder = QPixmap(PLACEHOLDER_IMAGE)
    _PIXMAP_CACHE[cache_key] = placeholder
    return placeholder
