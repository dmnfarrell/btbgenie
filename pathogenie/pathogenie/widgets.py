# -*- coding: utf-8 -*-

"""
    Qt widgets for pathogenie.
    Created Jan 2020
    Copyright (C) Damien Farrell

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 2
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

from PySide2 import QtCore, QtGui
from PySide2.QtCore import QObject
from PySide2.QtWidgets import *
from PySide2.QtGui import *

import sys, os, io
import numpy as np
import pandas as pd
import string

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
from . import tools

def dialogFromOptions(parent, opts, sections=None,
                      sticky='news', wrap=2, section_wrap=2):
    """Get Qt widgets dialog from a dictionary of options"""

    sizepolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    sizepolicy.setHorizontalStretch(1)
    sizepolicy.setVerticalStretch(0)

    style = '''
    QLabel {
        font-size: 12px;
    }
    QWidget {
        max-width: 130px;
        min-width: 30px;
        font-size: 14px;
    }
    QPlainTextEdit {
        max-height: 80px;
    }

    '''

    if sections == None:
        sections = {'options': opts.keys()}

    widgets = {}
    dialog = QWidget(parent)
    dialog.setSizePolicy(sizepolicy)

    l = QGridLayout(dialog)
    l.setSpacing(2)
    l.setAlignment(QtCore.Qt.AlignLeft)
    scol=1
    srow=1
    for s in sections:
        row=1
        col=1
        f = QGroupBox()
        f.setSizePolicy(sizepolicy)
        f.setTitle(s)
        #f.resize(50,100)
        #f.sizeHint()
        l.addWidget(f,srow,scol)
        gl = QGridLayout(f)
        gl.setAlignment(QtCore.Qt.AlignTop)
        srow+=1
        #gl.setSpacing(10)
        for o in sections[s]:
            label = o
            val = None
            opt = opts[o]
            if 'label' in opt:
                label = opt['label']
            val = opt['default']
            t = opt['type']
            lbl = QLabel(label)
            gl.addWidget(lbl,row,col)
            lbl.setStyleSheet(style)
            if t == 'combobox':
                w = QComboBox()
                w.addItems(opt['items'])
                #w.view().setMinListWidth(100)
                try:
                    w.setCurrentIndex(opt['items'].index(str(opt['default'])))
                except:
                    w.setCurrentIndex(0)
            elif t == 'entry':
                w = QLineEdit()
                w.setText(str(val))
            elif t == 'textarea':
                w = QPlainTextEdit()
                #w.setSizePolicy(sizepolicy)
                w.insertPlainText(str(val))
            elif t == 'slider':
                w = QSlider(QtCore.Qt.Horizontal)
                s,e = opt['range']
                w.setTickInterval(opt['interval'])
                w.setSingleStep(opt['interval'])
                w.setMinimum(s)
                w.setMaximum(e)
                w.setTickPosition(QSlider.TicksBelow)
                w.setValue(val)
            elif t == 'spinbox':
                w = QSpinBox()
                w.setValue(val)
                if 'interval' in opt:
                    w.setSingleStep(opt['interval'])
            elif t == 'checkbox':
                w = QCheckBox()
                w.setChecked(val)
            elif t == 'font':
                w = QFontComboBox()
                w.resize(w.sizeHint())
                w.setCurrentIndex(1)
            col+=1
            gl.addWidget(w,row,col)
            w.setStyleSheet(style)
            widgets[o] = w
            #print (o, row, col)
            if col>=wrap:
                col=1
                row+=1
            else:
                col+=2
        if scol >= section_wrap:
            scol=1
        else:
            scol+=1
    return dialog, widgets

def getWidgetValues(widgets):
    """Get values back from a set of widgets"""

    kwds = {}
    for i in widgets:
        val = None
        if i in widgets:
            w = widgets[i]
            if type(w) is QLineEdit:
                try:
                    val = float(w.text())
                except:
                    val = w.text()
            elif type(w) is QPlainTextEdit:
                val = w.toPlainText()
            elif type(w) is QComboBox or type(w) is QFontComboBox:
                val = w.currentText()
            elif type(w) is QCheckBox:
                val = w.isChecked()
            elif type(w) is QSlider:
                val = w.value()
            elif type(w) is QSpinBox:
                val = w.value()
            if val != None:
                kwds[i] = val
    kwds = kwds
    return kwds

def setWidgetValues(widgets, values):
    """Set values for a set of widgets from a dict"""

    kwds = {}
    for i in values:
        val = values[i]
        if i in widgets:
            #print (i, val, type(val))
            w = widgets[i]
            if type(w) is QLineEdit:
                w.setText(str(val))
            elif type(w) is QPlainTextEdit:
                w.insertPlainText(str(val))
            elif type(w) is QComboBox or type(w) is QFontComboBox:
                w.setCurrentIndex(1)
            elif type(w) is QCheckBox:
                w.setChecked(val)
            elif type(w) is QSlider:
                w.setValue(val)
            elif type(w) is QSpinBox:
                w.setValue(val)
    return

class ToolBar(QWidget):
    """Toolbar class"""
    def __init__(self, table, parent=None):
        super(ToolBar, self).__init__(parent)
        self.parent = parent
        self.table = table
        self.layout = QVBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.layout.setContentsMargins(2,2,2,2)
        self.setLayout(self.layout)
        self.createButtons()
        self.setMaximumWidth(40)
        return

    def createButtons(self):

        funcs = {'load':self.table.load, 'save':self.table.save,
                 'importexcel': self.table.load,
                 'copy':self.table.copy, 'paste':self.table.paste,
                 'plot':self.table.plot,
                 'transpose':self.table.pivot,
                 'pivot':self.table.pivot}
        icons = {'load': 'document-new', 'save': 'document-save-as',
                 'importexcel': 'x-office-spreadsheet',
                 'copy': 'edit-copy', 'paste': 'edit-paste',
                 'plot':'insert-image',
                 'transpose':'object-rotate-right',
                 'pivot': 'edit-undo',
                 }
        for name in funcs:
            self.addButton(name, funcs[name], icons[name])

    def addButton(self, name, function, icon):

        layout=self.layout
        button = QPushButton(name)
        button.setGeometry(QtCore.QRect(30,40,30,40))
        button.setText('')
        iconw = QIcon.fromTheme(icon)
        button.setIcon(QIcon(iconw))
        button.setIconSize(QtCore.QSize(20,20))
        button.clicked.connect(function)
        button.setMinimumWidth(30)
        layout.addWidget(button)

class BaseOptions(object):
    """Class to generate widget dialog for dict of options"""
    def __init__(self, parent=None, opts={}, groups={}):
        """Setup variables"""

        self.parent = parent
        self.groups = groups
        self.opts = opts
        return

    def applyOptions(self):
        """Set the plot kwd arguments from the widgets"""

        self.kwds = getWidgetValues(self.widgets)
        return

    def apply(self):
        self.applyOptions()
        if self.callback != None:
            self.callback()
        return

    def showDialog(self, parent, wrap=2, section_wrap=2):
        """Auto create tk vars, widgets for corresponding options and
           and return the frame"""

        dialog, self.widgets = dialogFromOptions(parent, self.opts, self.groups,
                                wrap=wrap, section_wrap=section_wrap)
        return dialog

    def setWidgetValue(self, key, value):
        "Set a widget value"

        setWidgetValues(self.widgets, {key: value})
        self.applyOptions()
        return

    def increment(self, key, inc):
        """Increase the value of a widget"""

        new = self.kwds[key]+inc
        self.setWidgetValue(key, new)
        return

class DynamicDialog(QDialog):
    """Dynamic form using baseoptions"""

    def __init__(self, parent=None, options={}, groups=None, title='Dialog'):
        super(DynamicDialog, self).__init__(parent)
        self.setWindowTitle(title)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.opts = BaseOptions(self, options, groups)
        dialog = self.opts.showDialog(self, wrap=1, section_wrap=1)
        layout.addWidget(dialog)
        buttonbox = QDialogButtonBox(self)
        buttonbox.addButton("Cancel", QDialogButtonBox.RejectRole)
        buttonbox.addButton("Ok", QDialogButtonBox.AcceptRole)
        self.connect(buttonbox, QtCore.SIGNAL("accepted()"), self, QtCore.SLOT("accept()"))
        self.connect(buttonbox, QtCore.SIGNAL("rejected()"), self, QtCore.SLOT("reject()"))
        layout.addWidget(buttonbox)
        return

    def get_values():
        """Get the widget values"""

        kwds = self.opts.kwds
        return kwds

class FileViewer(QDialog):
    """Sequence records features viewer"""
    def __init__(self, parent=None, filename=None):

        #QDialog.__init__(self)
        super(FileViewer, self).__init__(parent)
        self.ed = ed = QPlainTextEdit(self, readOnly=True)
        #ed.setStyleSheet("font-family: monospace; font-size: 14px;")
        font = QFont("Monospace")
        font.setPointSize(10)
        font.setStyleHint(QFont.TypeWriter)
        self.ed.setFont(font)
        self.setWindowTitle('sequence features')
        self.setGeometry(QtCore.QRect(200, 200, 800, 800))
        #self.setCentralWidget(ed)
        l = QVBoxLayout(self)
        self.setLayout(l)
        #w = self.recselect = QComboBox()
        #l.addWidget(QLabel('contig'))
        #l.addWidget(w)
        l.addWidget(ed)
        self.show()

    def show_records(self, recs, format='genbank'):

        from Bio import SeqIO
        recs = SeqIO.to_dict(recs)
        if format == 'genbank':
            for r in recs:
                self.ed.appendPlainText(recs[r].format('genbank'))
        elif format == 'gff':
            tools.save_gff(recs,'temp.gff')
            f = open('temp.gff','r')
            for l in f.readlines():
                self.ed.appendPlainText(l)
        recnames = list(recs.keys())
        return

class PlotViewer(QDialog):
    def __init__(self, parent=None):
        super(PlotViewer, self).__init__(parent)
        from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
        self.setGeometry(QtCore.QRect(200, 200, 600, 600))
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        #self.show()
        #self.show_figure()
        return

    def show_figure(self, fig):

        from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
        import matplotlib.pyplot as plt

        #ax.plot(range(10))
        canvas = FigureCanvas(fig)
        self.grid.addWidget(canvas)
        self.fig = fig
        #self.ax = ax
        return
