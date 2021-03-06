import tensorflow as tf

from tensorflow import keras
from tensorflow.keras.models import load_model
from sklearn.metrics import accuracy_score
import numpy as np
import time

def evaluate_model(interpreter):
  input_index = interpreter.get_input_details()[0]["index"]
  output_index = interpreter.get_output_details()[0]["index"]

  # Run predictions on every image in the "test" dataset.
  prediction_digits = []
  for i, test_image in enumerate(test_images):
    # Pre-processing: add batch dimension and convert to float32 to match with
    # the model's input data format.
    test_image = np.expand_dims(test_image, axis=0).astype(np.float32)
    interpreter.set_tensor(input_index, test_image)

    # Run inference.
    interpreter.invoke()

    # Post-processing: remove batch dimension and find the digit with highest
    # probability.
    output = interpreter.tensor(output_index)
    digit = np.argmax(output()[0])
    prediction_digits.append(digit)
  # Compare prediction results with ground truth labels to calculate accuracy.
  prediction_digits = np.array(prediction_digits)
  accuracy = (prediction_digits == test_labels).mean()
  return accuracy


# Load MNIST dataset
mnist = keras.datasets.mnist
(train_images, train_labels), (test_images, test_labels) = mnist.load_data()

model = load_model('model.h5')

# Interpreter for 
quant_interpreter = tf.lite.Interpreter(model_path="quant.tflite")
quant_interpreter.allocate_tensors()

interpreter = tf.lite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()

# Normalize image
train_images = train_images / 255.0
test_images = test_images / 255.0


# evaluate models
time_model = time.time()
y_pred = model.predict(test_images)
y_pred = np.argmax(y_pred, axis=1)
print("Time take by model is ",time.time()-time_model)



time_quant = time.time()
quant_test_accuracy = evaluate_model(quant_interpreter)
print("Time take by quantized tf lite  model is ",time.time()-time_quant)


time_tfmodel = time.time()
test_accuracy = evaluate_model(interpreter)
print("Time take by tf lite  model is ",time.time()-time_tfmodel)
print("\n")
print("Accuracy of normal model",accuracy_score(y_pred,test_labels))
print("Accuracy of quantized tf lite model is",quant_test_accuracy)
print("Accuracy of tf lite model is",test_accuracy)