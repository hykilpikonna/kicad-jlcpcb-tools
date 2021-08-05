import csv
import logging
import os
import re
import sys
from pathlib import Path
from zipfile import ZipFile

import wx
from pcbnew import *

from .fabrication import JLCPCBFabrication

# from .library import JLCPCBLibrary


class JLCPCBPlugin(ActionPlugin):
    def __init__(self):
        super(JLCPCBPlugin, self).__init__()

        self.name = "JLCPCB Tools"
        self.category = "Fabrication data generation"
        self.pcbnew_icon_support = hasattr(self, "show_toolbar_button")
        self.show_toolbar_button = True
        path, filename = os.path.split(os.path.abspath(__file__))
        self.icon_file_name = os.path.join(path, "jlcpcb-icon.png")
        self.description = "Generate JLCPCB conform Gerber, Excellon, BOM and CPL files"

    def Run(self):
        """Run is caled when the action button is clicked."""
        dialog = Dialog(None)
        dialog.Center()
        dialog.ShowModal()
        dialog.Destroy()


class FabricationTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # panel = wx.Panel(self)
        log = wx.TextCtrl(
            self, wx.ID_ANY, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1, 400)
        )
        # description = wx.StaticText(
        #     panel, label="Generate JLCPCB production and assembly files."
        # )
        generate_button = wx.Button(self, label="Generate")
        # clsbtn = wx.Button(panel, label="Close")
        # clsbtn.Bind(wx.EVT_BUTTON, self.close)
        generate_button.Bind(wx.EVT_BUTTON, self.generate)

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(generate_button)
        # buttonSizer.Add(clsbtn)
        layout = wx.BoxSizer(wx.VERTICAL)
        # layout.Add(description, flag=wx.EXPAND | wx.BOTTOM | wx.TOP | wx.LEFT, border=5)
        layout.Add(buttonSizer, flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        layout.Add(
            log, flag=wx.EXPAND | wx.BOTTOM | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        self.SetSizer(layout)
        self.Refresh()
        self.Layout()
        # redirect text here
        sys.stdout = log
        self.init_logger()
        self.fabrication = JLCPCBFabrication()

    def generate(self, e):
        e.Skip()
        self.fabrication.setup()
        self.fabrication.generate_geber()
        self.fabrication.generate_excellon()
        self.fabrication.zip_gerber_excellon()
        self.fabrication.generate_cpl()
        self.fabrication.generate_bom()

    def init_logger(self):
        # Remove all handlers associated with the root logger object.
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y.%m.%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        root.addHandler(handler)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Test")


class LibraryTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "This is the second tab", (20, 20))


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(
            self,
            parent,
            id=-1,
            title="KiCAD JLCPCB tools",
            size=(820, 620),
            style=wx.DEFAULT_DIALOG_STYLE
            | wx.CLOSE_BOX
            | wx.MAXIMIZE_BOX
            | wx.RESIZE_BORDER,
        )
        self.SetIcon(
            wx.Icon(
                os.path.join(
                    os.path.abspath(os.path.dirname(__file__)), "jlcpcb-icon.png"
                )
            )
        )

        panel = wx.Panel(self)
        notebook = wx.Notebook(panel)

        fabrication_tab = FabricationTab(notebook)
        library_tab = LibraryTab(notebook)

        notebook.AddPage(fabrication_tab, "Fabrication data")
        notebook.AddPage(library_tab, "Parts library")
        sizer = wx.BoxSizer()
        sizer.Add(notebook, 1, wx.EXPAND)
        panel.SetSizer(sizer)


JLCPCBPlugin().register()
