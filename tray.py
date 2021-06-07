import wx
import wx.adv
import os

dirName = os.path.dirname(os.path.abspath(__file__))
bitmapDir = os.path.join(dirName, 'bitmaps')

class TaskBarIcon(wx.adv.TaskBarIcon):
    TBMENU_RESTORE = wx.NewId()
    TBMENU_CLOSE   = wx.NewId()
    #----------------------------------------------------------------------
    def __init__(self, frame):
        wx.adv.TaskBarIcon.__init__(self)
        self.frame = frame
        
        img = wx.Image((os.path.join(bitmapDir, 'title_logo.png')), wx.BITMAP_TYPE_ANY)
        bmp = wx.Bitmap(img)
        self.icon = wx.Icon()
        self.icon.CopyFromBitmap(bmp)
        
        self.SetIcon(self.icon, "Fire Player")
        
        # Set events
        self.Bind(wx.EVT_MENU, self.OnTaskBarOpen, id=self.TBMENU_RESTORE)
        self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=self.TBMENU_CLOSE)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.OnTaskBarLeftClick)
        self.Bind(wx.adv.EVT_TASKBAR_RIGHT_DOWN, self.OnTaskBarRightClick)

    #----------------------------------------------------------------------
    def CreatePopupMenu(self, e=None):
        """
        Creates a popup menu with the function of opening and closing the program
        """
        menu = wx.Menu()
        menu.Append(self.TBMENU_RESTORE, "Open Fire Player")
        menu.AppendSeparator()
        menu.Append(self.TBMENU_CLOSE,   "Quit Fire Player")
        return menu

    #----------------------------------------------------------------------
    def OnTaskBarOpen(self, e):
        """
        Opens the program window
        """
        self.frame.Show()
        self.frame.Restore()
        
    #----------------------------------------------------------------------
    def OnTaskBarClose(self, e):
        """
        Destroys the taskbar icon and frame
        """
        self.frame.Close()

    #----------------------------------------------------------------------
    def OnTaskBarLeftClick(self, e):
        """
        Restores or hides the program window
        """
        if self.frame.Shown:
            self.frame.Hide()
        else:
            self.frame.Show()
            self.frame.Restore()

    #----------------------------------------------------------------------
    def OnTaskBarRightClick(self, e):
        """
        Creates the right-click menu
        """
        menu = self.CreatePopupMenu()
        self.PopupMenu(menu)
        menu.Destroy()