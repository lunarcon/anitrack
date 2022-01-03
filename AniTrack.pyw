import os,sys,requests,json
import clr,base64
from ctypes import POINTER, c_bool, sizeof, windll, pointer, c_int
from ctypes.wintypes import DWORD,ULONG
from ctypes import Structure

from enum import Enum

clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")
clr.AddReference("System")
clr.AddReference("System.Runtime.InteropServices")

from System.Drawing import *
from System.Windows.Forms import *
from System import *
from System.Windows.Forms import *
from System.Drawing.Drawing2D import *
from System.Drawing.Imaging import *

class WINDOWCOMPOSITIONATTRIB(Enum):
    WCA_UNDEFINED = 0,
    WCA_NCRENDERING_ENABLED = 1,
    WCA_NCRENDERING_POLICY = 2,
    WCA_TRANSITIONS_FORCEDISABLED = 3,
    WCA_ALLOW_NCPAINT = 4,
    WCA_CAPTION_BUTTON_BOUNDS = 5,
    WCA_NONCLIENT_RTL_LAYOUT = 6,
    WCA_FORCE_ICONIC_REPRESENTATION = 7,
    WCA_EXTENDED_FRAME_BOUNDS = 8,
    WCA_HAS_ICONIC_BITMAP = 9,
    WCA_THEME_ATTRIBUTES = 10,
    WCA_NCRENDERING_EXILED = 11,
    WCA_NCADORNMENTINFO = 12,
    WCA_EXCLUDED_FROM_LIVEPREVIEW = 13,
    WCA_VIDEO_OVERLAY_ACTIVE = 14,
    WCA_FORCE_ACTIVEWINDOW_APPEARANCE = 15,
    WCA_DISALLOW_PEEK = 16,
    WCA_CLOAK = 17,
    WCA_CLOAKED = 18,
    WCA_ACCENT_POLICY = 19,
    WCA_FREEZE_REPRESENTATION = 20,
    WCA_EVER_UNCLOAKED = 21,
    WCA_VISUAL_OWNER = 22,
    WCA_LAST = 23

class ACCENT_POLICY(Structure):
    _fields_ = [
        ('AccentState',   DWORD),
        ('AccentFlags',   DWORD),
        ('GradientColor', DWORD),
        ('AnimationId',   DWORD),
    ]


class WINDOWCOMPOSITIONATTRIBDATA(Structure):
    _fields_ = [
        ('Attribute',  DWORD),
        ('Data',       POINTER(ACCENT_POLICY)),
        ('SizeOfData', ULONG),
    ]


MY_PATH=__file__.replace(os.path.basename(__file__),'')
ANIME=os.path.join(MY_PATH,'data\\anime.json')

def open_url_in_browser(url):
    os.startfile(url)

def load_anime_from_json(path=ANIME):
    if os.path.exists(path):
        with open(path,'r') as f:
            anime_info = json.load(f)
        return anime_info
    else:
        return False

def download_file(url,name='temp.tmp'):
    r = requests.get(url, allow_redirects=True)
    open(name,'wb').write(r.content)

def onedrive_downurl(onedrive_link): #Ha, something i forgot to implement!
    data_bytes64 = base64.b64encode(bytes(onedrive_link, 'utf-8'))
    data_bytes64_String = data_bytes64.decode('utf-8').replace('/','_').replace('+','-').rstrip("=")
    resultUrl = f"https://api.onedrive.com/v1.0/shares/u!{data_bytes64_String}/root/content"
    return resultUrl

def get_anime_info(anime_title):
    try:
        anime_title = anime_title.replace(' ','+')
        url = f"https://api.jikan.moe/v3/search/anime?q={anime_title}"
        r = requests.get(url)
        anime_info = json.loads(r.text)
        return anime_info
    except:
        return None

def get_filename_from_url(url):
    return url.split('/')[-1].split('?')[0]

