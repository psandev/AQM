import sys
import time
import copy
import pandas as pd
# import seaborn as sns
import numpy as np
import os
from datetime import datetime
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from aqm_gui_3 import Ui_MainWindow
import natsort


class AQMApp(QMainWindow, Ui_MainWindow):
    row_data_c2c = pd.DataFrame()
    data_c2c = pd.DataFrame()
    col_tints = [['#f2f2f2', '#cccccc', '#a6a6a6', '#808080', '#666666'],
                 ['#e6ffff', '#b3ffff', '#80ffff', '#4dffff', '#00ffff'],
                 ['#ffffcc', '#ffff99', '#ffff66', '#ffff33', '#ffff00'],
                 ['#ffe6ff', '#ffb3ff', '#ff80ff', '#ff4dff', '#ff00ff']]
    files = []
    colors = {'Black': 'k', 'Cyan': 'c', 'Yellow': 'y', 'Magenta': 'm'}
    plt_col = ['Black', 'Cyan', 'Yellow', 'Magenta']

    def __init__(self):
        super(QMainWindow, self).__init__()
        self.setupUi(self)
        self._root_dir = ''
        self._files_row_c2c = []
        self._files_row_i2s = []
        self._files_analysis_c2c = []
        self._files_correction = []
        self._data_row_c2c = pd.DataFrame()
        self._dist = 3048
        self._col_base = 'Black'
        self._colors = []
        self._pannels_removed = []
        self._colors_removed = []
        self._sets_removed = []
        self.widget_c2c = QtWidgets.QWidget()
        self.tabWidget.addTab(self.widget_c2c, 'C2C')
        self.widget_c2c.fig = MyFigure(self)
        self.widget_c2c.canv = FigureCanvas(self.widget_c2c.fig)
        self.widget_c2c.toolbar = NavigationToolbar2QT(self.widget_c2c.canv, self)
        layout = QtWidgets.QVBoxLayout(self.widget_c2c)
        layout.addWidget(self.widget_c2c.toolbar)
        layout.addWidget(self.widget_c2c.canv)
        self.setLayout(layout)

        self.btn_load.clicked.connect(self.get_files_list)
        self.list_panels.itemChanged.connect(self.setPanelItems)
        self.list_colors.itemChanged.connect(self.setColorItems)
        self.list_sets.itemChanged.connect(self.setSetItems)

    def get_files_list(self):
        AQMApp.row_data_c2c = pd.DataFrame()
        AQMApp.data_c2c = pd.DataFrame()
        self._data_row_c2c = pd.DataFrame()
        self._root_dir = QtWidgets.QFileDialog.getExistingDirectory(options=QtWidgets.QFileDialog.ShowDirsOnly)
        subdur_raw = os.path.join(self._root_dir, 'RawResults')
        subdir_analysis = os.path.join(self._root_dir, 'AnalysisResults')
        subdir_correction = os.path.join(self._root_dir, 'CorrectionOperators')
        self._files_row_c2c = natsort.natsorted(
            [os.path.join(subdur_raw, f) for f in os.listdir(subdur_raw) if f.startswith('Registration')])
        self._files_row_i2s = [os.path.join(subdur_raw, f) for f in os.listdir(subdur_raw) if f.startswith('ImagePlacement_')]
        self._files_analysis_i2s = [f for f in os.listdir(subdir_analysis) if f.startswith('ImagePlacementAnalysis_')]
        self._files_analysis_c2c = [f for f in os.listdir(subdir_analysis) if f.startswith('ColorToColorAndScalingAnalysis_')]
        self._files_correction = natsort.natsorted([f for f in os.listdir(subdir_correction) if f.startswith('Machine')])
        self.load_data_row_c2c()
        self.adjust_data_row_c2c()
        self.draw_plots()


    def load_data_row_c2c(self):
        if self._files_row_c2c:
            for j in self._files_row_c2c:
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
                file_data = pd.read_csv(j, skiprows=7, header=0, index_col=0)
                file_data.insert(0, 'Sheet', page_id)
                file_data.insert(1, 'Panel', panel_id)
                file_data.insert(2, 'Status', status)
                self._data_row_c2c = self._data_row_c2c.append(file_data)
            self._data_row_c2c.columns = ['Sheet', 'Panel', 'Status', 'Set1_X', 'Set1_Y', 'Set2_X', 'Set2_Y', 'Set3_X',
                                          'Set3_Y', 'Set4_X', 'Set4_Y', 'Set5_X','Set5_Y']

    def adjust_data_row_c2c(self):
        self._colors = self._data_row_c2c.index[:4].tolist()
        self._colors.remove(self._col_base)
        self._colors.insert(0,self._col_base)
        list_y = ['Set1_Y', 'Set2_Y', 'Set3_Y', 'Set4_Y', 'Set5_Y']
        list_x = ['Set1_X', 'Set2_X', 'Set3_X', 'Set4_X', 'Set5_X']
        for i in self._colors:
            if i=='Magenta' or i == self._col_base:
                self._data_row_c2c.loc[i, list_y] -= self._dist
            if i == 'Yellow' or i=='Magenta':
                self._data_row_c2c.loc[i,  list_x] -= self._dist
            if i == self._col_base:
                xbase = self._data_row_c2c.loc[self._col_base, list_x]
                ybase = self._data_row_c2c.loc[self._col_base, list_y]
            else:
                xbase.index = [i] * len(xbase)
                ybase.index = [i] * len(ybase)
                self._data_row_c2c.loc[i, list_x] = self._data_row_c2c.loc[i, list_x].subtract(xbase)
                self._data_row_c2c.loc[i, list_y] = self._data_row_c2c.loc[i, list_y].subtract(ybase)
            AQMApp.data_c2c = copy.deepcopy(self._data_row_c2c)
            AQMApp.row_data_c2c = copy.deepcopy(self._data_row_c2c)
            self._data_row_c2c = self._data_row_c2c.drop(self._col_base)
        # self._data_row_c2c = copy.deepcopy(a)
        self._colors.remove(self._col_base)
        pass

    def setPanelItems(self, item):
        if item.checkState() == QtCore.Qt.Checked:
            self._pannels_removed.remove(int(item.text()))
            self.remove_panels_colors_sets()
            self.draw_plots()
            # print('Item Checked: %d',  int(item.text()))
            # print('Panels to: %d', self.pannels_removed)
        if item.checkState() == QtCore.Qt.Unchecked:
            self._pannels_removed.append(int(item.text()))
            self.remove_panels_colors_sets()
            self.draw_plots()
            # print('Item Unchecked: %d', int(item.text()))
            # print('Panels to: %d', self.pannels_removed)

    def setColorItems(self, item):
        if item.checkState() == QtCore.Qt.Checked:
            self._colors_removed.remove(int(item.text()))
        if item.checkState() == QtCore.Qt.Unchecked:
            self._colors_removed.append(int(item.text()))

    def setSetItems(self, item):
        if item.checkState() == QtCore.Qt.Checked:
            self._sets_removed.remove(int(item.text()))

        if item.checkState() == QtCore.Qt.Unchecked:
            self._sets_removed.append(int(item.text()))

    def remove_panels_colors_sets(self):
        AQMApp.data_c2c = copy.deepcopy(AQMApp.row_data_c2c)
        for i in self._pannels_removed:
            AQMApp.data_c2c.iloc[np.where(AQMApp.data_c2c.Panel == i)[0], [3,4,5,6,7,8,9,10,11,12]]=np.nan
            pass

    def draw_plots(self):
        """ Plot Plots """
        self.widget_c2c.fig.start_plotting_thread(on_finish=self.finish_drawing_plots)

    def finish_drawing_plots(self):
        """ Finish drawing plots """
        # self.widget_c2c.fig.canvas.update()
        self.widget_c2c.canv.draw()

        # self.widget_c2c.canv.flush_events()
        # self.show()




