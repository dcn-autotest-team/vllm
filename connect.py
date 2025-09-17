# -*- coding: UTF-8 -*-
# *********************************************************************
# connect.py - 新建连接-对话框（现代化UI）
#
# Author: sunkz(sunkz@digitalchina.com) | Modernized by Assistant
# Version 2.1.0
# *********************************************************************

import wx
from wx.lib.inspection import InspectionTool

from dauto import info, g
from dauto.app.bitmaps.tool.images import icon
from dauto.app.utils.url import Url
from dauto.app.utils.validators import CharValidator

(
    PROTOCOL_ID,
    TITLE_ID,
    SERIAL_PORT_ID,
    SERIAL_BAUDRATE_ID,
    HOST_ID,
    PORT_ID,
) = [wx.NewIdRef() for _ in range(6)]

PROTOCOL_SERIAL = "Serial"
PROTOCOL_TELNET = "Telnet"
PROTOCOL_SSH = "SSH"
TITLE_TITLE = "dut"


class ConnectDialog(wx.Dialog):
    """
    供parent frame模块中的ConfigNewChannel函数使用
    Dauto平台-文件-连接窗口(快捷键Ctrl+C)
    type:目前支持Telnet TelnetCCM  Serial
    title:设备名称例如s1 s2
    host:设备连接ip地址端口号 例如172.17.100.14:10007
    说明：手动打开窗口之后会让选择日志存放路径
    """

    def __init__(self, parent):
        super().__init__(
            parent,
            id=wx.ID_ANY,
            title="连接设置",
            pos=wx.DefaultPosition,
            size=wx.Size(560, 340),
            style=wx.DEFAULT_DIALOG_STYLE | wx.CAPTION | wx.RESIZE_BORDER,
        )

        # Colors & metrics
        self.color_header_bg = wx.Colour("#0F4C81")  # 深蓝色
        self.color_body_bg = wx.Colour("#F7F9FC")    # 浅灰蓝背景
        self.color_label_fg = wx.Colour("#2C3E50")   # 深色文字
        self.color_input_bg = wx.Colour("#FFFFFF")   # 输入白色
        self.color_primary = wx.Colour("#1E88E5")    # 主按钮
        self.color_primary_hover = wx.Colour("#1565C0")
        self.color_secondary_bg = wx.Colour("#ECEFF1")
        self.color_secondary_fg = wx.Colour("#37474F")

        default_uri = (
            "Telnet://admin:wifi_debug:dcn_debug:admin@192.168.1.10:23?title=dut"
        )
        self.uri = Url.from_string(g.options.Read("dut_uri", default_uri))
        self.SetIcon(icon.Icon)

        # Root content panel to better control background and padding
        self.bg_panel = wx.Panel(self)
        self.bg_panel.SetBackgroundColour(self.color_body_bg)

        # Header (custom title bar area)
        self.header_panel = wx.Panel(self.bg_panel)
        self.header_panel.SetBackgroundColour(self.color_header_bg)
        self.header_sizer = wx.BoxSizer(wx.HORIZONTAL)

        header_title = wx.StaticText(self.header_panel, label="连接设置")
        header_font = header_title.GetFont()
        header_font.SetPointSize(14)
        header_font.SetWeight(wx.FONTWEIGHT_BOLD)
        header_title.SetFont(header_font)
        header_title.SetForegroundColour(wx.WHITE)

        self.header_sizer.Add(header_title, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 12)
        self.header_panel.SetSizer(self.header_sizer)

        # Body content
        content_pad = 14
        self.content_panel = wx.Panel(self.bg_panel)
        self.content_panel.SetBackgroundColour(self.color_body_bg)

        # Protocol choice
        self.choice = wx.RadioBox(
            self.content_panel,
            label="",
            id=PROTOCOL_ID,
            choices=[PROTOCOL_TELNET, PROTOCOL_SERIAL, PROTOCOL_SSH],
            majorDimension=3,
            style=wx.RA_SPECIFY_COLS,
        )
        self.set_font_size(self.choice, 12)

        # Serial controls
        self.serial_port = wx.Choice(
            self.content_panel,
            SERIAL_PORT_ID,
            wx.DefaultPosition,
            wx.Size(140, -1),
            [
                "com0",
                "com1",
                "com2",
                "com3",
                "com4",
                "com5",
                "com6",
                "com7",
                "com8",
                "com9",
            ],
            0,
        )
        self.serial_port.SetBackgroundColour(self.color_input_bg)

        self.serial_baudrate = wx.Choice(
            self.content_panel,
            SERIAL_BAUDRATE_ID,
            wx.DefaultPosition,
            wx.Size(140, -1),
            ["9600", "115200", "4800", "14400", "19200", "38400", "56000", "57600"],
            0,
        )
        self.serial_baudrate.SetBackgroundColour(self.color_input_bg)

        self.hostname = wx.TextCtrl(
            self.content_panel,
            HOST_ID,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.Size(220, -1),
            0,
        )
        self.hostname.SetBackgroundColour(self.color_input_bg)

        self.serial_port_label = wx.StaticText(
            self.content_panel,
            wx.ID_ANY,
            "串口端口",
            wx.DefaultPosition,
            wx.Size(-1, -1),
            0,
        )
        self.serial_baudrate_label = wx.StaticText(
            self.content_panel,
            wx.ID_ANY,
            "波特率",
            wx.DefaultPosition,
            wx.Size(-1, -1),
            0,
        )
        self.hostname_label = wx.StaticText(
            self.content_panel,
            wx.ID_ANY,
            "主机 IP",
            wx.DefaultPosition,
            wx.Size(-1, -1),
            0,
        )
        self.port_label = wx.StaticText(
            self.content_panel,
            wx.ID_ANY,
            "端口",
            wx.DefaultPosition,
            wx.Size(-1, -1),
            0,
        )

        # Typography for labels
        for label in (
            self.serial_port_label,
            self.serial_baudrate_label,
            self.hostname_label,
            self.port_label,
        ):
            font = label.GetFont()
            font.SetPointSize(11)
            label.SetFont(font)
            label.SetForegroundColour(self.color_label_fg)

        self.port = wx.TextCtrl(
            self.content_panel,
            PORT_ID,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.Size(120, -1),
            0,
            validator=CharValidator("int-only"),
        )
        self.port.SetBackgroundColour(self.color_input_bg)

        # Buttons
        self.btn = wx.Button(self.content_panel, wx.ID_OK, label="连接")
        self.btn.SetDefault()
        self.btn.Disable()
        self.btn.SetBackgroundColour(self.color_primary)
        self.btn.SetForegroundColour(wx.WHITE)

        cancel_btn = wx.Button(self.content_panel, wx.ID_CANCEL, label="取消")
        cancel_btn.SetBackgroundColour(self.color_secondary_bg)
        cancel_btn.SetForegroundColour(self.color_secondary_fg)

        # Layout
        self.__do_layout(cancel_btn, content_pad)
        self.__bind_event()
        self.__do_init()
        self.title = "dut"
        self.Centre(wx.BOTH)

    def __do_init(self):
        # 定义端口和波特率映射
        choice_map = {PROTOCOL_TELNET: 0, PROTOCOL_SERIAL: 1, PROTOCOL_SSH: 2}
        port_map = {
            "com0": 0,
            "com1": 1,
            "com2": 2,
            "com3": 3,
            "com4": 4,
            "com5": 5,
            "com6": 6,
            "com7": 7,
            "com8": 8,
            "com9": 9,
        }
        baudrate_map = {
            9600: 0,
            115200: 1,
            4800: 2,
            14400: 3,
            19200: 4,
            38400: 5,
            56000: 6,
            57600: 7,
        }
        if self.uri.protocol == PROTOCOL_SERIAL:
            self.choice.SetSelection(choice_map.get(self.uri.protocol))
            self.main_body_sizer.Show(self.serial_sizer)
            self.main_body_sizer.Hide(self.telnet_sizer)
            serial_port_index = port_map.get(self.uri.hostname)
            if serial_port_index is not None:
                self.serial_port.SetSelection(serial_port_index)
            else:
                info("Warning: Unknown serial port name.")

            baudrate_index = baudrate_map.get(self.uri.port)
            if baudrate_index is not None:
                self.serial_baudrate.SetSelection(baudrate_index)
            else:
                info("Warning: Unknown baud rate.")
            self.btn.Enable()
        else:  # SSH or Telnet
            self.choice.SetSelection(choice_map.get(self.uri.protocol))
            self.main_body_sizer.Show(self.telnet_sizer)
            self.main_body_sizer.Hide(self.serial_sizer)
            self.port.SetValue(str(self.uri.port))
            self.hostname.SetValue(self.uri.hostname)

            hostname = self.hostname.GetValue()
            self.btn.Enable() if hostname else self.btn.Disable()
        self.title = TITLE_TITLE

    def __bind_event(self):
        self.Bind(wx.EVT_RADIOBOX, self.choice_change, self.choice)
        self.Bind(wx.EVT_TEXT, self.on_set_hostname, self.hostname)
        self.Bind(wx.EVT_TEXT, self.on_set_hostname, self.port)
        self.Bind(wx.EVT_CLOSE, self.close)
        self.Bind(wx.EVT_BUTTON, self.on_confirm, self.btn)

    def __do_layout(self, cancel_btn: wx.Button, content_pad: int):
        # Main root sizer for bg_panel: Header + Body
        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(self.header_panel, 0, wx.EXPAND)

        # content wrapper with padding and card-like panel
        body_wrapper = wx.Panel(self.bg_panel)
        body_wrapper.SetBackgroundColour(self.color_body_bg)
        body_sizer = wx.BoxSizer(wx.VERTICAL)

        # Card panel for content to improve contrast
        card = wx.Panel(body_wrapper)
        card.SetBackgroundColour(wx.Colour("#FFFFFF"))
        card.SetWindowVariant(wx.WINDOW_VARIANT_NORMAL)
        card_sizer = wx.BoxSizer(wx.VERTICAL)

        # Protocol choice
        card_sizer.Add(self.choice, 0, wx.ALL | wx.EXPAND, content_pad)

        # Serial Port & Rate row
        self.serial_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.serial_sizer.Add(self.serial_port_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        self.serial_sizer.Add(self.serial_port, 0, wx.RIGHT, 20)
        self.serial_sizer.Add(self.serial_baudrate_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        self.serial_sizer.Add(self.serial_baudrate, 0)
        card_sizer.Add(self.serial_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, content_pad)

        # Host & Port row
        self.telnet_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.telnet_sizer.Add(self.hostname_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        self.telnet_sizer.Add(self.hostname, 0, wx.RIGHT, 20)
        self.telnet_sizer.Add(self.port_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        self.telnet_sizer.Add(self.port, 0)
        card_sizer.Add(self.telnet_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, content_pad)

        # Divider line
        card_sizer.Add(wx.StaticLine(card), 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, content_pad)

        # Buttons row centered
        button_row = wx.BoxSizer(wx.HORIZONTAL)
        button_row.AddStretchSpacer(1)
        button_row.Add(self.btn, 0, wx.ALL, 8)
        button_row.AddSpacer(8)
        button_row.Add(cancel_btn, 0, wx.ALL, 8)
        button_row.AddStretchSpacer(1)
        card_sizer.Add(button_row, 0, wx.EXPAND | wx.ALL, content_pad)

        card.SetSizer(card_sizer)
        body_sizer.Add(card, 1, wx.EXPAND | wx.ALL, content_pad)
        body_wrapper.SetSizer(body_sizer)

        # Collect
        root.Add(body_wrapper, 1, wx.EXPAND)
        self.bg_panel.SetSizer(root)

        # Outer sizer of dialog
        outer = wx.BoxSizer(wx.VERTICAL)
        outer.Add(self.bg_panel, 1, wx.EXPAND)
        self.SetSizer(outer)
        self.Layout()
        self.SetMinSize(wx.Size(520, 320))

        # Keep a reference to toggle visibility later
        self.main_body_sizer = card_sizer
        self.title = TITLE_TITLE

    @staticmethod
    def set_font_size(widget, size):
        font = widget.GetFont()
        font.SetPointSize(size)
        widget.SetFont(font)

    def on_confirm(self, evt):
        self.port.GetValidator().Validate(self.title)
        self.on_connect(evt)
        evt.Skip()

    def on_connect(self, evt):  # 预留connect时获取参数
        connect_protocol = self.choice.GetStringSelection()
        if connect_protocol == PROTOCOL_SSH:  # SSH
            self.hostname.GetValue()
            self.port.GetValue()
        elif connect_protocol == PROTOCOL_TELNET:  # Telnet
            self.hostname.GetValue()
            self.port.GetValue()
        else:
            self.serial_port.GetStringSelection()
            self.serial_baudrate.GetStringSelection()
        self.title = TITLE_TITLE
        evt.Skip()

    def close(self, _):
        self.Destroy()
        if _:
            _.Skip()

    def choice_change(self, event):
        selection = self.choice.GetStringSelection()
        hostname = self.hostname.GetValue()
        if selection == PROTOCOL_SSH:  # SSH
            self.port.SetValue("22")
            self.main_body_sizer.Show(self.telnet_sizer)
            self.main_body_sizer.Hide(self.serial_sizer)
            self.btn.Enable() if hostname else self.btn.Disable()
        elif selection == PROTOCOL_TELNET:  # Telnet
            self.port.SetValue("23")
            self.main_body_sizer.Show(self.telnet_sizer)
            self.main_body_sizer.Hide(self.serial_sizer)
            self.btn.Enable() if hostname else self.btn.Disable()
        elif selection == PROTOCOL_SERIAL:
            self.main_body_sizer.Show(self.serial_sizer)
            self.main_body_sizer.Hide(self.telnet_sizer)
            self.btn.Enable()
        self.Layout()
        event.Skip()

    def on_set_hostname(self, evt):
        choice = self.choice.GetSelection()
        title = TITLE_TITLE
        hostname = self.hostname.GetValue()
        if choice == 0 or choice == 2:
            if title and hostname:
                self.btn.Enable()
            else:
                self.btn.Disable()
        elif title and choice == 1:
            self.btn.Enable()
        else:
            self.btn.Disable()
        evt.Skip()


if __name__ == "__main__":

    class MyApp(wx.App):
        def OnInit(self):
            dialog = ConnectDialog(None)
            self.SetAssertMode(wx.APP_ASSERT_SUPPRESS)
            InspectionTool().Show(wx.FindWindowAtPointer() or self, True)
            self.SetTopWindow(dialog)
            dialog.Show()
            return True

    app = MyApp(0)
    app.MainLoop()

