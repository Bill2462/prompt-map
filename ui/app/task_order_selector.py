import os
import json
from dataclasses import dataclass

@dataclass
class ConditionCounts:
    task_1_first: int
    task_2_first: int

class OrderSelector:
    def __init__(self, logger_path):
        self.logger_path = logger_path
        os.makedirs(self.logger_path, exist_ok=True)

        self.filepath = os.path.join(self.logger_path, "condition_counts.json")
    
    def _read_condition_counts(self):
        if not os.path.exists(self.filepath):
            return ConditionCounts(0, 0)
        
        with open(self.filepath, "r") as f:
            return ConditionCounts(**json.load(f))

    def _write_condition_counts(self, condition_counts):
        with open(self.filepath, "w") as f:
            json.dump(condition_counts.__dict__, f)

    def get_first_task(self):
        condition_counts = self._read_condition_counts()
        if condition_counts.task_1_first <= condition_counts.task_2_first:
            condition_counts.task_1_first += 1
            self._write_condition_counts(condition_counts)
            return 1
        else:
            condition_counts.task_2_first += 1
            self._write_condition_counts(condition_counts)
            return 2

