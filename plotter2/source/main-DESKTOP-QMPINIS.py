import re
import numpy as np
import PySimpleGUI as sg
import matplotlib.pyplot as plt
import japanize_matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.interpolate import interp1d
from scipy.interpolate import make_interp_spline
import scipy

y_axis_num = 3

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
        lp.append(re.split('[,\t]',l[0]))
        
        ret = []
        for i in range(len(lp[0])):
            ret.append(lp[0][i])
            
        return ret
    
    def __perse(self, input:str):
        l = input.split('\n')
        lp = []
        for i in range(len(l)):
            lp.append(re.split('[,\t]',l[i]))
            
        length = len(lp[0])
        max = len(l)
        
        ret = []
        for i in range(length):
            now = 1
            col = []
            while now < max:
                if len(lp[now]) != length:
                    while len(lp[now]) != length:
                        lp[now].append('')
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

color_list = [ '#ff00ff', '#ff0000', '#0000ff', '#00ff00', '#000000', '#ff8000', '#800080', '#808080', '#00ffff']
color_name = ['ピンク', '赤', '青', '緑', '黒', 'オレンジ', '紫', '灰', '水色']

def log_func(x,a,b):
    return a + b * np.log(x)

def liner_func(x,a,b):
    return a*x+b

class curve:
    def __init__(self):
        self.enable = True
        self.smooth = False
        self.linestyle = "-"
        self.curve_type = 0
        self.n = 2
        
    def _power(self, x, y):#累乗
        a, b = np.polyfit(np.log(x), y, 1)
        return x, np.exp(a) * x ** b
    
    def _exp(self, x, y):#指数
        lx = np.log(x)
        ly = np.log(y)
        
        c = np.polyfit(lx, ly, 1)
        return x, np.exp(c[1])*np.exp(c[0]*x)
    
    def _log(self, x, y):#対数
        a,b = np.polyfit(x,y,1)
        return x, np.exp(a*x+b)
    
    def _liner(self, x, y):#線形
        a, b = np.polyfit(x, y, 1)
        return x, a*x+b
    
    def _poly(self, x, y, n):#n次多項式
        a = np.polyfit(x, y, n)
        return x, np.polyval(a, x)
    
    def _ave(self, x, y, n):#移動平均
        conv_y = np.convolve(y, np.ones(n)/n, mode='valid')
        conv_x = np.linspace(x.min(), x.max(), len(conv_y))
        return conv_x, conv_y
    
    def _spline(self, x, y):
        rx = np.linspace(np.min(x), np.max(x),np.size(x)*10)
        f = interp1d(x, y, kind='cubic')
        ry = f(rx)
        return rx, ry
    
    def get(self, x, y):
        if self.smooth == True:
            x, y = self._spline(x, y)
        if self.curve_type == 0:
            return x, y
        elif self.curve_type == 1:
            return self._liner(x, y)
        elif self.curve_type == 2:
            return self._poly(x, y, self.n)
        elif self.curve_type == 3:
            return self._log(x, y)
        elif self.curve_type == 4:
            return self._exp(x, y)
        elif self.curve_type == 5:
            return self._power(x,y)
        elif self.curve_type == 6:
            return self._ave(x,y,self.n)
        else:
            return x, y
        
    
