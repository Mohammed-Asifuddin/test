"""
File validator
"""
ALLOWED_IMAGE_EXTENSIONS = set(["png", "jpg", "jpeg", "gif"])
ALLOWED_INTENT_EXTENSIONS = set(["csv"])


def allowed_image_file(filename):
    """
    Validate image file suffix.
    """
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS
    )


def allowed_intent_file(filename):
    """
    Validate intent file suffix.
    """
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_INTENT_EXTENSIONS
    )