def get_anime_image(anime_info,title=None):
    if title:
        for i in anime_info['results']:
            if i['title'] == title:
                anime_image= i['image_url']
                break
    else:
        anime_image = anime_info['results'][0]['image_url']
    download_file(anime_image, os.path.join(MY_PATH,'data\\images',get_filename_from_url(anime_image)))
    return os.path.join(MY_PATH,'data\\images',get_filename_from_url(anime_image))

def clear_cache():
    if os.path.exists(os.path.join(MY_PATH,'data\\cache')):
        for f in os.listdir(os.path.join(MY_PATH,'data\\cache')):
            try:
                os.remove(os.path.join(MY_PATH,'data\\cache',f))
            except:
                pass

def get_url_from_json(title):
    anime_info = load_anime_from_json()
    for anime in anime_info:
        if anime['title'] == title:
            return anime['anime_url']

def spl_anime_img(item):
    image_path=item['image_url']
    download_file(image_path,os.path.join(MY_PATH,'data\\cache',get_filename_from_url(image_path)))
    return os.path.join(MY_PATH,'data\\cache',get_filename_from_url(image_path))

def get_anime_description(anime_info,title=None):
    if title:
        for i in anime_info['results']:
            if i['title'] == title:
                anime_description= i['synopsis']
                break
    else:
        anime_description = anime_info['results'][0]['synopsis']
    return anime_description

def get_anime_url(anime_info,title=None):
    if title:
        for i in anime_info['results']:
            if i['title'] == title:
                anime_url= i['url']
                break
    anime_url = anime_info['results'][0]['url']
    return anime_url

def is_anime_in_json(title):
    anime_info = load_anime_from_json()
    if anime_info:
        for anime in anime_info:
            if anime['title'] == title:
                return True
    return False

def add_anime_to_json(title):
    anime_info = load_anime_from_json()
    af=get_anime_info(title)
    image_path = get_anime_image(af,title)
    desc=get_anime_description(af,title)
    url=get_anime_url(af,title)
    if anime_info:
        anime_info.append({
            "title":title,
            "anime_episodes":10,
            "anime_image":image_path,
            "anime_description":desc,
            "anime_url":url
        })
    else:
        anime_info = [{
            "title":title,
            "anime_episodes":10,
            "anime_image":image_path,
            "anime_description":desc,
            "anime_url":url
        }]
    with open(ANIME,'w') as f:
        json.dump(anime_info,f)

def remove_anime_from_json(title):
    anime_info = load_anime_from_json()
    for anime in anime_info:
        if anime['title'] == title:
            anime_info.remove(anime)
    with open(ANIME,'w') as f:
        json.dump(anime_info,f)

