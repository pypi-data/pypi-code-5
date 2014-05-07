"""
"""

from orangecontrib import earth

from Orange.OrangeWidgets.OWWidget import OWWidget
from .OWEarth import OWEarth

from Orange.OrangeWidgets import OWGUI


NAME = "Earth Classification" 
DESCRIPTION = "Multivariate Adaptive Regression Splines (MARS) classification."
ICON = "icons/EarthMars.svg"
CATEGORY = "Classification"

KEYWORDS = ["mars", "multivariate", "adaptive", "regression", "splines", "classification"]

INPUTS = (
    {"name": "Data",
     "type": Orange.data.Table,
     "handler": "set_data",
     "doc": "Set input training data set."},

    {"name": "Preprocessor",
     "type": PreprocessedLearner,
     "handler": "set_preprocessor",
     "doc": "Data Preprocessor"}
)

OUTPUTS = (
    ("Learner", earth.EarthLearner),
    ("Predictor", earth.EarthClassifier),
    ("Basis Matrix", Orange.data.Table)
)


class OWEarthClassification(OWEarth):
    settingsList = OWEarth.settingsList + ["link", "lr_lambda", "fda_k"]

    def __init__(self, parent=None, signalManager=None, title="Earth Classification"):
        OWEarth.__init__(self, parent, signalManager, title,
                         wantMainArea=False, resizingEnabled=False)

        self.link = 0
        self.lr_lambda = 1.0
        self.fda_k = 3

        self.loadSettings()

        
    def apply(self):
        base_learner = earth.EarthLearner(
            degree=self.degree,
            terms=self.terms if self.terms > 2 else None,
            penalty=self.penalty,
            name=self.name
        )
        if self.link == 0:
            wrapper = Orange


class FDALearner(Orange.classification.Learner):
    """
    Flexible Discriminant Analysis (FDA) learner.
    """
    def __init__(self, base_learner, k=3):
        self.base_learner = base_learner
        self.k = k

    def __call__(self, data, weight_id=None):
        if not isinstance(data.domain.class_var, Orange.feature.Discrete):
            raise TypeError("Discrete class expected")

        orig_domain = data.domain
        # Expand the class column into a continuous indicator matrix.
        data = utils.expand_class(data)

        base_pred = self.base_learner(data, weight_id)
        predictions = utils.predict(base_pred, data)

        scoring, _ = utils.fda(predictions, k=self.k)

        return FDAClassifier(orig_domain, base_pred, scoring)


class FDAClassifier(Orange.classification.ClassifierFD):
    def __init__(self, domain, base_predictor, scoring):
        self.domain = domain
        self.class_var = domain.class_var
        self.base_predictor = base_predictor
        self.scoring = scoring

    def __call__(self, instance, return_what=Orange.core.GetValue):
        instance = Orange.data.Instance(self.domain, instance)
        
        predictions = self.base_predictor(instance)
        vals = [pred]
