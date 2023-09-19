import PySimpleGUI as sg

class main:
    def __init__ (self):
        frameL = sg.Frame('', [
            [sg.Text('入力')],[sg.Multiline(font=('メイリオ',8),size=(60,4),key='-ELEMENT-')],[sg.Multiline(font=('メイリオ', 8),size=(60,94),key = '-INPUT-')],
            ], size=(460,800))
        button_convert = sg.Button('➡', font=('メイリオ', 8), key = '-CONVERT-')
        frameR = sg.Frame('', [
            [sg.Text('出力')],[sg.Multiline(font=('メイリオ', 8),size=(60,100), key = '-OUTPUT-', disabled=True)],
            ], size=(460,800))
        self.layout = [
            [frameL,button_convert, frameR]
        ]
        self.window = sg.Window('tsv to tabular', self.layout)
        
    def start(self):
        while True:
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break
            
            if event == '-CONVERT-':
                elems = values['-ELEMENT-']
                cnum = elems.splitlines()[0].count('\t') + 1
                print(cnum)
                elems = '\n'.join(elems.splitlines())
                elems = elems.replace('\n',' \\\\\n      ')
                elems = elems.replace('\t',' & ')
                elems = elems.replace('%','\\%')
                
                datas = values['-INPUT-']
                datas = '\n'.join(datas.splitlines())
                datas = datas.replace('\n',' \\\\\n      ')
                datas = datas.replace('\t',' & ')
                
                
                
                self.window['-OUTPUT-'].update('\\begin{table}[ht]\n'+
                                               '  \\caption{キャプション}\n'+
                                               '  \\label{tab:ラベル名}\n'+
                                               '  \\begin{adjustbox}{center}\n'+
                                               '    \\begin{tabular}{'+ 'c'*cnum +'}\n'+
                                               '      \\toprule\n      '+
                                               elems+' \\\\\n'+
                                               '      \\midrule\n      ' + 
                                               datas +' \\\\\n'+
                                               '      \\bottomrule\n'+
                                               '    \\end{tabular}\n'+
                                               '  \\end{adjustbox}\n'+
                                               '\\end{table}\n')

        self.window.close()
        
if __name__ == '__main__':
    ins = main()
    ins.start()