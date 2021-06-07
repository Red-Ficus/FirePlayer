import os
import time
import wx
import wx.adv
import MplayerCtrl as mpc
import wx.lib.buttons as buttons
import tray

dirName = os.path.dirname(os.path.abspath(__file__))
bitmapDir = os.path.join(dirName, 'bitmaps')

class Frame(wx.Frame):
    #----------------------------------------------------------------------
    def __init__(self, parent, id, title, mplayer):
        wx.Frame.__init__(self, parent, id, title)
        icon = wx.Icon(os.path.join(bitmapDir, 'title_logo.png'))
        self.SetIcon(icon)
        self.panel = wx.Panel(self)
        self.SetBackgroundColour(wx.Colour(239,72,35))

        sp = wx.StandardPaths.Get()
        self.currentFolder = sp.GetDocumentsDir()
        self.currentVolume = 50

        self.CreateStatusBar()
        self.CreateMenu()

        self.tbIcon = tray.TaskBarIcon(self)
        self.Bind(wx.EVT_ICONIZE, self.onMinimize)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        
        # Create sizers
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        controlSizer = self.build_controls()
        sliderSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.mpc = mpc.MplayerCtrl(self.panel, -1, mplayer)
        self.playbackSlider = wx.Slider(self.panel, size=wx.DefaultSize)
        sliderSizer.Add(self.playbackSlider, 1, wx.ALL|wx.EXPAND, 5)
        
        # Create a volume control
        self.volumeCtrl = wx.Slider(self.panel)
        self.volumeCtrl.SetRange(0, 100)
        self.volumeCtrl.SetValue(self.currentVolume)
        self.volumeCtrl.Bind(wx.EVT_SLIDER, self.on_set_volume)
        controlSizer.Add(self.volumeCtrl, 0, wx.ALL, 5)

        # Create a track counter
        self.trackCounter = wx.StaticText(self.panel, label="00:00")
        sliderSizer.Add(self.trackCounter, 0, wx.ALL|wx.CENTER, 5)

        # Create a playback timer
        self.playbackTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_update_playback, self.playbackTimer)
        
        mainSizer.Add(self.mpc, 1, wx.ALL|wx.EXPAND, 1)
        mainSizer.Add(sliderSizer, 0, wx.ALL|wx.EXPAND, 5)
        mainSizer.Add(controlSizer, 0, wx.ALL|wx.CENTER, 5)
        self.panel.SetSizer(mainSizer)

        self.panel.Bind(mpc.EVT_MEDIA_STARTED, self.on_media_started)
        self.panel.Bind(mpc.EVT_MEDIA_FINISHED, self.on_media_finished)
        self.panel.Bind(mpc.EVT_PROCESS_STARTED, self.on_process_started)
        self.panel.Bind(mpc.EVT_PROCESS_STOPPED, self.on_process_stopped)
        
        self.SetSize((450, 350))
        self.panel.Layout()

        self.Centre()
        self.Show()
        
    #----------------------------------------------------------------------
    def build_btn(self, btnDict, sizer):
        bmp = btnDict['bitmap']
        handler = btnDict['handler']
        
        img = wx.Bitmap(os.path.join(bitmapDir, bmp))
        btn = buttons.GenBitmapButton(self.panel, bitmap=img, style=wx.NO_BORDER, name=btnDict['name'])
        btn.SetBackgroundColour(wx.Colour(239,72,35))
        btn.SetInitialSize()
        btn.Bind(wx.EVT_BUTTON, handler)
        sizer.Add(btn, 0, wx.LEFT, 50)
        
    #----------------------------------------------------------------------
    def build_controls(self):
        """
        Builds the audio bar controls
        """
        controlSizer = wx.BoxSizer(wx.HORIZONTAL)

        btnData = [{'bitmap':'play_button.png',
                    'handler':self.on_pause, 'name':'pause'},
                   {'bitmap':'stop_button.png',
                    'handler':self.on_stop, 'name':'stop'}]
        for btn in btnData:
            self.build_btn(btn, controlSizer)
        
        return controlSizer

    #----------------------------------------------------------------------
    def CreateMenu(self):
        """
        Creates a menu
        """
        fileMenu = wx.Menu()
        menuOpen = fileMenu.Append(wx.ID_FILE, "&Open File...", " Open a file")
        fileMenu.AppendSeparator()
        menuQuit = fileMenu.Append(wx.ID_EXIT, "&Quit"," Terminate the program")
        helpmenu = wx.Menu()
        menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About..."," Information about this program")
        
        # Create a menubar
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpmenu, "&Help")

        # Sets events
        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnQuit, menuQuit)

    #----------------------------------------------------------------------
    def onClose(self, e):
        """
        Destroys the taskbar icon and the frame
        """
        if self.mpc.process_alive:
            self.mpc.Quit()
        self.tbIcon.RemoveIcon()
        self.tbIcon.Destroy()
        
        wx.GetApp().ExitMainLoop()
        self.Close()

    #----------------------------------------------------------------------
    def onMinimize(self, e):
        """
        Hides the frame
        """
        if self.IsIconized():
            self.Hide()
    #----------------------------------------------------------------------
    def OnOpen(self, e):
        """
        Configures the 'Open' menu item
        """
        wildcard = "Video files (all types) (*.avi;*.mp4;*.mkv;...)|*.*"
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=self.currentFolder,
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            self.mpc.Quit()
            path = dlg.GetPath()
            self.currentFolder = os.path.dirname(path[0])
            trackPath = '"%s"' % path.replace("\\", "/")
            self.mpc.Start()
            self.mpc.Loadfile(trackPath)

    def OnQuit(self,e):
        """
        Configures the 'Quit' menu item
        """
        if self.mpc.process_alive:
            self.mpc.Quit()
        self.tbIcon.RemoveIcon()
        self.tbIcon.Destroy()

        wx.GetApp().ExitMainLoop()
        self.Close()

    def OnAbout(self,e):
        """
        Configures the 'About' menu item
        """
        aboutForm = wx.adv.AboutDialogInfo()
        
        aboutForm.SetIcon(wx.Icon((os.path.join(bitmapDir, 'info.png')), wx.BITMAP_TYPE_PNG))
        aboutForm.SetName("Fire Player")
        aboutForm.SetVersion("1.0")
        aboutForm.SetDescription("Fire Player is a free and open source video player")
        aboutForm.AddDeveloper("Red-Ficus")
        
        wx.adv.AboutBox(aboutForm)

    #----------------------------------------------------------------------
    def on_process_started(self, e):
        print("Process started!")
        
    def on_process_stopped(self, e):
        print("Process stopped!")

    def on_media_started(self, e):
        print("Video started!")
        t_len = self.mpc.GetTimeLength()
        self.playbackSlider.SetRange(0, t_len)
        self.playbackTimer.Start(100)
        self.mpc.Pause()
        
    def on_media_finished(self, e):
        print("Video finished!")
        self.mpc.Quit()
        
    def on_pause(self, e):
        if self.mpc.playing:
            if self.playbackTimer.IsRunning():
                print("Pausing...")
                self.mpc.Pause()
                self.playbackTimer.Stop()
            else:
                print("Unpausing...")
                self.mpc.Pause()
                self.playbackTimer.Start()
        else:
            self.OnOpen(True)

    def on_stop(self, e):
        if self.mpc.playing:
            print("Stopping...")
            self.mpc.Stop()
            self.playbackTimer.Stop()
            self.trackCounter.SetLabel("00:00")
            self.playbackSlider.SetValue(0)

    #----------------------------------------------------------------------
    def on_update_playback(self, e):
        """
        Updates the playback slider and track counter
        """
        try:
            offset = self.mpc.GetTimePos()
        except:
            return
        print(offset)
        mod_off = str(offset)[-1]
        if mod_off == '0':
            print("mod_off")
            offset = int(offset)
            self.playbackSlider.SetValue(offset)
            secsPlayed = time.strftime('%M:%S', time.gmtime(offset))
            self.trackCounter.SetLabel(secsPlayed)
            
    #----------------------------------------------------------------------
    def on_set_volume(self, e):
        """
        Sets the volume
        """
        self.currentVolume = self.volumeCtrl.GetValue()
        self.mpc.SetProperty('volume', self.currentVolume)
        
    #----------------------------------------------------------------------
if __name__ == "__main__":
    import os, sys
    
    paths = [r'C:\Program Files\MPlayer\mplayer.exe']
    mplayerPath = None
    for path in paths:
        if os.path.exists(path):
            mplayerPath = path

    if not mplayerPath:
        print("'MPlayer' was not found!")
        sys.exit()

    app = wx.App(redirect=False)
    frame = Frame(None, -1, "Fire Player", mplayerPath)
    app.MainLoop()