class curve_wizard:
    def __init__(self, data: curve):
        self.data = data
        self.type = ['無し', '線形近似', '多項式近似', '対数近似', '指数近似', '累乗近似', '移動平均']
        self.line_list = ['無し', '―', '--', '―・', '・・']
        self.line_type = ['', '-', '--', '-.', ':']
        
        self.layout = [
            [sg.Text('近似曲線', font=('メイリオ', 12)), sg.Combo(self.type, default_value=self.type[data.curve_type], key='-TYPE-', size =(12,1))],
            [sg.Text('線種', font=('メイリオ', 12)), sg.Combo(self.line_list, default_value=self.line_list[self.line_type.index(data.linestyle)], key='-LINESTYLE-', size =(14,1))],
            [sg.Text('n', font = ('メイリオ', 12)), sg.InputText(self.data.n, key='-N-', size =(12,1))],
            [sg.Checkbox('有効', key='-ENABLE-', default=data.enable)],
            [sg.Checkbox('平滑化', key='-SMOOTH-', default=data.smooth)],
            [sg.Button('適用', key='Load'), sg.Button('キャンセル', key='Cancel')]
        ]
        self.window = sg.Window(f'線種設定', self.layout, finalize=True, element_justification='center', font='Monospace 18')

    def run(self):
        while True:
            event, values = self.window.read()
            if event in ('Exit', 'Quit', 'Cancel', None):
                break
            
            elif event == "Load":
                self.data.enable = values['-ENABLE-']
                linestyle = values['-LINESTYLE-']
                self.data.linestyle = self.line_type[self.line_list.index(linestyle)]
                self.data.smooth = values['-SMOOTH-']
                self.data.n = int(values['-N-'])
                self.data.curve_type = self.type.index(values['-TYPE-'])
                break;
            
        self.window.close()
        return self.data

class plot_data:
    def __init__(self, data_list, id):
        self.label = data_list[0]
        self.data = data_list[1]
        self.id = id
        self.x = False
        self.enable = True
        self.axis_id = 0
        self.color = color_list[id%len(color_list)]
        self.marker = ""
        self.curve = curve()

class plot_data_wizard:
    def __init__(self, data: plot_data):
        self.marker_list = ['無し', '・', '〇', '▽', '△', '◁', '▷', '×', '+', '◇', '|', '-']
        self.marker_type = ['', '.', 'o', 'v', '^', '<', '>', 'x', '+', 'd', '|', '-']
        self.axis_list = ['1', '2', '3']
        self.axis_type = [0,1,2]
        self.data = data
        self.layout = [
            [sg.Text('ラベル', font=('メイリオ', 12)), sg.InputText(self.data.label, key='-LABEL-', size =(12,1))],
            [sg.Text('軸', font=('メイリオ', 12)), sg.Combo(self.axis_list, default_value=self.axis_list[self.axis_type.index(self.data.axis_id)], key='-AXIS-', size =(14,1))],
            [sg.Text('色', font=('メイリオ', 12)), sg.Combo(color_name, default_value=color_name[color_list.index(self.data.color)], key='-COLOR-', size =(14,1))],
            [sg.Text('マーカー', font=('メイリオ', 12)), sg.Combo(self.marker_list, default_value=self.marker_list[self.marker_type.index(self.data.marker)], key='-MARKER-', size =(11,1))],
            [sg.Text('線種', font=('メイリオ', 12)), sg.Button(button_text='編集', font=('メイリオ', 8), key='-LINESTYLE-', size =(14,1))],
            [sg.Checkbox('有効', key='-ENABLE-', default=self.data.enable)],
            [sg.Button('適用', key='Load'), sg.Button('キャンセル', key='Cancel')]
        ]
        self.window = sg.Window(f'データ編集ウィザード {self.data.label}', self.layout, finalize=True, element_justification='center', font='Monospace 18')
    
    def run(self):
        while True:
            event, values = self.window.read()
            if event in ('Exit', 'Quit', 'Cancel', None):
                break
            
            elif event == "Load":
                self.data.label = values['-LABEL-']
                self.data.axis_id = self.axis_type[self.axis_list.index(values['-AXIS-'])]
                self.data.color = color_list[color_name.index(values['-COLOR-'])]
                marker = values['-MARKER-']
                self.data.enable = values['-ENABLE-']
                
                self.data.marker = self.marker_type[self.marker_list.index(marker)]
                break;
            elif event == "-LINESTYLE-":
                wizard = curve_wizard(self.data.curve)
                self.data.curve = wizard.run()
        self.window.close()
        return self.data

