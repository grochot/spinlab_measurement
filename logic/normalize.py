import numpy as np
from threading import Lock


class Normalize:
    def __init__(self, to_normalize: list = None, result_object=None):
        if to_normalize is None:
            to_normalize = []
        self.to_normalize = to_normalize

        self._args = {}
        for arg in self.to_normalize:
            self._args[arg] = [None, None]

        self._result_object = result_object
        self._lock = Lock()

    def __call__(self, results: dict):
        if self._result_object is None:
            raise Exception("Normalize: Result object not set!")

        for arg in self.to_normalize:
            if arg in results:
                with self._lock:
                    if self._args[arg][0] is None:
                        self._args[arg][0] = results[arg]
                        self._args[arg][1] = results[arg]
                    else:
                        self._args[arg][0] = min(self._args[arg][0], results[arg])
                        self._args[arg][1] = max(self._args[arg][1], results[arg])

                with self._lock:
                    data = self._result_object.data
                    min_val, max_val = self._args[arg]
                    if max_val - min_val == 0:
                        data[f"Norm {arg}"] = 0.0
                    else:
                        data[f"Norm {arg}"] = (data[arg].astype(float) - min_val) / (max_val - min_val)

                    with open(self._result_object.data_filename, "w") as f:
                        f.write(self._result_object.header())
                        f.write(self._result_object.metadata())
                        f.write(self._result_object.labels())
                        for _, row in data.iterrows():
                            f.write(self._result_object.format(row.to_dict()) + "\n")

            with self._lock:
                min_val, max_val = self._args[arg]
                if max_val - min_val == 0:
                    results[f"Norm {arg}"] = 0.0
                else:
                    results[f"Norm {arg}"] = (results[arg] - min_val) / (max_val - min_val)

        return results


if __name__ == "__main__":
    norm = Normalize(["a", "b"])
    results = {"a": 1, "b": 2}
    print(norm(results))
    results = {"a": 2, "b": 1}
    print(norm(results))
    results = {"a": 1, "b": 1.5}
    print(norm(results))
