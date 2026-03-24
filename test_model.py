from stress_model import predict_stress

# sample input
accuracy = 90
speed = 45
backspaces = 2

result = predict_stress(accuracy, speed, backspaces)

print("Predicted Stress:", result)
