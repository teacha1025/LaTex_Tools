import numpy as np
import PySimpleGUI as sg
import matplotlib.pyplot as plt
import japanize_matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def make_dpi_aware():
  import ctypes
  import platform
  if int(platform.release()) >= 8:
    ctypes.windll.shcore.SetProcessDpiAwareness(True)
make_dpi_aware()

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def plot(data:[]):
    flag = False
    x_id = 0
    for d in data:
        if d.enable:
            if d.axis2:
                flag = True
                break                
            
    for i in range(len(data)):
        if data[i].x:
            x_id = i
            break
            
    ax1.cla()
    ax1.set_xlim(x_min, x_max)
    ax1.set_ylim(y1_min, y1_max)
    if flag:
        ax2 = ax1.twinx()
        ax2.set_ylim(y2_min, y2_max)
    fig_agg.draw()
    x = np.array(data[x_id].data,dtype=np.float64)
    
    for i in range(len(data)):
        if i is x_id:
            continue
        y= np.array(data[i].data,dtype=np.float64)
        if data[i].enable:
            if data[i].axis2:
                ax2.scatter(x,y,marker='.',s=80,color=data[i].color,label=data[i].label)
            else:
                ax1.scatter(x,y,marker='.',s=80,color=data[i].color,label=data[i].label)
    
    ax1.set_xlabel(x_label, fontsize=15, fontname ='MS Gothic')
    ax1.set_ylabel(y1_label, fontsize=15, fontname ='MS Gothic')
    ax1.grid(True)
    if flag:
        ax2.set_ylabel(y2_label, fontsize=15, fontname ='MS Gothic')
    
    if(flag):
        h1,l1 = ax1.get_legend_handles_labels()
        h2,l2 = ax2.get_legend_handles_labels()
        plt.legend(h1+h2,l1+l2,bbox_to_anchor=(1.15, 0.5), loc='center left', borderaxespad=0, fontsize=12, prop = {"family" : "MS Gothic"});
    else:
        plt.legend(bbox_to_anchor=(1.05, 0.5), loc='center left', borderaxespad=0, fontsize=12, prop = {"family" : "MS Gothic"})            

    
    
    plt.tight_layout()
    fig_agg.draw()


color_list = [ '#ff00ff', '#ff0000', '#0000ff', '#00ff00', '#000000', '#ff8000', '#800080', '#808080', '#00ffff']
class plot_data:
    def __init__(self, data_list, id):
        self.label = data_list[0]
        self.data = data_list[1]
        self.id = id
        self.x = False
        self.enable = True
        self.axis2 = False
        self.color = color_list[id%len(color_list)]
        
class data_wizard:
    def __init__(self, data_list:plot_data):
        self.data = data_list
        self.imp_name_list = ['表示する', 'x軸にする', '第2y軸に表示する']
        self.frame = [
            [[sg.Checkbox(self.imp_name_list[0], default=self.data.enable)]],
            [[sg.Checkbox(self.imp_name_list[1], default=self.data.x)]],
            [[sg.Checkbox(self.imp_name_list[2], default=self.data.axis2)]],
            [[sg.Text('ラベル名'), sg.InputText(self.data.label, size=(20,1), key='-LABEL-')]],
            [[sg.Text('色'), sg.Input(enable_events=True, key='-COLOR-', size=(10,1)), sg.ColorChooserButton('色選択', key = '-COLOR_BUTTON-')]]
        ]
        self.layout = [
            [self.frame],
            [sg.Button("OK"), sg.Button('キャンセル',key="Cancel")]
        ]
        self.window = sg.Window(f'データ編集ウィザード {self.data.label}', self.layout, finalize=True, element_justification='center', font='Monospace 18')
        
    def run(self):
        while True:
            event, values = self.window.read()
            if event in ('Exit', 'Quit', 'Cancel', None):
                break
            
            elif event == '-COLOR-':
                print(values['-COLOR-'])
                try:
                    self.window['-COLOR_BUTTON-'].update(button_color=(values['-COLOR-']))
                    self.data.color = values['-COLOR-']
                except:
                    continue
            elif event == "OK":
                self.data.label = values['-LABEL-']
                for name, check in zip(self.imp_name_list, values.values()):
                    if name is self.imp_name_list[0]:
                        self.data.enable = check
                    elif name is self.imp_name_list[1]:
                        self.data.x = check
                    elif name is self.imp_name_list[2]:
                        self.data.axis2 = check
                break;
            
        self.window.close()
        return self.data

class import_wizard:
    def __init__(self) -> None:
        self.layout = [
            [sg.MLine(font=('メイリオ', 8),size=(120,40),key = '-INPUT-')],
            [sg.Button('読込', key='Load'), sg.Button('キャンセル', key='Cancel')]
        ]
        self.window = sg.Window('データ入力', self.layout, finalize=True, element_justification='center', font='Monospace 18')
    
    def __perse_label(self, input:str):
        l = input.split('\n')
        lp = []
        lp.append(l[0].split('\t'))
        
        ret = []
        for i in range(len(lp[0])):
            ret.append(lp[0][i])
            
        return ret
    
    def __perse(self, input:str):
        l = input.split('\n')
        lp = []
        for i in range(len(l)):
            lp.append(l[i].split('\t'))
            
        length = len(lp[0])
        max = len(l)
        
        ret = []
        for i in range(length):
            now = 1
            col = []
            while now < max:
                col.append(lp[now][i])
                now += 1
            ret.append(col)
            
        return ret
    
    def run(self):
        ret = []
        while True:
            event, values = self.window.read()
            if event in ('Exit', 'Quit', 'Cancel', None):
                break
            
            elif event == "Load":
                tmp = self.__perse(values['-INPUT-'])
                labels = self.__perse_label(values['-INPUT-'])
                for d in range(len(tmp)):
                    ret.append(plot_data([labels[d],tmp[d]], d))
                
                ret[0].x = True
                break;
            
        self.window.close()
        return ret


