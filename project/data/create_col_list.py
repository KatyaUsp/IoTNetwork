import pandas as pd
import numpy as np


def main():
    data_original = pd.read_csv('data/iot_network_intrusion_dataset.csv')
    numeric_cols = data_original.select_dtypes([np.number]).columns
    non_numeric_cols = list(set(data_original.columns) - set(numeric_cols))

    f = open('data/non_numeric_cols.txt', 'w')
    for col in non_numeric_cols:
        f.write(col + '\n')

    f.close()

    f = open('data/numeric_cols.txt', 'w')
    for col in numeric_cols:
        f.write(col + '\n')

    f.close()


if __name__ == "__main__":
    main()