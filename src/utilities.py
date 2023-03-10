import dask.dataframe as dd
import dask.array as da
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import seaborn
import glob
import os
import re

def csv_to_frame(csv:str):
    '''read csv file into a dask dataframe'''
    return dd.read_csv(csv)


def json_to_frame(json:str,
                    orient:str='records',
                    lines:bool=False,
                    blocksize:int=None):
    '''read json file into a dask dataframe'''
    return dd.read_json(json,
                        orient=orient,
                        lines=lines,
                        blocksize=blocksize)


def find_files(path:str):
    '''recursively find all data files in specified path'''
    return glob.glob(os.path.join(path, '*'), recursive=True)


def find_unique_name(path:str, pattern='(?![Supplier_])(.*)(?=_TestResults)'):
    name_search = re.search(pattern, os.path.basename(path))
    if name_search:
        return name_search.group(1)


def ident_file(path:str):
    '''identify the file type'''
    return os.path.splitext(os.path.basename(path))[1].strip('.')


def process_file(path:str):
    '''given the file type, read the file type into a dask dataframe'''
    ext = ident_file(path)
    if ext == 'csv':
        return csv_to_frame(path)
    if ext == 'json':
        return json_to_frame(path)


def check_folder_exists(path:str, dir='output'):
    filepath = os.path.join(os.path.dirname(path), '..', '..', dir)
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    return os.path.abspath(filepath)


class updateDF:
    '''Updating the dataframe as an object'''
    def __init__(self, df):
        self.original_df = df
        self.df = df.copy()

    def preprocess_data(self):
        '''method to process all preprocessing steps together'''

        def remove_BOM():
            '''remove byte order mark (BOM) from field'''
            self.df.columns = [str(col).lstrip('\ufeff') for col in self.df.columns]

        def to_datetime(col1:str='timestamp'):
            '''convert string object into a datetime object'''
            for col in self.df.columns:
                if 'time|date' in col:
                    self.df[col] = dd.to_datetime(self.df[col])

        def drop_empty_col():
            '''remove empty columns in the dataframe'''
            if "" in self.df.columns:
                self.df = self.df.drop("", axis=1)

        remove_BOM()
        to_datetime()
        drop_empty_col()

    def remove_data(self, col='force', value=20000):
        '''task 4 - remove data points'''
        self.df = self.df[~(self.df[col]>=value)]

    def calculate_metrics(self):
        def add_force_col(col:str='mass_kg', gravity:float=9.81):
            '''task 2: calculate force'''
            self.df['force'] = self.df[col] * gravity

        def add_displacement_col(col1:str='start_measurement_m', col2:str='end_measurement_m'):
            '''task 2: calculate spring displacement'''
            self.df['spring_displacement'] = self.df[col2] - self.df[col1]

        def add_constant_col(col1:str='force', col2:str='spring_displacement'):
            '''task 5: calculate sprint constant based on Hooke's law of elasticity.
            See README for how to calculate constant'''
            self.df['spring_constant'] = da.nan_to_num(self.df[col1] / self.df[col2])

        add_force_col()
        add_displacement_col()
        add_constant_col()

    def reset_df(self):
        '''reset the dataframe'''
        self.df = self.original_df.copy()


class plotDF:
    '''class object to plot graph'''
    def __init__(self, df):
        seaborn.set(style='whitegrid')
        self.df = df.compute()
        self.f, self.ax = plt.subplots(figsize=(10, 10))
        seaborn.despine(self.f, left=True, bottom=True)

    def plot_scatter(self, path:str, fname_suffix:str, x='force', y='spring_displacement', best_fit=True):
        '''create a scatter plot chart based on 'force' and 'spring_displacement' per instructions.
        x and y are set as parameters in case we need to select different dimensions.
        '''
        self.x_data, self.y_data = self.df[x], self.df[y]
        seaborn.scatterplot(x=x, y=y, data=self.df, ax=self.ax)
        plt.ylim(ymin=0)
        plt.xlim(xmin=0)


        # if best_fit parameter is True then add best-fit line to plot
        if best_fit:
            self.model = LinearRegression()
            self.model.fit(self.x_data.values.reshape(-1, 1), self.y_data)
            plt.plot(self.x_data, self.model.predict(self.x_data.values.reshape(-1, 1)), '-', color='red')

        # create a unique_name for the plot image file and specify the output location
        fname_prefix = find_unique_name(path)
        outputdir = check_folder_exists(path)

        # save the chart to file
        plt.xlabel('{} (N)'.format(x))
        plt.ylabel('{} (m)'.format(y))
        plt.title('{} {}'.format(fname_prefix, ' '.join([el for el in fname_suffix.split('.')[0].split('_')])))
        plt.savefig(os.path.join(outputdir, '{}_{}'.format(fname_prefix, fname_suffix)), dpi=300)
