import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.evaluate import evaluate_policy

if __name__ == "__main__":
    print("evaluate.py được gọi. Hàm evaluate_policy đã sẵn sàng để tích hợp.")
