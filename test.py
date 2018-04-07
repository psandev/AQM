import pandas as pd
import numpy as np
import os
import fnmatch
import natsort
import time
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib import style
from random import *
style.use('ggplot')

# folder = r'C:\Users\peters\Dropbox\Landa\Python Projects\AQM\20180301 - I2S job'
folder = r'E:\Not Backed Up\Dropbox\Landa\Python Projects\AQM\20180301 - I2S job'




def files_finder(folder, file_name):
    for path, directories, files in os.walk(folder):
        for dir in directories:
            subdir = os.path.join(path, dir)
            for file_path, _, file in os.walk(subdir):
                for file in fnmatch.filter(file,file_name):
                    yield os.path.join(file_path,file), file



def simple_files_finder(folder):
    subdur_raw = os.path.join(folder, 'RawResults')
    subdir_analysis = os.path.join(folder,  'AnalysisResults')
    subdir_correction = os.path.join(folder, 'CorrectionOperators')
    files_row_c2c = natsort.natsorted([os.path.join(subdur_raw,f) for f in os.listdir(subdur_raw) if f.startswith('Registration')])
    files_row_i2s = [os.path.join(subdur_raw,f) for f in os.listdir(subdur_raw) if f.startswith('ImagePlacement_')]
    files_analysis_i2s = [f for f in os.listdir(subdir_analysis) if f.startswith('ImagePlacementAnalysis_')]
    files_analysis_c2c = [f for f in os.listdir(subdir_analysis) if f.startswith('ColorToColorAndScalingAnalysis_')]
    files_correction = natsort.natsorted([f for f in os.listdir(subdir_correction) if f.startswith('Machine')])
    pass
    return files_row_c2c

def load_reg_files(reg_files):
    data_row_c2c = pd.DataFrame()
    for j  in reg_files:
        f = open(j)
        for i in range(7):
            line = f.readline().split(',')
            if i == 3:
                page_id = int(line[1].strip())
            if i == 4:
                panel_id = int(line[1].strip())
            if i == 6:
                status = line[1].strip()
        f.close()
        file_data = pd.read_csv(j,skiprows=7,header=0, index_col=0)
        file_data.insert(0,'Sheet',page_id)
        file_data.insert(1, 'Panel',panel_id)
        file_data.insert(2, 'Status',status)
        data_row_c2c = data_row_c2c.append(file_data)

    data_row_c2c.columns = ['Sheet', 'Panel', 'Status', 'Set1_X', 'Set1_Y', 'Set2_X', 'Set2_Y', 'Set3_X', 'Set3_Y', 'Set4_X', 'Set4_Y', 'Set5_X',
                            'Set5_Y']
    fig, ax = plt.subplots(nrows=4, ncols=2)
    fig.tight_layout()
    colors = np.unique(data_row_c2c.index).tolist()
    col_tints = [['#e6ffff', '#b3ffff','#80ffff','#4dffff','#00ffff'],
                 ['#f2f2f2', '#cccccc', '#a6a6a6','#808080', '#666666'],
                 ['#ffffcc','#ffff99','#ffff66','#ffff33','#ffff00'],
                 ['#ffe6ff','#ffb3ff','#ff80ff','#ff4dff','#ff00ff']]
    data_x = data_row_c2c.iloc[:,[0,1,2,3,5,7,9,11]]
    # x = data_x.groupby('Panel').agg(np.median).iloc[:, 1:]
    data_y = data_row_c2c.iloc[:, [0, 1, 2, 4, 6, 8, 10, 12]]
    # y = data_y.groupby('Panel').agg(np.median).iloc[:, 1:]
    # x.plot(kind = 'bar', ax = ax[0])
    # y.plot(kind='bar', ax=ax[1])
    bar_ax = np.empty([2,4, 5, 11], dtype=object)
    # bar_ax = [[[[None]*11]*5]*4]*2
    for i,col in enumerate(colors):
        x = data_x.ix[col].groupby('Panel').agg(np.median).iloc[:,1:]
        # x.plot(kind='bar', ax = ax[i][0],color=col_tints[i]*11)
        y = data_y.ix[col].groupby('Panel').agg(np.median).iloc[:,1:]
        # y.plot(kind='bar', ax=ax[i][1],color=col_tints[i]*11)
        x_pos = list(range(1,12))
        width = 1/6;
        for set in range(5):
            x_pos = [ el +width  for el in x_pos]
            for p in range(11):
                bar_ax[0][i][set][p] = ax[i][0].bar(x_pos[p],y.iloc[p,set],width,color=col_tints[i][set])
                bar_ax[1][i][set][p]= ax[i][1].bar(x_pos[p], y.iloc[p, set],width,color=col_tints[i][set])
    plt.ion()
    plt.show()

    pass

    tstart = time.time()
    num_plots = 0
    while time.time() - tstart < 1:
        for ii, cols in enumerate(colors):
            for z in range(5):
                # x_pos = [el + width for el in x_pos]
                for p in range(11):
                    bar_ax[0][ii][z][p][0].set_height(randint(-3000,3000))
                    bar_ax[1][ii][z][p][0].set_height(randint(-3000,3000))
        fig.canvas.draw()
        fig.canvas.flush_events()
        num_plots += 1
    print(num_plots)

    pass

def main():
    # reg_files = list(files_finder(folder,'Registration*.csv'))
    # i2s_files = list(files_finder(folder,'ImagePlacement_*.csv'))
    # col_analysis_files = list(files_finder(folder,'ColorToColorAndScalingAnalysis*.csv'))
    # i2s_analysis_files = list(files_finder(folder,'ImagePlacementAnalysis*.csv'))
    # scaling_files = list(files_finder(folder,'Machine*.txt'))
    files_row_c2c = simple_files_finder(folder)
    load_reg_files(files_row_c2c)



    pass

if __name__=='__main__':
    main()