data:plot_data = []
flag = True

x_min = 0.0
x_max = 100.0
y1_min = 0.0
y1_max = 100.0
y2_min = 0.0
y2_max = 100.0

x_label = 'X軸'
y1_label = 'Y軸1'
y2_label = 'Y軸2'


while flag:
    # レイアウト作成
    xaxis = sg.Frame('',[[sg.Text('X軸', font=('メイリオ', 12))],[sg.InputText(x_min, key='-X_MIN-', size =(5,1)), sg.Text('～'), sg.InputText(x_max, key='-X_MAX-', size =(5,1))],[sg.InputText(x_label, key='-X_LABEL-', size =(12,1))]])
    y1axis = sg.Frame('',[[sg.Text('Y軸1', font=('メイリオ', 12))],[sg.InputText(y1_min, key='-Y1_MIN-', size =(5,1)), sg.Text('～'), sg.InputText(y1_max, key='-Y1_MAX-', size =(5,1))],[sg.InputText(y1_label, key='-Y1_LABEL-', size =(12,1))]])
    y2axis = sg.Frame('',[[sg.Text('Y軸2', font=('メイリオ', 12))],[sg.InputText(y2_min, key='-Y2_MIN-', size =(5,1)), sg.Text('～'), sg.InputText(y2_max, key='-Y2_MAX-', size =(5,1))],[sg.InputText(y2_label, key='-Y2_LABEL-', size =(12,1))]])
    buttons = sg.Frame('',[[sg.Button('クリア', key='Clear')], [sg.Button('適用', key='Load')]])
    frameL = sg.Frame('',[[sg.Canvas(key='-CANVAS-')], 
                            [buttons,xaxis,y1axis,y2axis]],size=(960,760))
    
    col = [[sg.Text(d.label, font=('メイリオ', 10), size=(12,1), key=f'Label_{d.id}'), sg.Button("設定", font=('メイリオ', 8), key=f'Edit_{d.id}')] for d in data]
    frameR = sg.Frame('',[
            [sg.Button('読込', key='import'), sg.Button('保存', key='Save')],
            [sg.Col(col, scrollable=True, vertical_scroll_only=True, size=(240, 640))]
        ],size=(250,760))
    layout = [[frameL, frameR]]

    window = sg.Window('グラフ描画', layout, finalize=True, element_justification='center', font='Monospace 18')

    cm = 1/2.54 
    fig = plt.figure(figsize=(24*cm, 16*cm))
    
    fig_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)
    ax1 = fig.add_subplot(1,1,1)

    if len(data) != 0:
        fig.clear()
        ax1 = fig.add_subplot(1,1,1)
        plot(data)
    
    while True:
        event, values = window.read()

        if event in ('Exit', 'Quit', 'Cancel', None):
            flag = False
            break
        
        elif event == "Save":
            if(len(data) == 0):
                continue
            path = sg.popup_get_file('保存先を選択してください', default_path="../", save_as=True, multiple_files=False, file_types=(("PNG", "*.png"),("svg", "*.svg"),("JPG","*.jpg"),("TIFF", "*.tif"),("PDF", "*.pdf"),))
            if path is None:
                continue
            fig.savefig(fname=path, bbox_inches="tight")
        
        elif event == "import":
            wizard = import_wizard()
            data = wizard.run()
            flag = True
            if len(data) != 0:
                break
        
        elif 'Edit_' in event:
            id = int(event.split('_')[1])
            wizard = data_wizard(data[id])
            data[id] = wizard.run()
            
            if(len(data) == 0):
                continue
            x_min =  float(values['-X_MIN-'])
            x_max =  float(values['-X_MAX-'])
            y1_min = float(values['-Y1_MIN-'])
            y1_max = float(values['-Y1_MAX-'])
            y2_min = float(values['-Y2_MIN-'])
            y2_max = float(values['-Y2_MAX-'])
            
            x_label = values['-X_LABEL-']
            y1_label = values['-Y1_LABEL-']
            y2_label = values['-Y2_LABEL-']
            
            window[f'Label_{id}'].update(data[id].label)
            
            fig.clear()
            ax1 = fig.add_subplot(1,1,1)
            plot(data)
        
        elif event == "Load":
            if(len(data) == 0):
                continue
            x_min =  float(values['-X_MIN-'])
            x_max =  float(values['-X_MAX-'])
            y1_min = float(values['-Y1_MIN-'])
            y1_max = float(values['-Y1_MAX-'])
            y2_min = float(values['-Y2_MIN-'])
            y2_max = float(values['-Y2_MAX-'])
            
            x_label = values['-X_LABEL-']
            y1_label = values['-Y1_LABEL-']
            y2_label = values['-Y2_LABEL-']
            
            fig.clear()
            ax1 = fig.add_subplot(1,1,1)
            plot(data)

        elif event == "Clear":
            fig.clear()
            ax1=fig.add_subplot(1,1,1)
            fig_agg.draw()

    window.close()