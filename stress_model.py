import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from collections import Counter

# ---------------- TRAIN DATA ---------------- #

X = np.array([
[95, 55, 1],
[92, 50, 2],
[88, 48, 3],
[80, 40, 4],
[75, 35, 5],
[70, 30, 6],
[65, 28, 7],
[55, 20, 10],
[50, 18, 12],
[40, 15, 15]
])

y = [
"No Stress",
"No Stress",
"Low Stress",
"Medium Stress",
"Medium Stress",
"Medium Stress",
"Medium Stress",
"High Stress",
"High Stress",
"High Stress"
]

# ---------------- MODELS ---------------- #

lr_model = LogisticRegression(max_iter=200)
svm_model = SVC(probability=True)
rf_model = RandomForestClassifier(n_estimators=50)

# Train all
lr_model.fit(X, y)
svm_model.fit(X, y)
rf_model.fit(X, y)


# ---------------- HYBRID PREDICTION ---------------- #

def predict_stress(accuracy, speed, backspaces):

    # 🔴 RULE PRIORITY (VERY IMPORTANT)
    if backspaces >= 7 or accuracy < 50:
        return "High Stress"

    if (4 <= backspaces <= 7) or (50 <= accuracy < 75):
        return "Medium Stress"

    if backspaces <= 2 and accuracy >= 90:
        return "No Stress"

    if backspaces <= 3 and accuracy >= 75:
        if speed < 15:
            return "Medium Stress"
        return "Low Stress"

    # 🤖 ML PREDICTIONS
    data = [[accuracy, speed, backspaces]]

    p1 = lr_model.predict(data)[0]
    p2 = svm_model.predict(data)[0]
    p3 = rf_model.predict(data)[0]

    # 🗳️ MAJORITY VOTING
    final = Counter([p1, p2, p3]).most_common(1)[0][0]

    return final