class axis_data:
    def __init__(self, text, x_flag, y_id) -> None:
        self.minimum = 0
        self.maximum = 100
        self.text = text
        if x_flag:
            self.label = text+'軸'
        else:
            self.label = text+'軸'+str(y_id+1)
        self.key=text+str(y_id)
        self.frame = sg.Frame('',[[sg.Text(self.label, font=('メイリオ', 12))],[sg.InputText(self.minimum, key='-'+self.key +'-_MIN-', size =(5,1)), sg.Text('～'), sg.InputText(self.maximum, key='-'+self.key + '-_MAX-', size =(5,1))],[sg.InputText(self.label, key='-'+self.key + '-_LABEL-', size =(12,1))],[sg.Checkbox('対数軸', key='-'+self.key + '-_LOG-')]])
        self.y_id = y_id
        self.x_flag = x_flag
        self.scale = 'linear'
        
    
    def set(self, values):
        self.minimum =  float(values['-'+self.key+'-_MIN-'])
        self.maximum =  float(values['-'+self.key+'-_MAX-'])
        if values['-'+self.key+'-_LOG-']:
            self.scale = 'log'
        else:
            self.scale = 'linear'
        self.label = values['-'+self.key+'-_LABEL-']
        
    def update(self, window):
        window['-'+self.key+'-_MIN-'].update(self.minimum)
        window['-'+self.key+'-_MAX-'].update(self.maximum)
        window['-'+self.key+'-_LOG-'].update(self.scale == 'log')

class plotter:
    def get_canvas(self, canvas, figure):
        figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
        return figure_canvas_agg
    
    def __init__(self, canvas):
        cm = 1/2.54 
        self.fig = plt.figure(figsize=(24*cm, 16*cm))
        self.fig_agg = self.get_canvas(canvas, self.fig)
        
        self.y_axis_flag = [True,False,False]
        self.y_axis = [None,None,None]
        self.y_axis[0] = self.fig.add_subplot(1,1,1)
        for i in range(y_axis_num):
            self.y_axis_flag[i] = False
        self.y_axis_flag[0] = True
        
    def clear(self):
        self.fig.clear()
        self.fig_agg.draw()
    
    def set_lim(self, axis: list[axis_data], x_id):
        self.clear()
        self.y_axis[0] = self.fig.add_subplot(1,1,1)
        self.y_axis[0].cla()
        self.y_axis[0].set_xlim(axis[0].minimum,axis[0].maximum)
        self.y_axis[0].set_ylim(axis[1].minimum,axis[1].maximum)
        self.y_axis[0].set_axisbelow(True)
        for i in range(y_axis_num-1):
            self.y_axis[i+1] = None
            if self.y_axis_flag[i+1]:
                self.y_axis[i+1] = self.y_axis[0].twinx()
                self.y_axis[i+1].set_xlim(axis[0].minimum,axis[0].maximum)
                self.y_axis[i+1].set_ylim(axis[i+2].minimum,axis[i+2].maximum)
                self.y_axis[i+1].set_axisbelow(True)
                
    def set_scale(self, axis: list[axis_data], x_id):
        self.y_axis[0].set_xscale(axis[0].scale)
        self.y_axis[0].set_yscale(axis[1].scale)
        for i in range(y_axis_num):
            #self.y_axis[i+1] = None
            if self.y_axis_flag[i]:
                self.y_axis[i].set_xscale(axis[0].scale)
                self.y_axis[i].set_yscale(axis[i+1].scale)
    
    def plot(self, data:list[plot_data], axis: list[axis_data]):
        if len(data) == 0:
            return
        self.y_axis_flag = []
        for i in range(y_axis_num):
            self.y_axis_flag.append(False)
        x_id=0
        for d in data:
            if d.enable:
                if d.x:
                    x_id = d.id
                else:
                    self.y_axis_flag[d.axis_id] = True
        
        
        self.set_lim(axis, x_id)
        
        self.fig_agg.draw()
        
        self.set_scale(axis, x_id)
        
        for i in range(len(data)):
            _x = []
            _y = []
            if i == x_id:
                continue
            for j in range(len(data[i].data)):
                try:
                    _y.append(float(data[i].data[j]))
                    _x.append(float(data[x_id].data[j]))
                except:
                    continue
            x = np.array(_x,dtype=np.float64)
            y = np.array(_y,dtype=np.float64)
            if data[i].enable:
                if(data[i].curve.enable == False):
                    self.y_axis[data[i].axis_id].scatter(x,y, color=data[i].color, label=data[i].label, marker=data[i].marker, zorder = 2)
                else:
                    self.y_axis[data[i].axis_id].scatter(x,y, color=data[i].color, marker=data[i].marker, zorder = 2)
                    _x, _y = data[i].curve.get(x, y)
                    self.y_axis[data[i].axis_id].plot(_x,_y, color=data[i].color, label=data[i].label, linestyle=data[i].curve.linestyle, zorder = 1)
        if self.y_axis_flag[1] == True and self.y_axis_flag[2] == True:
            self.y_axis[2].spines["right"].set_position(("axes", 1.2))
        
        h=[]
        l=[]
        
        for i in range(y_axis_num):
            h.append(None)
            l.append(None)
        
        self.y_axis[0].set_xlabel(axis[0].label)
        #self.y_axis[0].grid()
        for i in range(y_axis_num):
            if self.y_axis_flag[i]:
                self.y_axis[i].set_ylabel(axis[i+1].label)
                h[i], l[i] = self.y_axis[i].get_legend_handles_labels()
        h_ = h[0]
        l_ = l[0]
        for i in range(y_axis_num-1):
            if self.y_axis_flag[i+1]:
                h_ += h[i+1]
                l_ += l[i+1]
        plt.legend(h_, l_)
        
        plt.tight_layout()
        self.fig_agg.draw()

