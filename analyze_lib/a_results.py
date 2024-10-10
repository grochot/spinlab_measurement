import os
import pandas as pd


class Results:
    COMMENT = "#"
    DELIMETER = ","
    LINE_BREAK = "\n"
    CHUNK_SIZE = 1000

    def __init__(self, data_filename) -> None:
        self._header_count = -1
        self._metadata_count = -1

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

    @staticmethod
    def load(data_filename):
        header = ""
        header_done = False
        header_count = 0
        with open(data_filename) as f:
            while not header_done:
                line = f.readline()
                if line.startswith(Results.COMMENT):
                    header += line.strip("\t\v\n\r\f") + Results.LINE_BREAK
                    header_count += 1
                else:
                    header_done = True
        results = Results(data_filename)
        results._header_count = header_count
        return results

    @staticmethod
    def parse_header(data_filename):
        header = ""
        header_done = False
        header_count = 0
        with open(data_filename) as f:
            while not header_done:
                line = f.readline()
                if line.startswith(Results.COMMENT):
                    header += line.strip("\t\v\n\r\f") + Results.LINE_BREAK
                    header_count += 1
                else:
                    header_done = True
        return header, header_count

    @property
    def data(self):
        return self._data
