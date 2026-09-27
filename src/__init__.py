"""
MatchNexa Business Entity Resolution Package
Amazon ML Challenge 2026
"""

from .pipeline import EntityResolutionPipeline
from .blocking import ScalableBlocker
from .features import extract_pair_features
from .preprocessing import preprocess_dataframe
from .model import EntityMatchingModel
from .metrics import compute_macro_f05
