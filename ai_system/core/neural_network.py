import numpy as np
import json

class SimpleNeuralNetwork:
    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        self.W1 = np.random.randn(input_size, hidden_size) * 0.1
        self.b1 = np.zeros((1, hidden_size))
        self.W2 = np.random.randn(hidden_size, output_size) * 0.1
        self.b2 = np.zeros((1, output_size))
        
        self.learning_rate = 0.01
    
    def sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
    
    def forward(self, X):
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = self.sigmoid(self.z1)
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = self.sigmoid(self.z2)
        return self.a2
    
    def train(self, X, y, epochs=1000):
        for i in range(epochs):
            output = self.forward(X)
            
            # Backpropagation
            m = X.shape[0]
            dZ2 = output - y
            dW2 = (1/m) * np.dot(self.a1.T, dZ2)
            db2 = (1/m) * np.sum(dZ2, axis=0, keepdims=True)
            
            dA1 = np.dot(dZ2, self.W2.T)
            dZ1 = dA1 * self.a1 * (1 - self.a1)
            dW1 = (1/m) * np.dot(X.T, dZ1)
            db1 = (1/m) * np.sum(dZ1, axis=0, keepdims=True)
            
            self.W2 -= self.learning_rate * dW2
            self.b2 -= self.learning_rate * db2
            self.W1 -= self.learning_rate * dW1
            self.b1 -= self.learning_rate * db1
            
            if i % 100 == 0:
                loss = np.mean(np.square(y - output))
                print(f"Epoch {i}, Loss: {loss:.4f}")
    
    def predict(self, X):
        return self.forward(X)