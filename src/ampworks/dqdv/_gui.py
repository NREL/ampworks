import os

from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog

path = os.path.dirname(__file__)


class InstructionsDialog(QDialog):

    def __init__(self, parent=None):
        from PyQt5.QtCore import Qt
        from PyQt5.uic import loadUi

        super().__init__(parent)

        # Load the UI file
        loadUi(path + '/ui_files/instructions.ui', self)

        # Remove help flag
        window_flags = self.windowFlags() & ~Qt.WindowContextHelpButtonHint
        self.setWindowFlags(window_flags)


class OptionsDialog(QDialog):

    def __init__(self, parent=None):
        from PyQt5.QtCore import Qt
        from PyQt5.uic import loadUi
        from PyQt5.QtGui import QDoubleValidator

        super().__init__(parent)

        # Load the UI file
        loadUi(path + '/ui_files/options.ui', self)

        # Store parent
        self.parent = parent

        # Remove help flag
        window_flags = self.windowFlags() & ~Qt.WindowContextHelpButtonHint
        self.setWindowFlags(window_flags)

        # Validator for line edits (only 0-9, -, ., and eE)
        validator = QDoubleValidator()

        self.EditBounds_neg0.setValidator(validator)
        self.EditBounds_neg100.setValidator(validator)

        self.EditBounds_pos0.setValidator(validator)
        self.EditBounds_pos100.setValidator(validator)

        self.Edit_coarse.setValidator(validator)
        self.Edit_maxiter.setValidator(validator)
        self.Edit_xtol.setValidator(validator)

        # Read in current values
        options = self.parent.get_fitter_options()

        bounds = options['bounds']
        coarse_Nx = options['coarse_Nx']
        maxiter = options['maxiter']
        xtol = options['xtol']

        self.SpinBox_smooth.setValue(options['smoothing'])
        self.SpinBox_font.setValue(options['figure_font'])

        self.EditBounds_neg0.setText(f'{bounds[0]:.2f}')
        self.EditBounds_neg100.setText(f'{bounds[1]:.2f}')

        self.EditBounds_pos0.setText(f'{bounds[2]:.2f}')
        self.EditBounds_pos100.setText(f'{bounds[3]:.2f}')

        self.Edit_coarse.setText(f'{coarse_Nx}')
        self.Edit_maxiter.setText(f'{maxiter:.0e}'.replace('+0', ''))
        self.Edit_xtol.setText(f'{xtol:.0e}'.replace('-0', '-'))

        self.VoltCheckBox.setChecked('voltage' in options['cost_terms'])
        self.dQdVCheckBox.setChecked('dqdv' in options['cost_terms'])
        self.dVdQCheckBox.setChecked('dvdq' in options['cost_terms'])

        # Program buttons
        self.CancelButton.clicked.connect(self.cancel)
        self.ApplyButton.clicked.connect(self.apply)

    def cancel(self):
        self.reject()

    def apply(self):

        try:
            smoothing = self.SpinBox_smooth.value()
            figure_font = self.SpinBox_font.value()

            bounds = []
            bounds.append(float(self.EditBounds_neg0.text()))
            bounds.append(float(self.EditBounds_neg100.text()))
            bounds.append(float(self.EditBounds_pos0.text()))
            bounds.append(float(self.EditBounds_pos100.text()))

            coarse_Nx = float(self.Edit_coarse.text())
            if not coarse_Nx.is_integer():
                raise TypeError('coarse_Nx must be type int.')

            if coarse_Nx < 3:
                raise ValueError('coarse_Nx must be >= 3.')

            coarse_Nx = int(coarse_Nx)

            maxiter = float(self.Edit_maxiter.text())
            maxiter = int(maxiter)

            xtol = float(self.Edit_xtol.text())

            cost_terms = []
            if self.VoltCheckBox.isChecked():
                cost_terms.append('voltage')

            if self.dQdVCheckBox.isChecked():
                cost_terms.append('dqdv')

            if self.dVdQCheckBox.isChecked():
                cost_terms.append('dvdq')

            options = {}
            options['smoothing'] = smoothing
            options['figure_font'] = figure_font
            options['bounds'] = bounds
            options['coarse_Nx'] = coarse_Nx
            options['maxiter'] = maxiter
            options['xtol'] = xtol
            options['cost_terms'] = cost_terms

            self.parent.set_fitter_options(options)
            self.close()

        except Exception as e:
            self.parent.pop_up(f'{type(e).__name__} : {str(e)}')

    def keyPressEvent(self, event):
        if event.key() == 16777220:
            event.ignore()
        else:
            super().keyPressEvent(event)


