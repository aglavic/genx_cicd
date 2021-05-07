'''
=====================================================
:mod:`sns_mr` SNS magnetism reflectometer data loader
=====================================================

Loads the default datafile format used for extracted reflectivity at
the SNS magnetism reflectometer. It allows to import several channels at
once, automatically naming the datasets according to the imported
polarizations.
'''

import numpy as np

from ..data_loader_framework import Template
from ..utils import ShowWarningDialog

class Plugin(Template):
    wildcard = '*.dat'

    def __init__(self, parent):
        Template.__init__(self, parent)
        self.x_col = 0
        self.y_col = 1
        self.e_col = 2
        self.xe_col = 3
        self.ai_col = 4
        self.comment = '#'
        self.skip_rows = 0
        self.delimiter = None

    def LoadData(self, dataset, filename):
        '''LoadData(self, data_item_number, filename) --> none

        Loads the data from filename into the data_item_number.
        '''
        # get scan number and polarization channel from filename
        name = ''
        fhandle = open(filename, 'r', encoding='utf-8')
        fline = fhandle.readline()
        while not '[Data]' in fline:
            if 'Input file indices:' in fline:
                name += fline.split(':')[1].strip()
            if 'Extracted states:' in fline:
                name += ' (%s)'%(fline.split(':')[1].strip().split(' ')[0])
            fline = fhandle.readline()
            if not fline:
                ShowWarningDialog(self.parent, 'Could not load the file: ' + filename+' \nWrong format.\n')
                return

        try:
            load_array = np.loadtxt(fhandle, delimiter=self.delimiter, comments=self.comment, skiprows=self.skip_rows)
        except Exception as e:
            ShowWarningDialog(self.parent, 'Could not load the file: ' + filename +
                              ' \nPlease check the format.\n\n numpy.loadtxt' + ' gave the following error:\n' + str(e))
            return
        else:
            # For the freak case of only one data point
            if len(load_array.shape) < 2:
                load_array = np.array([load_array])
            # Check so we have enough columns
            if load_array.shape[1] - 1 < max(self.x_col, self.y_col, self.e_col):
                ShowWarningDialog(self.parent, 'The data file does not contain' + 'enough number of columns. It has '
                                  + str(load_array[1]) + ' columns. Rember that the column index start at zero!')
                # Okay now we have showed a dialog lets bail out ...
                return
            # The data is set by the default Template.__init__ function, neat hu
            # Know the loaded data goes into *_raw so that they are not
            # changed by the transforms
            dataset.x_raw=load_array[:, self.x_col]
            dataset.y_raw=load_array[:, self.y_col]
            dataset.error_raw=load_array[:, self.e_col]
            dataset.set_extra_data('res', load_array[:,self.xe_col], 'res')
            dataset.set_extra_data('ai', load_array[:,self.ai_col], 'ai')
            # Name the dataset accordign to file name
            dataset.name = name
            # Run the commands on the data - this also sets the x,y, error memebers
            # of that data item.
            dataset.run_command()
