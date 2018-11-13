import pandas as pd


class DataLoader:
    @staticmethod
    def load_streams_from_excel(file_path):
        '''
        Loads stream data from an excel file. Stream data must be on the first sheet and be arranged with the columns:
        Name/ID | Supply Temperature | Target Temperature | CP | h (Optional)

        h values that are not supplied will be assumed to be 1
        :param file_path: path to the excel file (string)
        :return:
        '''
        df = pd.read_excel(file_path)

        print(df.head())

    @staticmethod
    def load_streams_from_csv(file_path):
        '''
        Loads stream data from an excel file. Stream data must be on the first sheet and be arranged with the columns:
        Name/ID,Supply Temperature,Target Temperature,CP,h (Optional)

        h values that are not supplied will be assumed to be 1
        :param file_path: path to the csv file (string)
        :return:
        '''

        df = pd.read_csv(file_path)

        df = df.drop(columns=df.columns[0])

        df = df.fillna(1)

        # _validate_stream_data(df)
        streams = df.values

        return streams


def load_streams_from_csv(file_path):
    '''
    Loads stream data from an excel file. Stream data must be on the first sheet and be arranged with the columns:
    Name/ID,Supply Temperature,Target Temperature,CP,h (Optional)

    h values that are not supplied will be assumed to be 1
    :param file_path: path to the csv file (string)
    :return:
    '''
    df = pd.read_csv(file_path)
    df = df.drop(columns=df.columns[0])
    df = df.fillna(1)
    df = df.round(decimals=6)

    streams = list(df.values)

    streams = [list(s) for s in streams]

    return streams

# Testing