class MainWindow(QMainWindow):

    def __init__(self):
        from PyQt5.uic import loadUi
        import matplotlib.pyplot as plt
        from PyQt5.QtWidgets import QVBoxLayout
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
        from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT

        from . import Fitter

        super().__init__()

        # Load the UI file
        loadUi(path + '/ui_files/main.ui', self)

        # Initialize fitter and set default coarse_Nx value because it is not
        # a property of the Fitter class.
        self.fitter = Fitter()
        self.coarse_Nx = 11

        # Setup menubar
        self.actionOptions.triggered.connect(self.open_options)
        self.actionInstructions.triggered.connect(self.open_instructions)

        # Setup toolbuttons
        self.load_flags = {'neg': False, 'pos': False, 'cell': False}

        self.BrowseButton_neg.clicked.connect(self.load_neg)
        self.BrowseButton_pos.clicked.connect(self.load_pos)
        self.BrowseButton_cell.clicked.connect(self.load_cell)

        # Setup canvas
        self.figure = plt.figure('gui', layout='tight', figsize=[10, 3])
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas_layout = QVBoxLayout(self.CanvasWidget)
        self.canvas_layout.addWidget(self.canvas)

        plt.close('gui')

        self.figure.add_subplot(1, 3, 1)
        self.figure.add_subplot(1, 3, 2)
        self.figure.add_subplot(1, 3, 3)

        # Add plot toolbar
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.verticalLayout_2.addWidget(self.toolbar)
        self.toolbar._actions['home'].triggered.connect(self.update_plot)

        # Change frame style
        self.theme = self.palette().window().color().name()
        self.CanvasFrame.setStyleSheet("background-color: white;"
                                       f" border: 2px solid {self.theme};")

        # Setup sliders
        self.sliders = []
        self.sliders.append(self.ScrollBar_neg_x0)
        self.sliders.append(self.ScrollBar_neg_x100)
        self.sliders.append(self.ScrollBar_pos_x0)
        self.sliders.append(self.ScrollBar_pos_x100)

        self.ScrollBar_neg_x0.valueChanged.connect(self.update_spin_neg_x0)
        self.ScrollBar_neg_x100.valueChanged.connect(self.update_spin_neg_x100)
        self.ScrollBar_pos_x0.valueChanged.connect(self.update_spin_pos_x0)
        self.ScrollBar_pos_x100.valueChanged.connect(self.update_spin_pos_x100)

        # Setup spinboxes
        self.spinboxes = []
        self.spinboxes.append(self.SpinBox_neg_x0)
        self.spinboxes.append(self.SpinBox_neg_x100)
        self.spinboxes.append(self.SpinBox_pos_x0)
        self.spinboxes.append(self.SpinBox_pos_x100)

        self.SpinBox_neg_x0.valueChanged.connect(self.update_slide_neg_x0)
        self.SpinBox_neg_x100.valueChanged.connect(self.update_slide_neg_x100)
        self.SpinBox_pos_x0.valueChanged.connect(self.update_slide_pos_x0)
        self.SpinBox_pos_x100.valueChanged.connect(self.update_slide_pos_x100)

        # Setup fit
        self.CoarseButton.clicked.connect(self.start_coarse)
        self.FitDataButton.clicked.connect(self.start_fit)

        self.update_plot()

    def open_options(self):
        options_dialog = OptionsDialog(self)
        options_dialog.exec_()

    def get_fitter_options(self):
        options = {}
        options['smoothing'] = self.fitter.smoothing
        options['figure_font'] = self.fitter.figure_font
        options['bounds'] = self.fitter.bounds
        options['coarse_Nx'] = self.coarse_Nx
        options['maxiter'] = self.fitter.maxiter
        options['xtol'] = self.fitter.xtol
        options['cost_terms'] = self.fitter.cost_terms

        return options

    def set_fitter_options(self, options):
        self.fitter.smoothing = options['smoothing']
        self.fitter.figure_font = options['figure_font']
        self.fitter.bounds = options['bounds']
        self.coarse_Nx = options['coarse_Nx']
        self.fitter.maxiter = options['maxiter']
        self.fitter.xtol = options['xtol']
        self.fitter.cost_terms = options['cost_terms']

        self.update_plot()

    def open_instructions(self):
        instructions_dialog = InstructionsDialog(self)
        instructions_dialog.exec_()

    def file_dialog(self):
        from PyQt5.QtWidgets import QFileDialog

        file_dialog = QFileDialog()
        file_dialog.setNameFilter('CSV Files (*.csv)')
        file_dialog.exec_()

        if file_dialog.selectedFiles() != []:
            file = file_dialog.selectedFiles()[0]
        else:
            file = None

        return file

    def load_neg(self):
        import pandas as pd

        file = self.file_dialog()

        if file is not None and file.endswith('.csv'):
            df_neg = pd.read_csv(file)
        elif file is not None and file.endswith('.xls'):
            df_neg = pd.read_excel(file)
        elif file is not None and file.endswith('.xlsx'):
            df_neg = pd.read_excel(file)

        try:
            if file is None:
                self.load_flags['neg'] = False
                self.TextBrowser_neg.setText('negative electrode ocv...')
            else:
                self.fitter.df_neg = df_neg
                self.load_flags['neg'] = True
                self.TextBrowser_neg.setText('df_neg: ' + file.split('/')[-1])

        except Exception as e:
            self.load_flags['neg'] = False
            self.TextBrowser_neg.setText('negative electrode ocv...')
            self.pop_up(f'{type(e).__name__} : {str(e)}')

        self.update_plot()

    def load_pos(self):
        import pandas as pd

        file = self.file_dialog()

        if file is not None and file.endswith('.csv'):
            df_pos = pd.read_csv(file)
        elif file is not None and file.endswith('.xls'):
            df_pos = pd.read_excel(file)
        elif file is not None and file.endswith('.xlsx'):
            df_pos = pd.read_excel(file)

        try:
            if file is None:
                self.load_flags['pos'] = False
                self.TextBrowser_pos.setText('positive electrode ocv...')
            else:
                self.fitter.df_pos = df_pos
                self.load_flags['pos'] = True
                self.TextBrowser_pos.setText('df_pos: ' + file.split('/')[-1])

        except Exception as e:
            self.load_flags['pos'] = False
            self.TextBrowser_pos.setText('positive electrode ocv...')
            self.pop_up(f'{type(e).__name__} : {str(e)}')

        self.update_plot()

    def load_cell(self):
        import pandas as pd

        file = self.file_dialog()

        if file is not None and file.endswith('.csv'):
            df_cell = pd.read_csv(file)
        elif file is not None and file.endswith('.xls'):
            df_cell = pd.read_excel(file)
        elif file is not None and file.endswith('.xlsx'):
            df_cell = pd.read_excel(file)

        try:
            if file is None:
                self.load_flags['cell'] = False
                self.TextBrowser_cell.setText('full cell ocv...')
            else:
                self.fitter.df_cell = df_cell
                self.load_flags['cell'] = True
                self.TextBrowser_cell.setText('df_cell: '
                                              + file.split('/')[-1])

        except Exception as e:
            self.load_flags['cell'] = False
            self.TextBrowser_cell.setText('full cell ocv...')
            self.pop_up(f'{type(e).__name__} : {str(e)}')

        self.update_plot()

    def pop_up(self, message):
        from PyQt5.QtWidgets import QMessageBox

        QMessageBox.critical(self, 'Error', message, QMessageBox.Ok)

    def get_xvals(self):
        import numpy as np

        x = np.empty(4)
        x[0] = self.SpinBox_neg_x0.value()
        x[1] = self.SpinBox_neg_x100.value()
        x[2] = self.SpinBox_pos_x0.value()
        x[3] = self.SpinBox_pos_x100.value()

        return x

    def set_xvals(self, x):

        self.SpinBox_neg_x0.setValue(x[0])
        self.SpinBox_neg_x100.setValue(x[1])
        self.SpinBox_pos_x0.setValue(x[2])
        self.SpinBox_pos_x100.setValue(x[3])

    def update_plot(self, **kwargs):

        for slot in self.sliders + self.spinboxes:
            slot.blockSignals(True)

        if all(self.load_flags.values()):
            x = kwargs.pop('x', self.get_xvals())

            self.fitter.plot(x, fig=self.figure)

            if x[0] > x[1] or x[2] > x[3]:
                self.statusbar.showMessage('WARNING: x0 > x100')
                self.statusbar.setStyleSheet('background-color: #FF6961;')
            else:
                self.statusbar.clearMessage()
                self.statusbar.setStyleSheet(
                    f'background-color: {self.theme};')

        self.canvas.draw()

        for slot in self.sliders + self.spinboxes:
            slot.blockSignals(False)

    def update_slide_neg_x0(self, value):
        new_value = int(value * 100)
        self.ScrollBar_neg_x0.setValue(new_value)

    def update_slide_neg_x100(self, value):
        new_value = int(value * 100)
        self.ScrollBar_neg_x100.setValue(new_value)

    def update_slide_pos_x0(self, value):
        new_value = int(value * 100)
        self.ScrollBar_pos_x0.setValue(new_value)

    def update_slide_pos_x100(self, value):
        new_value = int(value * 100)
        self.ScrollBar_pos_x100.setValue(new_value)

    def update_spin_neg_x0(self, value):
        self.SpinBox_neg_x0.setValue(value / 100)
        self.update_plot()

    def update_spin_neg_x100(self, value):
        self.SpinBox_neg_x100.setValue(value / 100)
        self.update_plot()

    def update_spin_pos_x0(self, value):
        self.SpinBox_pos_x0.setValue(value / 100)
        self.update_plot()

    def update_spin_pos_x100(self, value):
        self.SpinBox_pos_x100.setValue(value / 100)
        self.update_plot()

    def start_coarse(self):

        if all(self.load_flags.values()):
            self.CoarseButton.setEnabled(False)
            self.statusbar.showMessage('Fitting...')

            QApplication.processEvents()

            summary = self.fitter.coarse_search(self.coarse_Nx)
            self.stop_fit(self.CoarseButton, summary)

        else:
            self.pop_up("Load data before fitting.")

    def start_fit(self):

        if all(self.load_flags.values()):
            self.FitDataButton.setEnabled(False)
            self.statusbar.showMessage('Fitting...')

            QApplication.processEvents()

            x = self.get_xvals()
            summary = self.fitter.constrained_fit(x)
            self.stop_fit(self.FitDataButton, summary)

        else:
            self.pop_up("Load data before fitting.")

    def format_summary(self, summary):
        x = summary.pop('x')
        x_map = summary.pop('x_map')

        for key, value in zip(x_map, x):
            summary[key] = value

        output = ''
        for key, value in summary.items():
            output += f'{key} : {value}\n'

        return output

    def stop_fit(self, button, summary):
        from PyQt5.QtWidgets import QMessageBox

        button.setEnabled(True)

        self.set_xvals(summary['x'])
        self.update_plot(x=summary['x'])

        message = self.format_summary(summary)
        QMessageBox.information(self, 'Fit summary', message, QMessageBox.Ok)


def run():
    import sys

    from PyQt5.QtCore import Qt

    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