def boot(data, axis: list[axis_data]):
        layout = [[]]
        buttons = sg.Frame('',[[sg.Button('クリア', key='Clear')],[sg.Button('自動', key='AutoSet')], [sg.Button('適用', key='Load')]])
        col = [
            [sg.Text(d.label, font=('メイリオ', 10), size=(12,1), key=f'Label_{d.id}'), sg.Button("設定", font=('メイリオ', 8), key=f'Edit_{d.id}')] for d in data
            ]
        axis_impl: list[axis_data] = []
        for a in axis:
            axis_impl.append(axis_data(a.text, a.x_flag, a.y_id))
            axis_impl[-1].minimum = a.minimum
            axis_impl[-1].maximum = a.maximum
            axis_impl[-1].scale = a.scale
        axis_frame:list[sg.Frame] = []
        axis_frame.append(buttons)
        for a in axis_impl:
            axis_frame.append(a.frame)
        frameL = sg.Frame('',[[sg.Canvas(key='-CANVAS-')], 
                        axis_frame],size=(960,800))
        frameR = sg.Frame('',[
                [sg.Button('読込', key='import'), sg.Button('保存', key='Save')],
                [sg.Col(col, scrollable=True, vertical_scroll_only=True, size=(240, 640))]
            ],size=(250,800))
        layout = [[frameL, frameR]]
        return sg.Window('グラフ描画', layout, finalize=True, element_justification='center', font='Monospace 18')

def get_scale(minimum,maximum,is_log:bool):
    margin = 0.00
    NDIV = 10
    e = [1,2,5,10,20]
    R = maximum-minimum
    dig = 10 ** (np.floor(np.log10(R)))
    R = R / dig
    for i in range(5):
        if np.floor(R/e[i])<1:
            R=e[i+1]*dig/NDIV
            break
    
    if is_log:
        ret_min = 10 ** np.floor(np.log10(minimum))
        ret_max = 10 ** np.ceil(np.log10(maximum))
        return ret_min, ret_max
    
    ret_min = R * np.floor(minimum/R-margin)
    ret_max = R * np.ceil(maximum/R+margin)
    return ret_min, ret_max
    

