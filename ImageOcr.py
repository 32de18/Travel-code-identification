import wx
import threading

from main_v2 import OcrImage

zt = 0
global_obj = None


def do_it(key):
    global zt
    ocr = OcrImage()
    ocr.outer_process(key)
    zt -= 1

def jzt():
    global zt, global_obj
    while True:
        if zt == 0:
            global_obj.onEnd()
            break

class ButtonFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, '行程码识别器',
                          size=(300, 300), style=wx.DEFAULT_FRAME_STYLE)
        self.sizer = wx.GridBagSizer(2, 2)
        self.panel = wx.Panel(self, -1)
        self.button = wx.Button(self.panel, -1, "选择待识别压缩包", pos=(80, 50))
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        # self.button1 = wx.Button(self.panel, -1, "选择疫区文件", pos=(90, 150))
        self.sizer.Add(self.button, pos=(0, 1), flag=wx.EXPAND)
        # self.sizer.Add(self.button1, pos=(1, 1), flag=wx.EXPAND)
        # self.Bind(wx.EVT_BUTTON, self.OnLoad, self.button1)
        self.button.SetDefault()
        # self.button1.SetDefault()
        self.text = None
        self.text_complete = None

    def onStart(self):
        self.button.Hide()
        self.text = wx.StaticText(self.panel, label="正在识别", pos=(100, 50))

    def onEnd(self):
        self.text.Hide()
        self.button.Show()
        self.text_complete = wx.StaticText(self.panel, label="识别完成！！", pos=(100, 80))
        self.text_complete.Show()

    def OnClick(self, event):
        global zt, global_obj
        zt = False
        global_obj = self
        filesFilter = "All files (*.*)|*.*"
        fileDialog = wx.FileDialog(None, message="Choose a directory:", wildcard=filesFilter,
                                   style=wx.FD_OPEN | wx.FD_MULTIPLE)
        dialogResult = fileDialog.ShowModal()
        if dialogResult != wx.ID_OK:
            pass
        paths = fileDialog.GetPaths()
        fileDialog.Destroy()
        self.onStart()
        length = len(paths)
        if length > 1:
            path1 = paths[length // 2:]
            path2 = paths[:length // 2]
            obj1 = threading.Thread(target=do_it, kwargs={"key": path1})  # 在这可以优化速度
            obj2 = threading.Thread(target=do_it, kwargs={"key": path2})  # 在这可以优化速度
            obj1.start()
            obj2.start()
            zt += 2
        else:
            obj = threading.Thread(target=do_it, kwargs={"key": paths})  # 在这可以优化速度
            obj.start()
            zt += 1
        obj3 = threading.Thread(target=jzt)  # 此线程可以控制前端展示的状态
        obj3.start()

    def OnLoad(self, event):
        pass


if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = ButtonFrame()
    frame.Show()
    # frame.onStart()
    app.MainLoop()