CUR_PANE='Main_Panel'
class Window(Form):
    def __init__(self):
        self.SetWindowCompositionAttribute = windll.user32.SetWindowCompositionAttribute
        self.SetWindowCompositionAttribute.restype = c_bool
        self.SetWindowCompositionAttribute.argtypes = [
            c_int, POINTER(WINDOWCOMPOSITIONATTRIBDATA)]
        self.accentPolicy = ACCENT_POLICY()
        self.winCompAttrData = WINDOWCOMPOSITIONATTRIBDATA()
        self.winCompAttrData.Attribute = WINDOWCOMPOSITIONATTRIB.WCA_ACCENT_POLICY[0]
        self.winCompAttrData.SizeOfData = sizeof(self.accentPolicy)
        self.winCompAttrData.Data = pointer(self.accentPolicy)

        self.Text = ""
        self.Width = 1100
        self.Height = 768
        self.CenterToScreen()
        self.BackColor = Color.FromArgb(255,0,0,0)
        self.ForeColor = Color.FromArgb(255,255,255,255)
        self.Font = Font("Segoe UI",20)
        self.MinimumSize = Size(1024,768)

        # TITLE
        Title_Panel=self.create_panel(100,1024,0,0)
        Title_Panel.BackColor = Color.FromArgb(255,0,0,0)
        Title_Panel.ForeColor = Color.FromArgb(255,255,255,255)
        Title_Panel.Dock = DockStyle.Top
        YourAnime = self.create_label(100,130,0,0,"Home")
        YourAnime.Name='YourAnime'
        YourAnime.Font = Font("Hack",20)
        YourAnime.ForeColor = Color.FromArgb(255,255,255,255)
        YourAnime.Dock = DockStyle.Left
        YourAnime.TextAlign = ContentAlignment.MiddleCenter
        YourAnime.Click += self.show_main_panel

        spacer=self.create_label(100,1,0,0,"|")
        spacer.Font = Font("Hack",20)
        spacer.ForeColor = Color.FromArgb(255,255,255,255)
        spacer.Dock = DockStyle.Left
        spacer.TextAlign = ContentAlignment.MiddleCenter
        AnimeList = self.create_label(100,220,0,0,"Add Anime")
        AnimeList.Click += self.show_search_panel

        AnimeList.Name='AnimeList'
        AnimeList.Font = Font("Hack",20)
        AnimeList.ForeColor = Color.FromArgb(255,128,128,128)
        AnimeList.Dock = DockStyle.Left
        AnimeList.TextAlign = ContentAlignment.MiddleCenter

        Title_Panel.Controls.Add(AnimeList)
        Title_Panel.Controls.Add(spacer)
        Title_Panel.Controls.Add(YourAnime)
        Title_Panel.Click+=self.losefocus
        
        # SEARCH IN TITLE
        Search_Panel=self.create_panel(100,250,0,0)
        Search_Panel.BackColor = Color.FromArgb(255,0,0,0)
        Search_Panel.ForeColor = Color.FromArgb(255,255,255,255)
        Search_Panel.Dock = DockStyle.Right

        SearchBox=self.create_textbox(20,220,30,0,'Search')
        SearchBox.KeyDown+=self.search_anime
        SearchBox.Click+=self.tbclicked
        SearchBox.LostFocus+=self.tblostfocus
        SearchBox.Name = "SearchBox"
        Search_Panel.Controls.Add(SearchBox)
        Title_Panel.Controls.Add(Search_Panel)
        SettingsBtn=self.create_button(50,50,0,0,"")
        SettingsBtn.Font=Font('Segoe Fluent Icons',15)
        SettingsBtn.Margin=Padding(20,20,20,20)
        SettingsBtn.Padding=Padding(0,7,0,0)
        SettingsBtn.Dock=DockStyle.Right
        SettingsBtn.BackColor = Color.FromArgb(0,0,0,0)
        SettingsBtn.ForeColor = Color.FromArgb(255,200,200,200)
        SettingsBtn.FlatStyle = FlatStyle.Flat
        SettingsBtn.FlatAppearance.BorderSize = 0
        SettingsBtn.FlatAppearance.MouseOverBackColor = Color.FromArgb(100,0,0,0)
        SettingsBtn.FlatAppearance.MouseDownBackColor = Color.FromArgb(200,0,0,0)
        SettingsBtn.Click+=self.settings_btn_click
        Title_Panel.Controls.Add(SettingsBtn)
        self.Controls.Add(Title_Panel)
        

        # MAIN PANEL
        Main_Panel = self.create_FlowLayoutPanel(768,1024,200,0)
        Main_Panel.BackColor = Color.FromArgb(255,10,10,10)
        Main_Panel.ForeColor = Color.FromArgb(255,255,255,255)
        Main_Panel.Dock = DockStyle.Fill
        Main_Panel.AutoScroll = True
        Main_Panel.FlowDirection = FlowDirection.LeftToRight
        Main_Panel.Name = "Main_Panel"
        Main_Panel.Click+=self.losefocus
        self.Controls.Add(Main_Panel)
        Title_Panel.SendToBack()
        self.setAcrylicEffect()
        self.Populate(Main_Panel)

        # SETTINGS PANEL
        Settings_Panel = self.create_panel(1024,768,0,0)
        Settings_Panel.BackColor = Color.FromArgb(255,10,10,10)
        Settings_Panel.ForeColor = Color.FromArgb(255,255,255,255)
        Settings_Panel.Dock = DockStyle.Fill
        Settings_Panel.AutoScroll = True
        Settings_Panel.FlowDirection = FlowDirection.LeftToRight
        Settings_Panel.Visible = False
        Settings_Panel.Name = "Settings_Panel"
        Settings_Title=self.create_label(1024,50,0,0,"Settings")
        Settings_Title.Font = Font("Segoe UI",30,FontStyle.Bold)
        Settings_Title.ForeColor = Color.FromArgb(255,255,255,255)
        Settings_Title.Dock = DockStyle.Top
        Settings_Title.Padding = Padding(20,20,20,20)
        Settings_Panel.Controls.Add(Settings_Title)
        Settings_Panel.Click+=self.losefocus
        self.Controls.Add(Settings_Panel)

        # SEARCH_
        Search_=self.create_FlowLayoutPanel(1024,50,0,0)
        Search_.FlowDirection = FlowDirection.LeftToRight
        Search_.BackColor = Color.FromArgb(255,10,10,10)
        Search_.ForeColor = Color.FromArgb(255,255,255,255)
        Search_.Dock = DockStyle.Fill
        Search_.AutoScroll = True
        Search_.Name = "Search_"
        Search_.Visible = False
        Search_.Click+=self.losefocus
        Search_.Click+=self.losefocus
        self.Controls.Add(Search_)

        self.Show()
        self.ShowIcon=False

    def losefocus(self,sender,e):
        sender.Focus()

    def show_main_panel(self,sender,event):
        global CUR_PANE
        sender.ForeColor = Color.FromArgb(255,255,255,255)
        AnimeList=self.Controls.Find("AnimeList",True)[0]
        AnimeList.ForeColor = Color.FromArgb(255,128,128,128)
        Main_Panel= self.Controls.Find('Main_Panel',True)[0]
        Search_= self.Controls.Find('Search_',True)[0]
        Settings_Panel= self.Controls.Find('Settings_Panel',True)[0]
        Settings_Panel.Visible=False
        Main_Panel.Visible=True
        Main_Panel.BringToFront()
        Search_.Visible=False
        for i in Search_.Controls:
            Search_.Controls.Remove(i)
            i.Dispose()
        CUR_PANE='Main_Panel'
        sender.Parent.Focus()
        self.Populate(Main_Panel)

    def show_search_panel(self,sender,event):
        global CUR_PANE
        sender.ForeColor = Color.FromArgb(255,255,255,255)
        YourAnime= self.Controls.Find('YourAnime',True)[0]
        YourAnime.ForeColor = Color.FromArgb(255,128,128,128)
        Main_Panel= self.Controls.Find('Main_Panel',True)[0]
        Search_= self.Controls.Find('Search_',True)[0]
        Settings_Panel= self.Controls.Find('Settings_Panel',True)[0]
        Settings_Panel.Visible=False
        Main_Panel.Visible=False
        Search_.BringToFront()
        for i in Search_.Controls:
            Search_.Controls.Remove(i)
            i.Dispose()
        Search_.Controls.Clear()
        Search_.Visible=True
        search_label=self.create_label(1024,50,0,0,"Type to search")
        search_label.Font = Font("Segoe UI",30,FontStyle.Bold)
        search_label.ForeColor = Color.FromArgb(255,255,255,255)
        search_label.Dock = DockStyle.Fill
        search_label.TextAlign = ContentAlignment.MiddleCenter
        s_label_panel=self.create_panel(200,400,0,0)
        s_label_panel.BackColor = Color.FromArgb(255,30,30,30)
        s_label_panel.Controls.Add(search_label)
        s_label_panel.Margin = Padding(20,20,20,20)
        self.round_corners(s_label_panel,25)
        Search_.Controls.Add(s_label_panel)
        Search_.Refresh()
        SearchBox=self.Controls.Find('SearchBox',True)[0]
        SearchBox.Focus()
        SearchBox.Text = ''
        CUR_PANE='Search_'
  
    def settings_btn_click(self,sender,event):
        global CUR_PANE
        Settings_Panel= self.Controls.Find('Settings_Panel',True)[0]
        Main_Panel= self.Controls.Find('Main_Panel',True)[0]
        if Settings_Panel.Visible==False:
            CUR_PANE='Settings_Panel'
            Settings_Panel.Visible=True
            Main_Panel.SendToBack()
            Main_Panel.Visible=False
            Settings_Panel.BringToFront()
        else:
            CUR_PANE='Main_Panel'
            Settings_Panel.Visible=False
            Main_Panel.Visible=True
            Main_Panel.BringToFront()
            Settings_Panel.SendToBack()
 
    def search_anime(self,sender,event):
        global CUR_PANE
        if CUR_PANE=='Main_Panel':
            Main_Panel = self.Controls[0]
            Main_Panel.Controls.Clear()
            self.Populate(Main_Panel)
            if sender.Text != "Search":
                for c in Main_Panel.Controls:
                    if sender.Text.lower() in c.Tag.lower():
                        c.Show()
                    else:
                        c.Hide()
        elif CUR_PANE=='Search_':
            # only when enter is pressed
            if sender.Text != '':
                if event.KeyCode == Keys.Enter:
                    AnimeList=self.Controls.Find("Search_",True)[0]
                    for i in AnimeList.Controls:
                        AnimeList.Controls.Remove(i)
                        i.Dispose()
                    AnimeList.Controls.Clear()
                    clear_cache()
                    print('searching for '+sender.Text)
                    g=get_anime_info(sender.Text)['results']
                    if len(g)>20:
                        g=g[:20]
                    if g==None:
                        return
                    
                    for i in g:
                        print('found'+i['title'])
                        try:
                            if not is_anime_in_json(i['title']):
                                AnimeList.Controls.Add(self.create_AnimeDisplay(i['title'],spl_anime_img(i)))
                        except:
                            print('error')
                            
    def tbclicked(self,sender,event):
        sender.Text=""

    def tblostfocus(self,sender,event):
        if sender.Text=="":
            sender.Text="Search"
    
    def create_textbox(self,h,w,y,x,text):  
        textbox = TextBox()
        textbox.Location = Point(x,y)
        textbox.Size = Size(w,h)
        textbox.Text = text
        textbox.Font=Font("Segoe UI",15)
        textbox.BackColor = Color.FromArgb(255,10,10,10)
        textbox.ForeColor = Color.FromArgb(255,100,100,100)
        textbox.FlatStyle = FlatStyle.Flat
        textbox.Resizable = True
        return textbox

    def create_button(self,h,w,y,x,text):
        button = Button()
        button.Location = Point(x,y)
        button.Size = Size(w,h)
        button.Text = text
        return button

    def create_panel(self,h,w,y,x):
        panel = Panel()
        panel.Location = Point(x,y)
        panel.Size = Size(w,h)
        return panel

    def create_label(self,h,w,y,x,text):
        label = Label()
        label.Location = Point(x,y)
        label.Size = Size(w,h)
        label.Text = text
        return label

    def create_FlowLayoutPanel(self,h,w,y,x):
        Flowpanel = FlowLayoutPanel()
        Flowpanel.Location = Point(x,y)
        Flowpanel.Size = Size(w,h)
        Flowpanel.BackColor = Color.FromArgb(255,10,10,10)
        Flowpanel.Padding = Padding(10,10,10,10)
        return Flowpanel

    def create_picturebox(self,h,w,y,x,image):
        picturebox = PictureBox()
        picturebox.Location = Point(x,y)
        picturebox.Size = Size(w,h)
        picturebox.Image = Image.FromFile(image)
        return picturebox
    
    def create_AnimeDisplay(self,title,imagepath):
        AnimeDisplay = self.create_panel(330,240,0,0)
        AnimeDisplay.ForeColor = Color.FromArgb(255,255,255,255)
        AnimeDisplay.Margin = Padding(10,10,10,10)
        AnimeDisplay.Name=title
        AnimeDisplay.Tag=title
        AnimeDisplay.MouseLeave += self.AniDis_MouseLeave
        btn=self.create_button(420,250,0,0,'')
        btn.FlatStyle = FlatStyle.Flat
        btn.FlatAppearance.BorderSize = 0
        btn.BorderColor = Color.FromArgb(0,0,0,0)
        btn.ForeColor = Color.FromArgb(255,255,255,255)
        btn.BackColor = Color.FromArgb(70,20,20,20)
        btn.Tag = title+','+imagepath
        btn.Font = Font("Segoe UI",20,FontStyle.Bold)
        btn.Dock = DockStyle.Fill
        btn.BackgroundImage = Image.FromFile(imagepath)
        btn.BackgroundImageLayout = ImageLayout.Stretch
        btn.MouseEnter+=self.AnimeDisplay_Hover
        btn.MouseLeave+=self.AnimeDisplay_MouseLeave
        btn.MouseDown+=self.AnimeDisplay_MouseDown
        btn.MouseUp+=self.AnimeDisplay_MouseUp
        btn.Click+=self.AnimeDisplay_Click
        AnimeDisplay.Controls.Add(btn)

        if CUR_PANE=='Main_Panel':
            arbtn=self.create_button(50,50,0,0,'-')
            arbtn.BackColor = Color.FromArgb(200,80,10,10)
        else:
            arbtn=self.create_button(50,50,0,0,'+')
            arbtn.BackColor = Color.FromArgb(200,10,10,80)
        arbtn.Click += self.add_remove_anime
        arbtn.Name='mod'
        arbtn.FlatStyle = FlatStyle.Flat
        arbtn.FlatAppearance.BorderSize = 0
        arbtn.FlatAppearance.MouseOverBackColor = Color.FromArgb(255,40,40,40)
        arbtn.FlatAppearance.MouseDownBackColor = Color.FromArgb(255,10,10,10)
        arbtn.BorderColor = Color.FromArgb(0,0,0,0)
        arbtn.ForeColor = Color.FromArgb(255,255,255,255)
        arbtn.Tag = title
        arbtn.Font = Font("Segoe UI",30,FontStyle.Bold)
        AnimeDisplay.Controls.Add(arbtn)
        btn.SendToBack()
        arbtn.BringToFront()

        self.round_corners(AnimeDisplay,25)
        return AnimeDisplay

    def add_remove_anime(self,sender,e):
        if sender.Text=="+":
            sender.Text="-"
            add_anime_to_json(sender.Tag)
            sender.Parent.Controls[1].Text='Added to your list'
            self.Controls.Find('Search_',True)[0].Controls.Remove(sender.Parent)
            sender.Parent.Dispose()
            print("Added anime to list")
        else:
            sender.Text="+"
            remove_anime_from_json(sender.Tag)
            sender.BackColor=Color.FromArgb(255,10,10,80)
            self.Controls.Find('Main_Panel',True)[0].Controls.Remove(sender.Parent)
            sender.Parent.Dispose()
            print("Removed anime from list")

    def Populate(self,control):
        control.Controls.Clear()
        with open(ANIME,'r') as f:
            anime_info = json.load(f)
        for anime in anime_info:
            dis=self.create_AnimeDisplay(anime['title'],anime['anime_image'])
            control.Controls.Add(dis)
            #print('added anime {}'.format(anime['title']))
        control.Refresh()

    def AniDis_MouseLeave(self,sender,e):
        btn=sender.Parent.Controls.Find("mod",True)[0]

    def AnimeDisplay_Hover(self,sender,event):
        btn=sender.Parent.Controls.Find("mod",True)[0]
        sender.ForeColor = Color.FromArgb(255,255,255,255)
        img=sender.Tag.split(',')[1]
        btn.Visible=True
        #make img darker
        sender.BackgroundImage=self.DarkenImage(img,0.5)
   
        sender.Text=str(sender.Tag).split(',')[0]

    def DarkenImage(self,img,value):
        myImg=Image.FromFile(img)
        newImg = Image.FromHbitmap(myImg.GetHbitmap())
        g = Graphics.FromImage(newImg)
        cm = ColorMatrix()
        cm.Matrix00 = value
        cm.Matrix11 = value
        cm.Matrix22 = value
        cm.Matrix33 = 1
        cm.Matrix44 = 1
        cm.Matrix55 = 0
        cm.Matrix66 = 1
        ia = ImageAttributes()
        ia.SetColorMatrix(cm)
        g.DrawImage(myImg,
                    Rectangle(0,0,myImg.Width,myImg.Height),
                    0,0,myImg.Width,myImg.Height,
                    GraphicsUnit.Pixel,ia)
        g.Dispose()
        return newImg
    
    def AnimeDisplay_MouseLeave(self,sender,event):
        sender.ForeColor = Color.FromArgb(255,255,255,255)
        sender.BackgroundImage = Image.FromFile(str(sender.Tag).split(',')[1])
        sender.Text=''

    def AnimeDisplay_MouseDown(self,sender,event):
        sender.Font=Font("Segoe UI",15,FontStyle.Bold)
        sender.FlatAppearance.BorderSize = 5
        sender.FlatAppearance.BorderColor = Color.FromArgb(150,100,100,100)

    def AnimeDisplay_MouseUp(self,sender,event):
        sender.Font=Font("Segoe UI",20,FontStyle.Bold)
        sender.FlatAppearance.BorderSize = 0
        sender.FlatAppearance.BorderColor = Color.FromArgb(0,0,0,0)

    def AnimeDisplay_Click(self,sender,event):
        open_url_in_browser(get_url_from_json(str(sender.Tag).split(',')[0]))
        print(f'clicked {sender.Tag}')

    def bring_to_front(self,control):
        control.BringToFront()
        self.Refresh()

    def round_corners(self,oj,rad=5):
        p = GraphicsPath()
        p.StartFigure()
        p.AddArc(0, 0, rad, rad, 180, 90)
        p.AddLine(rad, 0, oj.Width - rad, 0)
        p.AddArc(oj.Width - rad, 0, rad, rad, 270, 90)
        p.AddLine(oj.Width, rad, oj.Width, oj.Height - rad)
        p.AddArc(oj.Width - rad, oj.Height - rad, rad, rad, 0, 90)
        p.AddLine(oj.Width - rad, oj.Height, rad, oj.Height)
        p.AddArc(0, oj.Height - rad, rad, rad, 90, 90)
        p.AddLine(0, oj.Height - rad, 0, rad)
        
        p.CloseFigure()
        oj.Region = Region(p)

    def draw_shadow(self,control,colorstart,colorend): #Aha!, another thing i forgot to implement, but this time entirely
        pass
                
    def get_hwnd(self):
        return self.Handle.ToInt64()
    
    def setAcrylicEffect(self, gradientColor: str = 'C0'+'222222', isEnableShadow: bool = True,animationId: int = 0):
        self.accentPolicy.AccentState = 4
        hWnd=self.get_hwnd()
        gradientColor = DWORD(int(gradientColor, base=16))
        animationId = DWORD(animationId)
        accentFlags = DWORD(0x20 | 0x40 | 0x80 | 0x100) if isEnableShadow else DWORD(0)

        self.accentPolicy.AccentState = 4
        self.accentPolicy.GradientColor = gradientColor
        self.accentPolicy.AccentFlags = accentFlags
        self.accentPolicy.AnimationId = animationId
        self.SetWindowCompositionAttribute(hWnd, pointer(self.winCompAttrData))
        self.Refresh()

def main():
    clear_cache()
    if not os.path.exists(os.path.join(MY_PATH,'data')):
        os.mkdir(os.path.join(MY_PATH,'data'))
        os.mkdir(os.path.join(MY_PATH,'data','cache'))
        os.mkdir(os.path.join(MY_PATH,'data','images'))
        with open(ANIME,'w') as j:
            json.write('[]')
    Application.EnableVisualStyles()
    Application.Run(Window())

if __name__ == "__main__":
    main()