class MyFigure(Figure, QtCore.QThread):
    def __init__(self, parent):
        QtCore.QThread.__init__(self, parent)
        Figure.__init__(self)
        self.clear()

    def start_plotting_thread(self,on_finish=None):
        """ Start plotting """
        if on_finish is not None:
            self.finished.connect(on_finish)
        self.start()


    def run(self):
        self.clear()
        start_time = datetime.now()
        ax = self.subplots(nrows=3, ncols=2)
        self.tight_layout()
        b = []
        b.append([0, 1, 2, 3, 5, 7, 9, 11])
        b.append([0, 1, 2, 4, 6, 8, 10, 12])
        for i, col in enumerate(AQMApp.plt_col[1:]):
            for j in range(2):
                ax[i][j].clear()
                c2c_median = AQMApp.data_c2c.iloc[:, b[j]].ix[col].groupby('Panel').agg(np.median).iloc[:, 1:]
                # bar, = ax[i][j].bar(np.arange(1,12),c2c_median.transpose(),width = 0.3,color=AQMApp.col_tints[i+1] * 11,edgecolor = 'k')
                bar = c2c_median.plot(kind='bar', ax=ax[i][j], color=AQMApp.col_tints[i+1] * 11,edgecolor = 'k')
                # ax[i][j].draw_artist(ax[i][j].patch)
                # ax[i][j].draw_artist(bar)
                self.canvas.update()
                self.canvas.flush_events()
        self.subplots_adjust(wspace=0, top=1, right=0.995, left=0.044, bottom=0.08, hspace=0)
        plt.show()
        time_elapsed = datetime.now() - start_time
        print('Time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))

def main():
    def my_excepthook(type, value, tback):
        # log the exception here
        # then call the default handler
        sys.__excepthook__(type, value, tback)
    sys.excepthook = my_excepthook

    app = QtWidgets.QApplication(sys.argv)
    main_window = AQMApp()
    app.setActiveWindow(main_window)
    # main_window.showMaximized()
    main_window.show()
    app.exec_()


if __name__ == '__main__':
    main()