class main_window:
    def __init__(self) -> None:
        self.start()
        self.data = []
    
    def start(self):
        self.xaxis = axis_data('X',True,0)
        self.y1axis = axis_data('Y',False,0)
        self.y2axis = axis_data('Y',False,1)
        self.y3axis = axis_data('Y',False,2)
    
    def auto_set(self, window):
        if len(self.data) == 0:
            return
        y_minimum = []
        y_maximum = []
        x_minimum = 0
        x_maximum = 0
        
        if self.xaxis.scale == 'log':
            x_minimum = float('inf')
        
        for i in range(y_axis_num):
            if i == 0 and self.y1axis.scale == 'log' or i == 1 and self.y2axis.scale == 'log' or i == 2 and self.y3axis.scale == 'log':
                y_minimum.append(float('inf'))
            else:
                y_minimum.append(0)
            y_maximum.append(0)
        
        for d in self.data:
            dt=[]
            for i in range(len(d.data)):
                try:
                    dt.append(float(d.data[i]))
                except:
                    continue
            if d.x:
                x_minimum = min(x_minimum,min(dt))
                x_maximum = max(x_maximum, max(dt))
            else:
                m=min(dt)
                M=max(dt)
                y_minimum[d.axis_id] = min(y_minimum[d.axis_id],m)
                y_maximum[d.axis_id] = max(y_maximum[d.axis_id],M)
        
        if self.xaxis.scale == 'log' and x_minimum <= 0:
            self.xaxis.scale = 'linear'
        self.xaxis.minimum, self.xaxis.maximum = get_scale(x_minimum, x_maximum, self.xaxis.scale == 'log')
        if y_minimum[0] != y_maximum[0]:
            if self.y1axis.scale == 'log' and y_minimum[0] <= 0:
                self.y1axis.scale = 'linear'
            self.y1axis.minimum, self.y1axis.maximum = get_scale(y_minimum[0], y_maximum[0], self.y1axis.scale == 'log')
        if y_minimum[1] != y_maximum[1]:
            if self.y2axis.scale == 'log' and y_minimum[1] <= 0:
                self.y2axis.scale = 'linear'
            self.y2axis.minimum, self.y2axis.maximum = get_scale(y_minimum[1], y_maximum[1], self.y2axis.scale == 'log')
        if y_minimum[2] != y_maximum[2]:
            if self.y3axis.scale == 'log' and y_minimum[2] <= 0:
                self.y3axis.scale = 'linear'
            self.y3axis.minimum, self.y3axis.maximum = get_scale(y_minimum[2], y_maximum[2], self.y3axis.scale == 'log')
            
        self.xaxis.update(window)
        self.y1axis.update(window)
        self.y2axis.update(window)
        self.y3axis.update(window)
        
    def update(self):
        while True:
            window = boot(self.data, [self.xaxis, self.y1axis, self.y2axis, self.y3axis])
            self.auto_set(window)
            self.plotter = plotter(window['-CANVAS-'].TKCanvas)
            self.plotter.plot(self.data, [self.xaxis, self.y1axis, self.y2axis, self.y3axis])
            while True:
                event, values = window.read()

                if event in ('Exit', 'Quit', 'Cancel', None):
                    window.close()
                    return
                elif event == "Clear":
                    self.plotter.clear()
                elif event == "import":
                    wizard = import_wizard()
                    self.data = wizard.run()
                    self.auto_set(window)
                    window.close()
                    break
                elif event == "Save":
                    1
                elif 'Edit_' in event:
                    id = int(event.split('_')[1])
                    wizard = plot_data_wizard(self.data[id])
                    self.data[id] = wizard.run()
                    self.xaxis.set(values)
                    self.y1axis.set(values)
                    self.y2axis.set(values)
                    self.y3axis.set(values)
                    self.plotter.plot(self.data, [self.xaxis, self.y1axis, self.y2axis, self.y3axis])
                elif event == "Load":
                    self.xaxis.set(values)
                    self.y1axis.set(values)
                    self.y2axis.set(values)
                    self.y3axis.set(values)
                    self.plotter.plot(self.data, [self.xaxis, self.y1axis, self.y2axis, self.y3axis])
                elif event == "AutoSet":
                    self.xaxis.set(values)
                    self.y1axis.set(values)
                    self.y2axis.set(values)
                    self.y3axis.set(values)
                    self.auto_set(window)
                    self.plotter.plot(self.data, [self.xaxis, self.y1axis, self.y2axis, self.y3axis])


def main():
    ins = main_window()
    ins.update()

if __name__ == '__main__':
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['mathtext.fontset'] = 'stix'
    plt.rcParams['font.size'] = 22 
    plt.rcParams['legend.framealpha'] = 0 
    plt.rcParams['xtick.direction'] = 'in' 
    plt.rcParams['ytick.direction'] = 'in' 
    
    main()