from dask.diagnostics import ProgressBar
import os

import utilities as ut

def main():
    filepath = os.path.join('..', 'data', 'test_results')

    for file in ut.find_files(filepath):
        with ProgressBar():
            test = ut.process_file(file)
            updateDF = ut.updateDF(test)
            updateDF.preprocess_data()
            updateDF.calculate_metrics()
            print(updateDF.df.compute().head())
            plotDF = ut.plotDF(updateDF.df)
            plotDF.plot_scatter(file, 'output_no_best_fit_line.png', best_fit=False)


if __name__ == '__main__':
    main()
