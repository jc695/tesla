from dask.diagnostics import ProgressBar
import os

import utilities as ut

def main(dir='test_results'):
    '''main process for data pipeline'''
    # establish the data directory
    filepath = os.path.join('..', 'data', dir)

    # iterate through the data directory and perform the specified task
    # from the challenge instructions
    for file in ut.find_files(filepath):
        with ProgressBar():
            # task 1: read the file and preprocess the data
            test = ut.process_file(file)
            updateDF = ut.updateDF(test)
            updateDF.preprocess_data()
            # task 2a: calculate force and spring displacement
            updateDF.calculate_metrics()
            # [remove print when finished]
            print(updateDF.df.compute().head())
            # task 2/3/4: create a scatterplot and save as file
            plotDF = ut.plotDF(updateDF.df)
            # task 2b: scatterplot without best-fit line
            plotDF.plot_scatter(file, 'output_no_best_fit_line.png', best_fit=False)
            # task 3b: scatterplot with best-fit line
            plotDF.plot_scatter(file, 'output_w_best_fit_line.png')
            # task 4: Pruning/remove data points over 20,000 N in force.
            # used eye test to remove data points.  There are other methods
            # like mahalanobis distance that calculates distance from the mean.
            # ~ran out of time for this task.~
            updateDF.remove_data()
            plotDF = ut.plotDF(updateDF.df)
            plotDF.plot_scatter(file, 'pruned_output_w_best_fit_line.png')
            updateDF.reset_df()



if __name__ == '__main__':
    main()
