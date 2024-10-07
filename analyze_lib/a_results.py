import os
import pandas as pd


class Results:
    COMMENT = "#"
    DELIMETER = ","
    LINE_BREAK = "\n"
    CHUNK_SIZE = 1000

    def __init__(self, data_filename) -> None:
        if isinstance(data_filename, (list, tuple)):
            data_filenames, data_filename = data_filename, data_filename[0]
        else:
            data_filenames = [data_filename]

        self.data_filename = data_filename
        self.data_filenames = data_filenames

        if os.path.exists(data_filename):
            self.reload()
        else:
            for filename in self.data_filenames:
                with open(filename, "w") as f:
                    f.write(self.header())
                    f.write(self.labels())
            self._data = None

    def header(self):
        raise NotImplementedError()

    def labels(self):
        raise NotImplementedError()

    def reload(self):
        chunks = pd.read_csv(self.data_filename, comment=self.COMMENT, delimiter=self.DELIMETER, chunksize=self.CHUNK_SIZE, iterator=True)
        try:
            self._data = pd.concat(chunks, ignore_index=True)
        except Exception:
            self._data = chunks.read()
            
    @property
    def data(self):
        return self._data
