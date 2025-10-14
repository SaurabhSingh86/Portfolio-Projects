
def normalize_label(label: str) -> str:
    """
    Map multiple raw labels into unified classes for consistency.
    """
    mapping = {
        "Normal": "Normal",
        "Pneumonia": "Pneumonia",
        "Pneumonia (Lung Opacity)": "Pneumonia",
        "Lung Opacity": "Pneumonia",
        "Abnormal": "No Lung Opacity / Not Normal",
        "Not Normal": "No Lung Opacity / Not Normal",
        "No Lung Opacity": "No Lung Opacity / Not Normal",
        "No Lung Opacity / Not Normal": "No Lung Opacity / Not Normal",
    }
    return mapping.get(label.strip(), label.strip())
