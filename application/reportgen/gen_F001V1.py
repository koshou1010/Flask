from pydoc import TextDoc
from warnings import filterwarnings
import plotly.graph_objects as go
from fpdf import FPDF
import os
from datetime import datetime
from numpy import irr
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

#####
# Use this function need the following extra packages
# plotly
# kaleido
#####

COLOR_BAR = ['#FF4040', '#0000CD', '#76EE00', '#FF8C00',  '#9932CC']


class PDF_F001V1(FPDF):

    # Page header
    def header(self):
        pass

    # Page footer
    def footer(self):
        pass

    def sColors(self, txtColor=[0, 0, 0], drawColor=[0, 0, 0], fillColor=[255, 255, 255]):
        self.set_text_color(txtColor[0], txtColor[1], txtColor[2])
        self.set_draw_color(drawColor[0], drawColor[1], drawColor[2])
        self.set_fill_color(fillColor[0], fillColor[1], fillColor[2])

    def dText(self, x, y, txt, family, size: int = 7):
        self.set_font(family, size=size)
        self.text(x, y, txt=txt)

    def dMultiText(self, x, y, w, h, txt, family, size: int = 7):
        self.set_font(family, size=size)
        self.set_xy(x, y)
        self.multi_cell(w, h, txt=txt)

    def dLine(self, x0, y0, x1, y1, lwidth: float = 0.1):
        self.set_line_width(lwidth)
        self.line(x0, y0, x1, y1)

    def dDashLine(self, x0, y0, x1, y1, lwidth: float = 0.1):
        self.set_line_width(lwidth)
        self.dashed_line(x0, y0, x1, y1)

    def dRect(self, x, y, w, h, lwidth: float = 0.1, style: str = "D"):
        self.set_line_width(lwidth)
        self.rect(x, y, w, h, style=style)

    def dCircle(self, x, y, r, lwidth: float = 0.1, style: str = "D"):
        self.set_line_width(lwidth)
        self.ellipse(x, y, r, r, style=style)

    def dImage(self, x, y, imagePath, w=0, h=0):
        # self.set_xy(x, y)
        self.image(imagePath, x=x,y=y,w=w, h=h)


class F001V1():
    def __init__(self) -> None:
        self.pageNo = 0             # 頁數
        self.pageWidth = 210        # 頁寬
        self.pageHeight = 297       # 頁高
        self.cellW = 2
        self.rowNo = 12
        self.rowWidth = 16  # (210-12)/12=16
        self.pageWidth_mx = 9       # 頁寬 margin left & right
        self.pageHeight_mt = 6      # 頁高 margin top & bottom

        # 檔案相關
        pypath = os.path.dirname(__file__)
        self.fontFamily = 'TaipeiSans'                              # 字型
        self.fontSungFamily = 'TW-Sung'
        self.fontPath = os.path.join(
            pypath, "doc", "TaipeiSansTCBeta-Regular.ttf")  # 字型檔案位置
        self.fontSungPath = os.path.join(
            pypath, "doc", "TW-Sung-98_1.ttf")  # 字型檔案位置
        self.logoPath = os.path.join(
            pypath, "doc", "SW-Logo.png")                   # logo 檔案位置
        self.maxHRDecPath = os.path.join(pypath, "doc", "hr_decrease.png")
        self.minHRPath = os.path.join(pypath, "doc", "hr_min.png")
        self.pvcPath = os.path.join(pypath, "doc", "Poincare_PVC.png")
        self.persistAFPath = os.path.join(
            pypath, "doc", "Poincare_Persist_AF.png")
        self.paroxysmalAFPath = os.path.join(
            pypath, "doc", "Poincare_Paroxysmal_AF.png")
        self.flagPath = os.path.join(pypath, "doc", "flag.png")

        # 色彩
        self.black = [0, 0, 0]
        self.white = [255, 255, 255]
        self.lightGrey = [230, 230, 230]
        self.grey = [190, 190, 190]
        self.darkGrey = [64, 64, 64]
        self.drak_blue = [0, 0, 205]
        self.orange = [255, 127, 36]
        pass

    def genReport(self, json, file_name, pngFloder):

        self.position_pie_path = os.path.join(pngFloder, 'position_pie.png')
        self.position_bar_path = os.path.join(pngFloder, 'position_bar.png')
        self.sleep_pie_path = os.path.join(pngFloder, 'sleep_pie.png')
        self.sleep_bar_path = os.path.join(pngFloder, 'sleep_bar.png')
        # sleepingQR = json['sleepingQualityReport']
        apnea_state = json['apneaState']
        self.__drawPie(['仰躺', '左側躺', '趴睡', '右側躺', '直立'], [i if i != 0 else None for i in json['sleepingPostureEvaluation']['abnPostureStatistic']['percentage']], self.position_pie_path)
        self.__drawPie(['REM', '淺眠', '深眠'], json['sleepingQualityEvaluation']['abnormalStateStatistic']['percentage'], self.sleep_pie_path)
        self.__draw_3D_bar(json['sleepingPostureEvaluation']['postureSeverity'], self.position_bar_path)
        self.__draw_3D_bar2(json['sleepingQualityEvaluation']['stateSeverity'], self.sleep_bar_path)
        file = self.generateReport(
            json['header'], json['userInfo'], json['sleepingState'], apnea_state, json['sleepingPostureEvaluation'], json['sleepingQualityEvaluation'], json['breathSignals'], file_name)
        return file

    def generateReport(self, header, userInfo, sleepingState, apnea_state, sleeping_posture_evaluation, sleeping_quality_evaluation, breath_signals, file_name) -> None:
        print('in generate Report')
        # A4 (w:210 mm and h:297 mm)
        filterwarnings("ignore")

        # 繪製PDF
        self.report = PDF_F001V1(format='A4')
        self.report.add_font(self.fontFamily, '', self.fontPath, uni=True)
        self.report.add_font(self.fontSungFamily, '',
                             self.fontSungPath, uni=True)
        self.header = header
        self.userInfo = userInfo
        self.__addSleepApneaReport(sleepingState, apnea_state)
        self.__addNote("notes")
        self.__add_position_assessment(sleepingState, sleeping_posture_evaluation, sleeping_quality_evaluation, apnea_state)
        self.__add_breath(apnea_state, breath_signals)

        # 匯出PDF
        pypath = os.path.join(os.path.dirname(__file__),
                              '..','..', 'user_pdf', 'F001V1')
        if not os.path.exists(pypath):
            os.makedirs(pypath)

        file = os.path.join(pypath, file_name)
        self.report.output(file, 'F')
        return file

    def __drawPie(self, labels, values, png_path):
        pie_colors = COLOR_BAR
        # pull is given as a fraction of the pie radius
        # let Deep be the pulled part and set sort as False to maintain the order.
        fig = go.Figure(data=[go.Pie(direction='clockwise', labels=labels, values=values, textinfo='label+percent',
                        insidetextorientation='horizontal', marker_colors=pie_colors, sort=False, pull=[0, 0.2, 0, 0])])
        fig.write_image(png_path, engine="kaleido",
                        format="png", width=600, height=600)

    def __draw_3D_bar(self, values, png_path):
        __colors = COLOR_BAR[:4]
        __font = fm.FontProperties(fname=self.fontPath, size=8)
        fig = plt.figure(figsize=(6, 6),
                         facecolor='blue',
                         edgecolor='black')
        ax = plt.subplot(projection='3d')
        x = [2, 4, 6, 8]
        y1 = 10
        y2 = 12
        y3 = 14
        y4 = 16
        z = 0
        # 仰躺
        ax.bar3d(x, y1, z, dx=1, dy=1, dz=values[0], color=__colors[2])
        label4 = plt.Rectangle((0, 0), 1, 1, fc=__colors[2])
        # 左側躺
        ax.bar3d(x, y2, z, dx=1, dy=1, dz=values[2], color=__colors[1])
        label3 = plt.Rectangle((0, 0), 1, 1, fc=__colors[1])
        # 右側躺
        ax.bar3d(x, y3, z, dx=1, dy=1, dz=values[1], color=__colors[3])
        label2 = plt.Rectangle((0, 0), 1, 1, fc=__colors[3])
        # 趴睡
        ax.bar3d(x, y4, z, dx=1, dy=1, dz=values[3], color=__colors[0])
        label1 = plt.Rectangle((0, 0), 1, 1, fc=__colors[0])

        xlabel = ["", "<10秒", "", "11~20秒", "", "21~30秒", "", ">30秒"]
        ylabel = ["", "趴睡", "", "左側躺", "", "", "右側躺", "", "仰躺"]
        ax.set_xticklabels(xlabel, fontproperties=__font)
        ax.set_yticklabels(ylabel, fontproperties=__font)
        ax.legend([label1, label2, label3, label4], ["仰躺", "右側躺", "左側躺",
                  "趴睡"], prop=__font, loc='right', bbox_to_anchor=(1.2, 0.5))
        ax.view_init(elev=10, azim=290)

        # plt.show()
        plt.savefig(
            png_path,
            bbox_inches='tight',
            pad_inches=0,
            transparent=True
        )

    def __draw_3D_bar2(self, values, png_path):
        __colors = COLOR_BAR[:4]
        __font = fm.FontProperties(fname=self.fontPath, size=8)
        fig = plt.figure(figsize=(6, 6))
        ax = plt.subplot(projection='3d')
        x = [2, 4, 6, 8]
        y1 = 10
        y2 = 12
        y3 = 14
        z = 0
        # REM
        ax.bar3d(x, y1, z, dx=1, dy=1, dz=values[0], color=__colors[2])
        label3 = plt.Rectangle((0, 0), 1, 1, fc=__colors[2])
        # 淺眠
        ax.bar3d(x, y2, z, dx=1, dy=1, dz=values[1], color=__colors[1])
        label2 = plt.Rectangle((0, 0), 1, 1, fc=__colors[1])
        # 深眠
        ax.bar3d(x, y3, z, dx=1, dy=1, dz=values[2], color=__colors[0])
        label1 = plt.Rectangle((0, 0), 1, 1, fc=__colors[0])

        xlabel = ["", "<10秒", "", "11~20秒", "", "21~30秒", "", ">30秒"]
        ylabel = ["", "深眠", "", "淺眠", "", "", "REM"]
        ax.set_xticklabels(xlabel, fontproperties=__font)
        ax.set_yticklabels(ylabel, fontproperties=__font)
        ax.legend([label1, label2, label3], ["REM", "淺眠", "深眠"],
                  prop=__font, loc='right', bbox_to_anchor=(1.2, 0.5))
        ax.view_init(elev=10, azim=290)
        # plt.show()
        print(png_path)
        plt.savefig(
            png_path,
            bbox_inches='tight',
            pad_inches=0,
            transparent=True)

    def __addPage(self, mode:int = 0) -> None:
        #mode 0 = default, 1 = blank page
        # y軸

        self.y = 0 + self.pageHeight_mt
        self.report.add_page()
        self.report.alias_nb_pages()
        if mode == 0:
            if (self.report.page_no() == 1):
                self.__gen1PageHeader()
            else:
                self.__genHeader()
            self.__genFooter()
        else:
            pass
    
    def __gen1PageHeader(self) -> None:
        # 報告名稱、logo
        startHeight = self.pageHeight_mt
        cellHeightNo = 4
        self.report.dText(self.pageWidth_mx, startHeight+(self.cellW*1.5),
                          self.header['reportName'], self.fontFamily, 8)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*6),
                          startHeight+(self.cellW*1.5), "測試期間", self.fontFamily, 8)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*6), startHeight +
                          (self.cellW*3), self.header['testingPeriod'], self.fontFamily, 7)
        self.report.dImage(self.pageWidth_mx+(self.rowWidth*9),
                           startHeight-self.cellW, self.logoPath, h=7.5)
        self.__addDriven(self.pageWidth_mx, self.pageWidth_mx +
                         (self.rowWidth*9)-(self.cellW*2), startHeight+(self.cellW*4))
        self.__addDriven(self.pageWidth_mx+(self.rowWidth*9),
                         self.pageWidth_mx+(self.rowWidth*12), startHeight+(self.cellW*4))

        # 使用者和公司資訊
        startHeight = self.pageHeight_mt+(self.cellW*4)
        cellHeightNo = 16
        self.report.dText(self.pageWidth_mx, startHeight +
                          (self.cellW*3), '姓名:', self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx, startHeight +
                          (self.cellW*5), self.userInfo['name'], self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx, startHeight +
                          (self.cellW*9), '生日:', self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx, startHeight+(self.cellW*11),
                          self.userInfo['birthday'], self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*2),
                          startHeight+(self.cellW*3), '年齡:', self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*2), startHeight +
                          (self.cellW*5), str(self.userInfo['age']), self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*2),
                          startHeight+(self.cellW*9), '性別:', self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*2), startHeight +
                          (self.cellW*11), self.userInfo['gender'], self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*4),
                          startHeight+(self.cellW*3), '高度:', self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*4), startHeight +
                          (self.cellW*5), self.userInfo['height'], self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*4),
                          startHeight+(self.cellW*9), '重量:', self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*4), startHeight +
                          (self.cellW*11), self.userInfo['weight'], self.fontFamily, 7)
        self.__addDriven(self.pageWidth_mx, self.pageWidth_mx +
                         (self.rowWidth*9)-(self.cellW*2), startHeight+(self.cellW*13))
        self.report.dText(self.pageWidth_mx+(self.rowWidth*9),
                          startHeight+(self.cellW*3), '公司', self.fontFamily, 8)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*9), startHeight +
                          (self.cellW*5), 'company', self.fontFamily, 8)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*9), startHeight +
                          (self.cellW*9), 'service@koshou.com', self.fontFamily, 8)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*9), startHeight +
                          (self.cellW*11), 'www.koshou.com', self.fontFamily, 8)
        self.__addDriven(self.pageWidth_mx+(self.rowWidth*9),
                         self.pageWidth_mx+(self.rowWidth*12), startHeight+(self.cellW*13))
        pass

    def __genHeader(self) -> None:
        startHeight = self.pageHeight_mt
        self.__addDriven(self.pageWidth_mx, self.pageWidth_mx +
                         self.rowWidth*12, startHeight+(self.cellW*2))
        self.report.set_font(self.fontFamily, size=7)
        self.report.text(self.pageWidth_mx, startHeight +
                         self.cellW, txt='睡眠呼吸中止報告')
        self.report.text(self.pageWidth_mx+(self.rowWidth*4), startHeight +
                         self.cellW, txt='報告日期: '+self.header['reportDate'])
        self.report.text(self.pageWidth_mx+(self.rowWidth*8), startHeight +
                         self.cellW, txt='測試期間: '+self.header['testingPeriod'])
        pass

    def __genFooter(self) -> None:
        startHeight = self.pageHeight_mt+(self.cellW*140)
        self.__addDriven(self.pageWidth_mx, self.pageWidth_mx +
                         self.rowWidth*12, startHeight)
        self.report.set_font(self.fontFamily, size=7)
        self.report.text(self.pageWidth_mx, startHeight +
                         self.cellW*2, txt='使用者: '+self.userInfo['name'])
        self.report.text(self.pageWidth_mx+(self.rowWidth*3),
                         startHeight+self.cellW*2, txt='報告類別: F001V1')
        self.report.text(self.pageWidth_mx+(self.rowWidth*6), startHeight +
                         self.cellW*2, txt='報告日期: '+self.header['reportDate'])
        self.report.text(self.pageWidth_mx+(self.rowWidth*10), startHeight +
                         self.cellW*2, txt='頁數: '+str(self.report.page_no()))
        pass

    def __addSleepApneaReport(self, sleepingState, apnea_state) -> None:
        self.__addPage()
        startHeight = self.pageHeight_mt+(self.cellW*20)
        self.report.sColors()

        self.report.dText(self.pageWidth_mx, startHeight +
                          self.cellW, '睡眠呼吸中止評估', self.fontFamily, 12)
        RDI = round(apnea_state['overview']['RDI'], 1)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*10), startHeight +
                          self.cellW, str(RDI), self.fontFamily, 12)
        self.report.dText(self.pageWidth_mx, startHeight+(self.cellW*4),
                          'SLEEPING APNEA ANALYSIS REPORT', self.fontFamily, 12)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*6),
                          startHeight+(self.cellW*4), "|", self.fontFamily, 7)
        strWidth = self.report.get_string_width("普通")
        self.report.dText(self.pageWidth_mx+(self.rowWidth*6.75)-(strWidth/2),
                          startHeight+(self.cellW*4), "普通", self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*7.5),
                          startHeight+(self.cellW*4), "|", self.fontFamily, 7)
        strWidth = self.report.get_string_width("輕度")
        self.report.dText(self.pageWidth_mx+(self.rowWidth*8.25)-(strWidth/2),
                          startHeight+(self.cellW*4), "輕度", self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*9),
                          startHeight+(self.cellW*4), "|", self.fontFamily, 7)
        strWidth = self.report.get_string_width("中度")
        self.report.dText(self.pageWidth_mx+(self.rowWidth*9.75)-(strWidth/2),
                          startHeight+(self.cellW*4), "中度", self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*10.5),
                    startHeight+(self.cellW*4), "|", self.fontFamily, 7)
        strWidth = self.report.get_string_width("嚴重")
        self.report.dText(self.pageWidth_mx+(self.rowWidth*11.25)-(strWidth/2),
                          startHeight+(self.cellW*4), "嚴重", self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*12),
                          startHeight+(self.cellW*4), "|", self.fontFamily, 7)

        self.report.sColors(drawColor=self.lightGrey, fillColor=self.lightGrey)
        self.report.dRect(self.pageWidth_mx+(self.rowWidth*6), startHeight +
                          (self.cellW*5.5), self.rowWidth*6+0.5, self.cellW*4, 0.2, 'F')
        # scoreWidth = (self.rowWidth*6+0.5)*(qualityReport['score']/100.0)
        # <=5 ：普通 ; >5 ~ 15 : 輕度 ; 15~30 ： 中度, >30 :嚴重
        if RDI < 5:
            scoreWidth = (self.rowWidth*6+0.5)*0.25*(RDI/5)
        elif RDI >= 5 and RDI <15:
            scoreWidth = (self.rowWidth*6+0.5)*0.25 * \
                ((RDI-5)/10) + (self.rowWidth*6+0.5)*0.25
        elif RDI >= 15 and RDI < 30:
            scoreWidth = (self.rowWidth*6+0.5)*0.25 * \
                ((RDI-15)/15) + (self.rowWidth*6+0.5)*0.5
        elif RDI >= 30 and RDI < 100:
            scoreWidth = (self.rowWidth*6+0.5)*0.25 * \
                ((RDI-30)/70) + (self.rowWidth*6+0.5)*0.75
        elif RDI >= 100:
            scoreWidth = (self.rowWidth*6+0.5)*0.25 * \
                (100/100) + (self.rowWidth*6+0.5)*0.75
        self.report.sColors(drawColor=self.black, fillColor=self.black)
        self.report.dRect(self.pageWidth_mx+(self.rowWidth*6), startHeight +
                          (self.cellW*5.5), scoreWidth, self.cellW*4, 0.2, 'F')
        stlen = 3
        if stlen > 0:
            self.report.sColors(txtColor=self.white)
            scoreTextWidth = 3
            self.report.dText(self.pageWidth_mx+(self.rowWidth*6)+scoreWidth-scoreTextWidth-4,
                              startHeight+(self.cellW*8), str(RDI), self.fontFamily, 7)
            self.report.sColors()
        self.__addDriven(self.pageWidth_mx, self.pageWidth_mx +
                         self.rowWidth*12, startHeight+(self.cellW*12))

        self.__analysis_totaly(startHeight+(self.cellW*12), apnea_state)
        self.__addDriven(self.pageWidth_mx, self.pageWidth_mx +
                         self.rowWidth*12, startHeight+(self.cellW*35))
        # levels max *6 [90,60,30,'']
        

        self.__add_heart_rate(startHeight+(self.cellW*36),
                                  sleepingState['date'], sleepingState['time'], apnea_state)

        self.__addDriven(self.pageWidth_mx, self.pageWidth_mx +
                         self.rowWidth*12, startHeight+(self.cellW*65))
        self.__add_apnea_analysis(startHeight+(self.cellW*66),
                            sleepingState['date'], sleepingState['time'], apnea_state)
        # self.__add_breath_all(startHeight+(self.cellW*66),
        #                           sleepingState['date'], sleepingState['time'], apnea_state)
        # self.__analysis_abnormal(startHeight+(self.cellW*65), apnea_state)
        
        # self.__addDriven(self.pageWidth_mx, self.pageWidth_mx +
        #                  self.rowWidth*12, startHeight+(self.cellW*95))


    def __analysis_totaly(self, startHeight, apnea_state):
        title = '分析總覽'
        self.report.dText(self.pageWidth_mx, startHeight +
                          (self.cellW*3.5), title, self.fontFamily, 10)
        # self.report.dText(self.pageWidth_mx+(8), startHeight +
        #                   (self.cellW*6), "指    標", self.fontFamily, 8)

        self.report.dText(self.pageWidth_mx, startHeight +
                          (self.cellW*6), "指    標", self.fontFamily, 8)
        self.report.dText(self.pageWidth_mx+(8)+(self.rowWidth*2), startHeight +
                          (self.cellW*6), "數值", self.fontFamily, 8)
        self.report.dText(self.pageWidth_mx+(8)+(self.rowWidth*4), startHeight +
                          (self.cellW*6), "標準", self.fontFamily, 8)
        self.report.dText(self.pageWidth_mx+2+(self.rowWidth*6), startHeight +
                          (self.cellW*6), "指    標", self.fontFamily, 8)
        self.report.dText(self.pageWidth_mx+(8)+(self.rowWidth*8), startHeight +
                          (self.cellW*6), "數值", self.fontFamily, 8)
        self.report.dText(self.pageWidth_mx+(8)+(self.rowWidth*10), startHeight +
                          (self.cellW*6), "標準", self.fontFamily, 8)

        start_height = startHeight + (self.cellW*3)
        self.__add_analysis_totaly_detail(start_height, self.asign_one_line_content("RDI(呼吸障礙指數):", '{}'.format(round(
            apnea_state['overview']['RDI'], 1)), "<5次/小時", "睡眠總時間:", '{}小時{}分'.format(apnea_state['overview']['totalSleepTime']//60, apnea_state['overview']['totalSleepTime'] % 60), ""))
        start_height = startHeight + (self.cellW*6)
        self.__add_analysis_totaly_detail(start_height, self.asign_one_line_content("呼吸異常總次數:", '{} 次'.format(int(
            apnea_state['overview']['abnormalBreathing'])), "", "臥床總時間:", '{}小時{}分'.format(
            apnea_state['overview']['totalInBedTime']//60, apnea_state['overview']['totalInBedTime'] % 60), ""))
        start_height = startHeight + (self.cellW*9)
        self.__add_analysis_totaly_detail(start_height, self.asign_one_line_content("高頻呼吸異常時間:", '{}'.format(apnea_state['overview']['abnormalHighFreqTime']), "", "測試開始時間:", '{}'.format(apnea_state['overview']['testStartTime']), ""))
        start_height = startHeight + (self.cellW*12)
        # self.__add_analysis_totaly_detail(start_height, self.asign_one_line_content(
        #     "最少呼吸異常時間:", "2022/12/06 12:06", "", "測試開始時間:", '{}'.format(apnea_state['overview']['testStartTime']), ""))
        # start_height = startHeight + (self.cellW*15)
        
        longest_abnormal_time = apnea_state['overview']['longestabnormalTime']
        if not longest_abnormal_time:
            pass
        elif longest_abnormal_time <= 60:
            self.__add_analysis_totaly_detail(start_height, self.asign_one_line_content("最長異常持續時間:", '{} 秒'.format(
                longest_abnormal_time), "", "測試結束時間:", '{}'.format(apnea_state['overview']['testEndTime']), ""))
        elif 3600 > longest_abnormal_time > 60:
            self.__add_analysis_totaly_detail(start_height, self.asign_one_line_content("最長異常持續時間:", '{}分{}秒'.format(
                longest_abnormal_time//60, longest_abnormal_time % 60), "",  "", "測試結束時間:", '{}'.format(apnea_state['overview']['testEndTime']), ""))
        elif longest_abnormal_time > 3600:
            self.__add_analysis_totaly_detail(start_height, self.asign_one_line_content("最長異常持續時間:", '{}小時{}分{}秒'.format(
                longest_abnormal_time//3600, longest_abnormal_time % 3600//60, longest_abnormal_time % 60), "", "測試結束時間:", '{}'.format(apnea_state['overview']['testEndTime']), ""))
        start_height = startHeight + (self.cellW*15)
        self.__add_analysis_totaly_detail(start_height, self.asign_one_line_content("", "", "", "", '', ""))

    def __analysis_abnormal(self, startHeight, apnea_state):
        title = '異常分析'
        self.report.dText(self.pageWidth_mx, startHeight +
                          (self.cellW*3.5), title, self.fontFamily, 10)

        self.report.dText(self.pageWidth_mx+(8)+(self.rowWidth*3), startHeight +
                          (self.cellW*6), "異常持續時間", self.fontFamily, 8)
        self.report.dText(self.pageWidth_mx+(8)+(self.rowWidth*5), startHeight +
                          (self.cellW*6), "發生次數", self.fontFamily, 8)
        self.report.dText(self.pageWidth_mx+(8)+(self.rowWidth*7), startHeight +
                          (self.cellW*6), "佔比", self.fontFamily, 8)

        # check array length and replace
        if len(apnea_state['abnormalAnalysis']['abnormalDuration']['occurNums']) != 5 or len(apnea_state['abnormalAnalysis']['abnormalDuration']['percentage']) != 5:
            raise "abnormalAnalysis.abnormalDuration.occurNums or percentage ERROR"
        abnormal_duration_list = [int(i) if int(
            i) != 0 else '--' for i in apnea_state['abnormalAnalysis']['abnormalDuration']['occurNums']]
        abnormal_duration_percentage_list = [int(
            i*100) for i in apnea_state['abnormalAnalysis']['abnormalDuration']['percentage']]
        start_height = startHeight + (self.cellW*3)
        # self.__add_analysis_abnormal(start_height, self.asign_one_line_content("<=5秒:", '{} 次'.format(
        #     abnormal_duration_list[0]), '{} %'.format(abnormal_duration_percentage_list[0]), "", "", ""))
        # start_height = startHeight + (self.cellW*6)
        # self.__add_analysis_abnormal(start_height, self.asign_one_line_content("6~10秒:", '{} 次'.format(
        #     abnormal_duration_list[1]), '{} %'.format(abnormal_duration_percentage_list[1]), "", "", ""))
        self.__add_analysis_abnormal(start_height, self.asign_one_line_content("11~15秒:", '{} 次'.format(
            abnormal_duration_list[0]), '{} %'.format(abnormal_duration_percentage_list[0]), "", "", ""))
        start_height = startHeight + (self.cellW*6)
        self.__add_analysis_abnormal(start_height, self.asign_one_line_content("16~20秒:", '{} 次'.format(
            abnormal_duration_list[1]), '{} %'.format(abnormal_duration_percentage_list[1]), "", "", ""))
        start_height = startHeight + (self.cellW*9)
        self.__add_analysis_abnormal(start_height, self.asign_one_line_content("21~25秒:", '{} 次'.format(
            abnormal_duration_list[2]), '{} %'.format(abnormal_duration_percentage_list[2]), "", "", ""))
        start_height = startHeight + (self.cellW*12)
        self.__add_analysis_abnormal(start_height, self.asign_one_line_content("26~30秒:", '{} 次'.format(
            abnormal_duration_list[3]), '{} %'.format(abnormal_duration_percentage_list[3]), "", "", ""))
        start_height = startHeight + (self.cellW*15)
        self.__add_analysis_abnormal(start_height, self.asign_one_line_content(">31秒:", '{} 次'.format(
            abnormal_duration_list[4]), '{} %'.format(abnormal_duration_percentage_list[4]), "", "", ""))

    def asign_one_line_content(self, key1, value1, normal1, key2, value2, normal2) -> dict:
        one_line_content = {
            "key1": key1,
            "value1": value1,
            "normal1": normal1,
            "key2": key2,
            "value2": value2,
            "normal2": normal2
        }
        return one_line_content

    def __add_analysis_totaly_detail(self, start_height, one_line_content: dict):

        self.report.dText(self.pageWidth_mx, start_height +
                          (self.cellW*6), one_line_content['key1'], self.fontFamily, 8)
        self.report.dText(self.pageWidth_mx+8+(self.rowWidth*2), start_height +
                          (self.cellW*6), one_line_content['value1'], self.fontFamily, 8)
        self.report.dText(self.pageWidth_mx+7+(self.rowWidth*4), start_height +
                          (self.cellW*6), one_line_content['normal1'], self.fontFamily, 8)
        self.report.dText(self.pageWidth_mx+2+(self.rowWidth*6), start_height +
                          (self.cellW*6), one_line_content['key2'], self.fontFamily, 8)
        self.report.dText(self.pageWidth_mx+8+(self.rowWidth*8), start_height +
                          (self.cellW*6), one_line_content['value2'], self.fontFamily, 8)
        self.report.dText(self.pageWidth_mx+8+(self.rowWidth*10), start_height +
                          (self.cellW*6), one_line_content['normal2'], self.fontFamily, 8)
        pass

    def __add_analysis_abnormal(self, start_height, one_line_content: dict):

        self.report.dText(self.pageWidth_mx+8+(self.rowWidth*3), start_height +
                          (self.cellW*6), one_line_content['key1'], self.fontFamily, 8)
        self.report.dText(self.pageWidth_mx+8+(self.rowWidth*5), start_height +
                          (self.cellW*6), one_line_content['value1'], self.fontFamily, 8)
        self.report.dText(self.pageWidth_mx+8+(self.rowWidth*7), start_height +
                          (self.cellW*6), one_line_content['normal1'], self.fontFamily, 8)
        self.report.dText(self.pageWidth_mx+8+(self.rowWidth*6), start_height +
                          (self.cellW*6), one_line_content['key2'], self.fontFamily, 8)
        self.report.dText(self.pageWidth_mx+8+(self.rowWidth*8), start_height +
                          (self.cellW*6), one_line_content['value2'], self.fontFamily, 8)
        self.report.dText(self.pageWidth_mx+8+(self.rowWidth*10), start_height +
                          (self.cellW*6), one_line_content['normal2'], self.fontFamily, 8)
        pass

    def __add_heart_rate(self, startHeight, date, time, values):
        dt = datetime.strptime(date+' '+time, "%Y/%m/%d %H:%M:%S")
        # tt = dt.replace(minute=0, second=0,microsecond=0).timestamp()
        tt = dt.timestamp()
        cleaned_list = []
        start_tt = dt.timestamp()
        end_tt = datetime.strptime(values['overview']['testEndTime'], "%Y/%m/%d %H:%M:%S").timestamp()
        
        max_value = max(values['wholeNightHeartRate']['numArray']) 
        # max value = 40
        if max_value>120:
            levels = ['140','120','100','80', '60','40']
        if 100< max_value <= 120:
            levels = ['120','100','80', '60','40']
        elif max_value <= 100:
            levels = ['100','80','60','40']
        

        # 8H values
        eHUnitNo = len(levels)
        uspace = 0.366
        fyNo = 480
        uWidth = uspace*480 
        xUnitNo = 16
        # data
        one_width = 60*uspace
        line_width = 4.13
        line_interval = 1.78
        
        title = '心率變化圖'+" (8H SLEEP)"
        vNo = len(values['wholeNightHeartRate']['numArray'])
        if (vNo > 480):#480*60
            title = '心率變化圖'+" (10H SLEEP)"
            uspace = 0.293
            fyNo = 600
            uWidth = uspace*600
            xUnitNo = 20
        if (vNo > 600):#600*60
            title = '心率變化圖'+" (12H SLEEP)"
            uspace = 0.244
            fyNo = 720
            uWidth = uspace*720
            xUnitNo = 24
            one_width = 60*uspace
            line_width = 2.65
            line_interval = 0.8

        eHUnit = self.cellW*3.5
        hspace = eHUnit*(eHUnitNo-1)
        self.report.sColors()
        self.report.dText(self.pageWidth_mx, startHeight +
                          (self.cellW*3.5), title, self.fontFamily, 10)

        # x-axis hidden line
        for i in range(0, eHUnitNo):
            self.report.sColors()
            self.report.dText(self.pageWidth_mx+12, startHeight +
                              (self.cellW*7)+(i*eHUnit), levels[i], self.fontFamily, 5)
            self.report.sColors(drawColor=self.lightGrey)
            self.report.dLine(self.pageWidth_mx+self.rowWidth, startHeight+(self.cellW*7)+(i*eHUnit),
                              self.pageWidth_mx+self.rowWidth+uWidth, startHeight+(self.cellW*7)+(i*eHUnit), 0.15)
        # y-axis hidden line
        for i in range(0, xUnitNo+1):
            self.report.sColors(drawColor=self.lightGrey)
            self.report.dLine(self.pageWidth_mx+self.rowWidth+(i*30*uspace), startHeight+(self.cellW*7),
                              self.pageWidth_mx+self.rowWidth+(i*30*uspace), startHeight+(self.cellW*7)+((eHUnitNo-1)*eHUnit), 0.15)

        # set x-axis time label
        self.report.set_font(self.fontFamily, size=5)
        for i in range(0, xUnitNo+1):
            self.report.rotate(45, self.pageWidth_mx+(self.rowWidth)-(self.cellW)+(
                i*uspace*30), startHeight+(self.cellW*11)+((eHUnitNo-1)*eHUnit))
            tstr = datetime.fromtimestamp(tt+(i*1800)).strftime('%H:%M')
            self.report.dText(self.pageWidth_mx+(self.rowWidth)-(self.cellW)+(i*uspace*30),
                              startHeight+(self.cellW*11)+((eHUnitNo-1)*eHUnit), tstr, self.fontFamily, 5)
            self.report.rotate(0, self.pageWidth_mx+(self.rowWidth)-(self.cellW)+(
                i*uspace*30), startHeight+(self.cellW*11)+((eHUnitNo-1)*eHUnit))

        if (vNo > fyNo):
            vNo = fyNo
        preV = -1
        delta_y = (len(levels)-1)*eHUnit
        # self.report.dText(self.pageWidth_mx, startHeight +(self.cellW*7), "test", self.fontFamily, 6)
        # self.report.dText(self.pageWidth_mx, startHeight +(self.cellW*7)+delta_y, "test2", self.fontFamily, 6)
        # self.report.dText(self.pageWidth_mx, (startHeight +(self.cellW*7)+delta_y)-(delta_y*((values['wholeNightHeartRate']['numArray'][0]-40)/(int(levels[0])-40))), "one", self.fontFamily, 6)
        for i in range(0, vNo):
            if (values['wholeNightHeartRate']['numArray'][i] > -1 and preV > -1):
                prey = (startHeight +(self.cellW*7)+delta_y)- (delta_y*(
                    (preV-int(levels[-1]))/
                    (int(levels[0])-int(levels[-1]))
                ))
                cury = (startHeight +(self.cellW*7)+delta_y)-(delta_y*(
                    (values['wholeNightHeartRate']['numArray'][i]-int(levels[-1]))/
                    (int(levels[0])-int(levels[-1]))
                ))

                self.report.sColors()
                self.report.dLine(self.pageWidth_mx+self.rowWidth+((i-1)*uspace),
                                  prey, self.pageWidth_mx+self.rowWidth+((i)*uspace), cury, 0.3)
            preV = values['wholeNightHeartRate']['numArray'][i]

    def __add_breath_all(self, startHeight, date, time, values):
        dt = datetime.strptime(date+' '+time, "%Y/%m/%d %H:%M:%S")
        # tt = dt.replace(minute=0, second=0,microsecond=0).timestamp()
        tt = dt.timestamp()
        cleaned_list = []
        start_tt = dt.timestamp()
        end_tt = datetime.strptime(values['overview']['testEndTime'], "%Y/%m/%d %H:%M:%S").timestamp()

        max_value = max(values['wholeNightBreathRate']['numArray']) 
        # max value = 40
        if max_value>40:
            max_value = 40
        if 30< max_value <= 40:
            levels = ['40','30','20', '10','0']
        elif max_value <= 30:
            levels = ['30','20','10','0']
        
        
        # 8H values
        eHUnitNo = len(levels)
        uspace = 0.366
        fyNo = 480
        uWidth = uspace*480*60  # 8H = 8*60m
        xUnitNo = 16
        # data
        one_width = 60*uspace
        line_width = 4.13
        line_interval = 1.78
        
        title = '呼吸率變化圖'+" (8H SLEEP)"
        vNo = len(values['wholeNightBreathRate']['numArray'])


        if (vNo > 480):
            title = '呼吸率變化圖'+" (10H SLEEP)"
            uspace = 0.293
            fyNo = 600
            uWidth = uspace*600
            xUnitNo = 20
        if (vNo > 600):
            title = '呼吸率變化圖'+" (12H SLEEP)"
            uspace = 0.244
            fyNo = 720
            uWidth = uspace*720
            xUnitNo = 24
            one_width = 60*uspace
            line_width = 2.65
            line_interval = 0.8

        eHUnit = self.cellW*3.5
        hspace = eHUnit*(eHUnitNo-1)/60
        self.report.sColors()
        self.report.dText(self.pageWidth_mx, startHeight +
                          (self.cellW*3.5), title, self.fontFamily, 10)

        # x-axis hidden line
        for i in range(0, eHUnitNo):
            self.report.sColors()
            self.report.dText(self.pageWidth_mx+12, startHeight +
                              (self.cellW*7)+(i*eHUnit), levels[i], self.fontFamily, 5)
            self.report.sColors(drawColor=self.lightGrey)
            self.report.dLine(self.pageWidth_mx+self.rowWidth, startHeight+(self.cellW*7)+(i*eHUnit),
                              self.pageWidth_mx+self.rowWidth+uWidth, startHeight+(self.cellW*7)+(i*eHUnit), 0.15)
        # y-axis hidden line
        for i in range(0, xUnitNo+1):
            self.report.sColors(drawColor=self.lightGrey)
            self.report.dLine(self.pageWidth_mx+self.rowWidth+(i*30*uspace), startHeight+(self.cellW*7),
                              self.pageWidth_mx+self.rowWidth+(i*30*uspace), startHeight+(self.cellW*7)+((eHUnitNo-1)*eHUnit), 0.15)

        # set x-axis time label
        self.report.set_font(self.fontFamily, size=5)
        for i in range(0, xUnitNo+1):
            self.report.rotate(45, self.pageWidth_mx+(self.rowWidth)-(self.cellW)+(
                i*uspace*30), startHeight+(self.cellW*11)+((eHUnitNo-1)*eHUnit))
            tstr = datetime.fromtimestamp(tt+(i*1800)).strftime('%H:%M')
            self.report.dText(self.pageWidth_mx+(self.rowWidth)-(self.cellW)+(i*uspace*30),
                              startHeight+(self.cellW*11)+((eHUnitNo-1)*eHUnit), tstr, self.fontFamily, 5)
            self.report.rotate(0, self.pageWidth_mx+(self.rowWidth)-(self.cellW)+(
                i*uspace*30), startHeight+(self.cellW*11)+((eHUnitNo-1)*eHUnit))

        if (vNo > fyNo):
            vNo = fyNo
        preV = -1
        delta_y = (len(levels)-1)*eHUnit
        for i in range(0, vNo):
            if (values['wholeNightBreathRate']['numArray'][i] > -1 and preV > -1):
                prey = (startHeight +(self.cellW*7)+delta_y)- (delta_y*(preV/int(levels[0])))
                cury = (startHeight +(self.cellW*7)+delta_y)-(delta_y*(values['wholeNightBreathRate']['numArray'][i]/int(levels[0])))

                self.report.sColors()
                self.report.dLine(self.pageWidth_mx+self.rowWidth+((i-1)*uspace),
                                  prey, self.pageWidth_mx+self.rowWidth+((i)*uspace), cury, 0.3)
            preV = values['wholeNightBreathRate']['numArray'][i]
    
    def __add_apnea_analysis(self, startHeight, date, time, values):
        dt = datetime.strptime(date+' '+time, "%Y/%m/%d %H:%M:%S")
        # tt = dt.replace(minute=0, second=0,microsecond=0).timestamp()
        tt = dt.timestamp()
        # cleaned_list = []
        start_tt = dt.timestamp()
        end_tt = datetime.strptime(values['overview']['testEndTime'], "%Y/%m/%d %H:%M:%S").timestamp()
        # for index, i in enumerate(values['apneaTimeline']['timeArray']):
        #     if datetime.strptime(i, "%Y-%m-%d %H:%M:%S").timestamp() < start_tt:
        #         cleaned_list.append(-1)
        #     elif datetime.strptime(i, "%Y-%m-%d %H:%M:%S").timestamp() > end_tt or end_tt - datetime.strptime(i, "%Y-%m-%d %H:%M:%S").timestamp() < 60*15:
                
        #         cleaned_list.append(-1)
        #     else:
        #         cleaned_list.append(values['apneaTimeline']['numArray'][index])
        levels_template = ['15','10','5','0']
        # max is *6 [90,60,30,0]
        levels = levels_template
        for i in range(1, 7):
            if (i-1)*15 < max(values['apneaTimeline']['numArray']) <= 15*i:
                levels = [str(int(j)*i)for j in levels_template]
        
        
        # 8H values
        eHUnitNo = len(levels)
        uspace = 0.366
        fyNo = 480
        uWidth = uspace*480  # 8H = 8*60m
        xUnitNo = 16
        # data
        one_width = 30*uspace # 10.92
        line_width = 0.2928 # 10.92 *0.8 / 30
        line_interval = 0.075 # 10.92 * 0.2 /29
        
        title = '呼吸中止統計'
        # vNo = values['overview']['totalSleepTime']
        vNo = len(values['apneaTimeline']['numArray'])
        if (vNo > 480):
            uspace = 0.293
            fyNo = 600
            uWidth = uspace*600
            xUnitNo = 20
            one_width = 30*uspace #8.79
            line_width = 0.2344 # 8.79 *0.8 /30 
            line_interval = 0.06 # 8.79 *0.2 /29
            
        if (vNo > 600):
            uspace = 0.244
            fyNo = 720
            uWidth = uspace*720
            xUnitNo = 24
            one_width = 30*uspace #7.32
            line_width = 0.1952 # 7.32 *0.8 /30 
            line_interval = 0.05 # 7.32 *0.2 /29
        
        eHUnit = self.cellW*3.5
        hspace = eHUnit*(eHUnitNo-1)/60
        self.report.sColors()
        self.report.dText(self.pageWidth_mx, startHeight +
                          (self.cellW*3.5), title, self.fontFamily, 10)

        # x-axis hidden line
        for i in range(0, eHUnitNo):
            self.report.sColors()
            self.report.dText(self.pageWidth_mx+12, startHeight +
                              (self.cellW*7)+(i*eHUnit), levels[i], self.fontFamily, 5)
            self.report.sColors(drawColor=self.lightGrey)
            self.report.dLine(self.pageWidth_mx+self.rowWidth, startHeight+(self.cellW*7)+(i*eHUnit),
                              self.pageWidth_mx+self.rowWidth+uWidth, startHeight+(self.cellW*7)+(i*eHUnit), 0.15)
        # y-axis hidden line
        for i in range(0, xUnitNo+1):
            self.report.sColors(drawColor=self.lightGrey)
            self.report.dLine(self.pageWidth_mx+self.rowWidth+(i*30*uspace), startHeight+(self.cellW*7),
                              self.pageWidth_mx+self.rowWidth+(i*30*uspace), startHeight+(self.cellW*7)+((eHUnitNo-1)*eHUnit), 0.15)

        # set x-axis time label
        self.report.set_font(self.fontFamily, size=5)
        for i in range(0, xUnitNo+1):
            self.report.rotate(45, self.pageWidth_mx+(self.rowWidth)-(self.cellW)+(
                i*uspace*30), startHeight+(self.cellW*11)+((eHUnitNo-1)*eHUnit))
            tstr = datetime.fromtimestamp(tt+(i*1800)).strftime('%H:%M')
            self.report.dText(self.pageWidth_mx+(self.rowWidth)-(self.cellW)+(i*uspace*30),
                              startHeight+(self.cellW*11)+((eHUnitNo-1)*eHUnit), tstr, self.fontFamily, 5)
            self.report.rotate(0, self.pageWidth_mx+(self.rowWidth)-(self.cellW)+(
                i*uspace*30), startHeight+(self.cellW*11)+((eHUnitNo-1)*eHUnit))

        # data
        self.report.sColors(drawColor=self.orange, fillColor=self.orange)
        
        line_num_in_one_block = 30
        
        for i in range(len(values['apneaTimeline']['numArray'])//line_num_in_one_block):
            for j in range(0, line_num_in_one_block):
                if values['apneaTimeline']['numArray'][(i*line_num_in_one_block)+j] != -1:
                    self.report.dRect(
                        self.pageWidth_mx+line_interval+self.rowWidth+(i*one_width)+j*line_interval+j*line_width, 
                        startHeight+(self.cellW*7)+((eHUnitNo-1)*eHUnit), 
                        w=line_width, 
                        h=-((eHUnitNo-1)*eHUnit)*(values['apneaTimeline']['numArray'][(i*line_num_in_one_block)+j])/max([int(i) for i in levels]), style='F')
                    
        for j in range(len(values['apneaTimeline']['numArray'])%line_num_in_one_block):
            if values['apneaTimeline']['numArray'][((len(values['apneaTimeline']['numArray'])//line_num_in_one_block)*line_num_in_one_block)+j] != -1:
                self.report.dRect(
                    self.pageWidth_mx+self.rowWidth+((len(values['apneaTimeline']['numArray'])//line_num_in_one_block)*one_width)+j*line_interval+j*line_width, 
                    startHeight+(self.cellW*7)+((eHUnitNo-1)*eHUnit), 
                    w=line_width, 
                    h=-((eHUnitNo-1)*eHUnit)*(values['apneaTimeline']['numArray'][((len(values['apneaTimeline']['numArray'])//line_num_in_one_block)*line_num_in_one_block)+j])/max([int(j) for j in levels]), style='F')
                                
    def __addNote(self, note) -> None:
        startHeight = self.pageHeight_mt+(self.cellW*117)
        cellHeightNo = 24
        self.report.set_draw_color(0, 0, 0)
        self.report.set_fill_color(255, 255, 255)
        self.report.set_text_color(0, 0, 0)
        self.report.rect(self.pageWidth_mx, startHeight,
                         self.rowWidth*self.rowNo, self.cellW*(cellHeightNo-2), '')
        self.report.text(self.pageWidth_mx+self.cellW,
                         startHeight+(self.cellW*1.5), "NOTES")
        if len(note) > 0:
            self.report.set_xy(self.pageWidth_mx+self.cellW,
                               startHeight+(self.cellW*2))
            self.report.multi_cell(
                w=(self.rowWidth*12)-(4*self.cellW), h=self.cellW*2, txt=note, align='L')
        pass

    def __add_pie_descrition(self, start_height, one_line_content: dict):
        self.report.dText(self.pageWidth_mx, start_height +
                          (self.cellW*6), one_line_content['key1'], self.fontFamily, 8)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*2), start_height +
                          (self.cellW*6), one_line_content['value1'], self.fontFamily, 8)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*4), start_height +
                          (self.cellW*6), one_line_content['normal1'], self.fontFamily, 8)

    def __add_position_abnormal_summary(self, startHeight, abnormal_posture_statistic):
        title = '睡姿發生呼吸異常統計圖'
        self.report.sColors()
        self.report.dText(self.pageWidth_mx, startHeight +
                          (self.cellW*3.5), title, self.fontFamily, 10)
        # check array length and replace
        if len(abnormal_posture_statistic['occurNums']) != 5 or len(abnormal_posture_statistic['percentage']) != 5:
            raise "sleepingPostureEvaluation.abnormal_posture_statistic.occurNums or percentage ERROR"

        start_height = startHeight + (self.cellW*1)
        self.__add_pie_descrition(
            start_height, self.asign_one_line_content("睡姿", "發生次數", "佔比", "", "", ""))
        start_height = startHeight + (self.cellW*4)
        self.__add_pie_descrition(start_height, self.asign_one_line_content("仰躺:", "{}次".format(
            abnormal_posture_statistic['occurNums'][0]), "{}%".format(round(abnormal_posture_statistic['percentage'][0]*100), 2), "", "", ""))
        start_height = startHeight + (self.cellW*7)
        self.__add_pie_descrition(start_height, self.asign_one_line_content("左側躺:", "{}次".format(
            abnormal_posture_statistic['occurNums'][1]), "{}%".format(round(abnormal_posture_statistic['percentage'][1]*100), 2), "", "", ""))
        start_height = startHeight + (self.cellW*10)
        self.__add_pie_descrition(start_height, self.asign_one_line_content("趴睡:", "{}次".format(
            abnormal_posture_statistic['occurNums'][2]), "{}%".format(round(abnormal_posture_statistic['percentage'][2]*100), 2), "", "", ""))
        start_height = startHeight + (self.cellW*13)
        self.__add_pie_descrition(start_height, self.asign_one_line_content("右側躺:", "{}次".format(
            abnormal_posture_statistic['occurNums'][3]), "{}%".format(round(abnormal_posture_statistic['percentage'][3]*100), 2), "", "", ""))
        start_height = startHeight + (self.cellW*16)
        self.__add_pie_descrition(start_height, self.asign_one_line_content("直立:", "{}次".format(
            abnormal_posture_statistic['occurNums'][4]), "{}%".format(round(abnormal_posture_statistic['percentage'][4]*100), 2), "", "", ""))

    def __add_position_assessment(self, sleepingState, sleeping_posture_evaluation, sleeping_quality_evaluation, apnea_state) -> None:
        self.__addPage(mode=1)
        startHeight = self.pageHeight_mt+(self.cellW*2)
        cellHeightNo = 6
        self.report.set_draw_color(0, 0, 0)
        self.report.set_fill_color(255, 255, 255)
        self.report.set_text_color(0, 0, 0)
        self.report.set_font(self.fontFamily, size=12)
        self.report.text(self.pageWidth_mx, startHeight +
                         (self.cellW*4), "睡姿影響評估")
        
        self.report.sColors()
        
        #睡眠深熟度發生呼吸異常統計圖
        self.__add_sleep_abnormal_summary(startHeight+(self.cellW*cellHeightNo)+66*2, 
                                    sleeping_quality_evaluation['abnormalStateStatistic'])
        self.report.dImage(self.pageWidth_mx+(self.rowWidth*5.5),
            (startHeight+(self.cellW*cellHeightNo)+66*2)*0.92, self.sleep_pie_path, h=self.rowWidth*5.5)

        #睡眠深熟度異常嚴重度分析圖
        self.report.dText(self.pageWidth_mx, startHeight+(self.cellW*cellHeightNo)+66*3+(self.cellW*3.5),
                          "睡眠深熟度異常嚴重度分析圖", self.fontFamily, 10)
        self.report.dImage(
            self.pageWidth_mx+(self.rowWidth*3),
            (startHeight+(self.cellW*cellHeightNo)+66*3)*0.96,
            self.sleep_bar_path,
            h=self.rowWidth*5.055
        )

        #睡姿發生呼吸異常統計圖
        self.report.sColors()
        self.report.dImage(self.pageWidth_mx+(self.rowWidth*5.5),
                    startHeight-2, self.position_pie_path, h=self.rowWidth*5.5)
        
        #睡姿嚴重度分析圖
        self.report.dText(self.pageWidth_mx, startHeight+(self.cellW*cellHeightNo)+66+(self.cellW*3.5), "睡姿嚴重度分析圖", self.fontFamily, 10)
        self.__add_position_abnormal_summary(startHeight+(self.cellW*cellHeightNo), sleeping_posture_evaluation['abnPostureStatistic'])
        self.report.dImage(
            self.pageWidth_mx+(self.rowWidth*3),
            (startHeight+(self.cellW*cellHeightNo)+66)*0.9,
            self.position_bar_path,
            h=self.rowWidth*5.055
        )

    

        #(286-22)/4 =66
        self.__genHeader()
        self.__genFooter()
        for i in range(4):
            self.__addDriven(self.pageWidth_mx, self.pageWidth_mx +
                            self.rowWidth*12, startHeight+(self.cellW*cellHeightNo)+66*i)

    def __add_sleep_abnormal_summary(self, startHeight, abnormal_sleep_statistic):
        title = '睡眠深熟度發生呼吸異常統計圖'
        self.report.sColors()
        self.report.dText(self.pageWidth_mx, startHeight +
                          (self.cellW*3.5), title, self.fontFamily, 10)
        start_height = startHeight + (self.cellW*1)
        self.__add_pie_descrition(start_height, self.asign_one_line_content(
            "睡眠分期", "發生次數", "佔比", "", "", ""))
        start_height = startHeight + (self.cellW*4)
        self.__add_pie_descrition(start_height, self.asign_one_line_content("REM:", "{}次".format(
            abnormal_sleep_statistic['occurNums'][0]), "{}%".format(round(abnormal_sleep_statistic['percentage'][0]*100), 2), "", "", ""))
        start_height = startHeight + (self.cellW*7)
        self.__add_pie_descrition(start_height, self.asign_one_line_content("淺眠:", "{}次".format(
            abnormal_sleep_statistic['occurNums'][1]), "{}%".format(round(abnormal_sleep_statistic['percentage'][1]*100), 2), "", "", ""))
        start_height = startHeight + (self.cellW*10)
        self.__add_pie_descrition(start_height, self.asign_one_line_content("深眠:", "{}次".format(
            abnormal_sleep_statistic['occurNums'][2]), "{}%".format(round(abnormal_sleep_statistic['percentage'][2]*100), 2), "", "", ""))

    def __add_breath(self, apnea_state, breath_signals):
        self.__addPage()
        startHeight = self.pageHeight_mt+(self.cellW*2)
        cellHeightNo = 6
        self.report.set_draw_color(0, 0, 0)
        self.report.set_fill_color(255, 255, 255)
        self.report.set_text_color(0, 0, 0)
        self.report.set_font(self.fontFamily, size=12)
        self.report.text(self.pageWidth_mx, startHeight +
                         (self.cellW*4), "呼吸訊號圖")
        self.__addDriven(self.pageWidth_mx, self.pageWidth_mx +
                    self.rowWidth*12, startHeight+(self.cellW*cellHeightNo))
        for i in range(2):
            self.__addDriven(self.pageWidth_mx, self.pageWidth_mx +
                    self.rowWidth*12, startHeight+(self.cellW*cellHeightNo)+50+88*i)
        self.__analysis_abnormal(startHeight+(self.cellW*6), apnea_state)
            
        # if there are data of longestAbnDuration , else pass
        data = breath_signals['longestAbnDuration']
        if data:
            self.__add_hrv_and_breath(startHeight+(self.cellW*cellHeightNo)+50+88*0, "最大異常持續發生時間",
                                  breath_signals['longestAbnDuration'], "")

            # 異常呼吸圖
            if len(breath_signals['otherAbnBreathSignals']) > 0:
                if (len(breath_signals['otherAbnBreathSignals'])-2) % 3 != 0:
                    add_page_num = (
                        (len(breath_signals['otherAbnBreathSignals'])-2)//3)+1
                else:
                    add_page_num = (
                        len(breath_signals['otherAbnBreathSignals'])-2)//3
                for i in range(len(breath_signals['otherAbnBreathSignals'])):
                    if i == 0:
                        self.__add_hrv_and_breath(
                            startHeight+(self.cellW*cellHeightNo)+50+88*1, "異常呼吸圖", breath_signals['otherAbnBreathSignals'][i])
                '''
                notes
                '''
                __startHeight = self.pageHeight_mt+(self.cellW*122)
                self.report.set_draw_color(0, 0, 0)
                self.report.set_fill_color(255, 255, 255)
                self.report.set_text_color(0, 0, 0)
                self.report.rect(self.pageWidth_mx, __startHeight,
                                self.rowWidth*self.rowNo, self.cellW*(cellHeightNo*4-7), '')
                self.report.text(self.pageWidth_mx+self.cellW,
                                __startHeight+(self.cellW*1.5), "NOTES")
                if len("") > 0:
                    self.report.set_xy(self.pageWidth_mx+self.cellW,
                                    __startHeight+(self.cellW*2))
                    self.report.multi_cell(
                        w=(self.rowWidth*12)-(4*self.cellW), h=self.cellW*2, txt="", align='L')
                # least data
                for j in range(0, add_page_num):
                    self.__addPage()
                    for k in range(3):
                        self.__addDriven(self.pageWidth_mx, self.pageWidth_mx +self.rowWidth*12, startHeight+(self.cellW*cellHeightNo)+88*k)
                    startHeight = self.pageHeight_mt+(self.cellW*2)
                    self.report.sColors()
                    self.report.dText(
                        self.pageWidth_mx, startHeight + (self.cellW*4), "呼吸訊號圖", self.fontFamily, 12)
                    # - up two fig
                    for i in range(len(breath_signals['otherAbnBreathSignals'])-1-(j*3)):
                            self.__add_hrv_and_breath(
                                startHeight+(self.cellW*cellHeightNo)+88*i, "異常呼吸圖", breath_signals['otherAbnBreathSignals'][i+1])
   

        # else:
        #     # 異常呼吸圖
        #     if len(breath_signals['otherAbnBreathSignals']) > 0:
        #         if (len(breath_signals['otherAbnBreathSignals'])-2) % 4 != 0:
        #             add_page_num = (
        #                 (len(breath_signals['otherAbnBreathSignals'])-2)//4)+1
        #         else:
        #             add_page_num = (
        #                 len(breath_signals['otherAbnBreathSignals'])-2)//4
        #         self.__addDriven(self.pageWidth_mx, self.pageWidth_mx +
        #                          self.rowWidth*12, startHeight+(self.cellW*104))
        #         for i in range(len(breath_signals['otherAbnBreathSignals'])):
        #             if i == 0:
        #                 self.__add_hrv_and_breath(
        #                     startHeight+(self.cellW*(70)), "異常呼吸圖", breath_signals['otherAbnBreathSignals'][i])
        #             elif i == 1:
        #                 self.__add_hrv_and_breath(
        #                     startHeight+(self.cellW*(104)), "", breath_signals['otherAbnBreathSignals'][i])
        #         for j in range(0, add_page_num):
        #             self.__addPage()
        #             startHeight = self.pageHeight_mt+(self.cellW*2)
        #             self.report.sColors()
        #             self.report.dText(
        #                 self.pageWidth_mx, startHeight + (self.cellW*4), "呼吸訊號圖", self.fontFamily, 12)
        #             self.__addDriven(self.pageWidth_mx, self.pageWidth_mx +
        #                              self.rowWidth*12, startHeight+(self.cellW*cellHeightNo))
        #             # - up two fig
        #             for i in range(len(breath_signals['otherAbnBreathSignals'])-2-(j*4)):
        #                 if i == 0:
        #                     self.__add_hrv_and_breath(
        #                         startHeight+(self.cellW*(6)), "異常呼吸圖", breath_signals['otherAbnBreathSignals'][i+2])
        #                     self.__addDriven(
        #                         self.pageWidth_mx, self.pageWidth_mx + self.rowWidth*12, startHeight+(self.cellW*40))
        #                 else:
        #                     self.__add_hrv_and_breath(
        #                         startHeight+(self.cellW*(6+i*34)), "", breath_signals['otherAbnBreathSignals'][i+2])
        #                     self.__addDriven(self.pageWidth_mx, self.pageWidth_mx +
        #                                      self.rowWidth*12, startHeight+(self.cellW*(6+(i+1)*34)))

    def __add_hrv_and_breath(self, start_height, title, target_content, special_text="", fig_title="Abnormal Breath"):
        start_height_pre = start_height
        self.report.sColors()
        if title != "":
            self.report.dText(self.pageWidth_mx, start_height +(self.cellW*2.5), title, self.fontFamily, 10)
            start_height = start_height + (self.cellW*15)
            self.__add_pie_descrition(start_height, self.asign_one_line_content(
                target_content['date'], 'BR: {}bpm'.format(target_content['breath']), special_text, "", "", ""))
            start_height = start_height + (self.cellW*1.5)
            self.__add_pie_descrition(start_height, self.asign_one_line_content(
                target_content['time'], "", "", "", "", ""))
        else:
            self.__add_pie_descrition(start_height-(self.cellW*3.5), self.asign_one_line_content(
                target_content['date'], 'BR: {}bpm'.format(target_content['breath']), special_text, "", "", ""))
            self.__add_pie_descrition(
                start_height-(self.cellW*1.5), self.asign_one_line_content(target_content['time'], "", "", "", "", ""))
        
        delta_x = 0.07*2499
        delta_y = delta_x/50*6
        eUnit = delta_y/6
        """
        heart rate part
        """
        start_x = self.pageWidth_mx+(self.rowWidth)-(self.cellW)
        start_y = start_height_pre+(self.cellW*6)
        end_x = start_x + (delta_x)
        end_y = start_y+delta_y
        self.report.dText(self.pageWidth_mx + self.rowWidth*6,
                          start_height_pre+(self.cellW*5.5), "Heart Rate Variation", self.fontFamily, 6)
        self.report.dRect(start_x,
                            start_y, delta_x, delta_y, 0.15, 'D')
        
        # x-axis time label
        self.report.set_font(self.fontFamily, size=5)
        if title != "最小呼吸速率":
            dt = datetime.strptime(
                target_content['SegStartTime'], "%Y-%m-%d %H:%M:%S")
            tt = dt.timestamp()
        else:
            dt = datetime.strptime(
                target_content['date']+' '+target_content['time'], "%Y/%m/%d %H:%M:%S")
            tt = dt.timestamp()
        for index, i in enumerate(range(0, 66, 6)):
            tstr = datetime.fromtimestamp(tt+i).strftime('%H:%M:%S')
            tstrLen = self.report.get_string_width(tstr)
            self.report.dText(self.pageWidth_mx+(self.rowWidth)-(self.cellW)+(index*eUnit*5)-(tstrLen/2),
                              start_height_pre+(self.cellW*18), tstr, self.fontFamily, 5)
        

        # print(target_content['HeartRateArray'])
        #cleaned data
        for i in range(1, len(target_content['HeartRateArray'])):
            if int(target_content['HeartRateArray'][i]) == -1 and int(target_content['HeartRateArray'][i-1]) != -1:
                target_content['HeartRateArray'][i] = target_content['HeartRateArray'][i-1]
        # print(target_content['HeartRateArray'])
        
        __min = 1000
        for i in target_content['HeartRateArray']:
            if int(i) != -1 and int(i) < __min:
                __min = int(i)
                
            
        # y-axis label
        self.report.dText(start_x-7, start_y, "{}bpm".format(int(max(target_content['HeartRateArray']))), self.fontFamily, 6)
        self.report.dText(start_x-7, end_y, "{}bpm".format(__min), self.fontFamily, 6)
        
        
        # hrv data
        x_space = delta_x/60
        # cause reverse so minus
        # nor_list = [(end_y) - (x - min(target_content['HeartRateArray']))/(max(target_content['HeartRateArray']) -
        #                                                             min(target_content['HeartRateArray'])) * (end_y-start_y) for x in target_content['HeartRateArray']]
        nor_list = [(end_y) - (x - __min)/(max(target_content['HeartRateArray']) -
                                                                    __min) * (end_y-start_y) for x in target_content['HeartRateArray']]        

        # print(nor_list)
        
        self.report.sColors(drawColor=self.drak_blue)
        for i in range(0, len(target_content['HeartRateArray'])):
            if nor_list[i]!= nor_list[0]:
                if i ==len(target_content['HeartRateArray'])-1:
                    self.report.dLine(start_x, nor_list[i], start_x+x_space, nor_list[i], 0.15)
                else:
                    self.report.dLine(start_x, nor_list[i], start_x+x_space, nor_list[i+1], 0.15)
            start_x += x_space








        """
        breath part
        """

        start_x = self.pageWidth_mx+(self.rowWidth)-(self.cellW)
        end_x = start_x + (delta_x)
        start_y = start_height+(self.cellW*7)
        end_y = start_y+delta_y
        self.report.sColors()
        self.report.dText(self.pageWidth_mx + self.rowWidth*6,
                          start_height+(self.cellW*6.5), fig_title, self.fontFamily, 6)
        self.report.dRect(start_x,
                          start_y, delta_x, delta_y, 0.15, 'D')

        # x-axis time label
        self.report.set_font(self.fontFamily, size=5)
        if title != "最小呼吸速率":
            dt = datetime.strptime(
                target_content['SegStartTime'], "%Y-%m-%d %H:%M:%S")
            tt = dt.timestamp()
        else:
            dt = datetime.strptime(
                target_content['date']+' '+target_content['time'], "%Y/%m/%d %H:%M:%S")
            tt = dt.timestamp()
        for index, i in enumerate(range(0, 66, 6)):
            tstr = datetime.fromtimestamp(tt+i).strftime('%H:%M:%S')
            tstrLen = self.report.get_string_width(tstr)
            self.report.dText(self.pageWidth_mx+(self.rowWidth)-(self.cellW)+(index*eUnit*5)-(tstrLen/2),
                              start_height+(self.cellW*19), tstr, self.fontFamily, 5)

        # breaths data
        x_space = delta_x/3000
        # cause reverse so minus
        nor_list = [(end_y) - (x - min(target_content['signals']))/(max(target_content['signals']) -
                                                                    min(target_content['signals'])) * (end_y-start_y) for x in target_content['signals']]
        self.report.sColors(drawColor=self.drak_blue)
        for i in range(0, len(target_content['signals'])-1):
            self.report.dLine(
                start_x, nor_list[i], start_x+x_space, nor_list[i+1], 0.15)
            start_x += x_space

        eWidth = 0.07*2499
        # little圖

        lastEWidth = eWidth
        espace = 0.0229
        eWidth = espace*7499
        eHeight = eWidth/150*6
        eUnit = eHeight/6
        self.report.dText(self.pageWidth_mx, start_height +
                          (self.cellW*23)+(eHeight/2), "180 SEC", self.fontFamily, 6)
        # 外框
        self.report.sColors()
        self.report.dRect(self.pageWidth_mx+(self.rowWidth)-(self.cellW),
                          start_height+(self.cellW*23), lastEWidth, eHeight, 0.15)
        # 陰影
        dummySpace = (lastEWidth-eWidth)/2
        self.report.sColors(fillColor=self.lightGrey)
        self.report.dRect(self.pageWidth_mx+(self.rowWidth)-(self.cellW),
                          start_height+(self.cellW*23), dummySpace, eHeight, style='F')
        self.report.dRect(self.pageWidth_mx+(self.rowWidth)-(self.cellW)+dummySpace+(
            espace*2500), start_height+(self.cellW*23), espace*2500, eHeight, style='F')
        self.report.dRect(self.pageWidth_mx+(self.rowWidth)-(self.cellW)+lastEWidth -
                          dummySpace, start_height+(self.cellW*23), dummySpace, eHeight, style='F')

        # LongSignals
        start_x = self.pageWidth_mx+(self.rowWidth)-(self.cellW)+dummySpace
        end_x = self.pageWidth_mx+(self.rowWidth) - \
            (self.cellW)+lastEWidth - dummySpace
        delta_x = end_x - start_x
        start_y = start_height+(self.cellW*23)
        end_y = start_height+(self.cellW*23) + eHeight

        x_space = delta_x/9000
        # cause reverse so minus
        nor_list = [(end_y) - (x - min(target_content['LongSignals']))/(max(target_content['LongSignals']) -
                                                                        min(target_content['LongSignals'])) * (end_y-start_y) for x in target_content['LongSignals']]

        for i in range(0, len(target_content['LongSignals'])-1):
            if nor_list[i] == nor_list[i+1] == start_y or nor_list[i] == nor_list[i+1] == end_y:
                self.report.sColors(drawColor=self.black)
                self.report.dLine(
                    start_x, nor_list[i], start_x+x_space, nor_list[i], 0.15)
            else:
                self.report.sColors(drawColor=self.drak_blue)
                self.report.dLine(
                    start_x, nor_list[i], start_x+x_space, nor_list[i+1], 0.15)
            start_x += x_space

    def __addDriven(self, startGridX, endGridX, y='') -> None:
        # 分割線
        if(y == ''):
            y = self.y
        self.report.sColors()
        self.report.dLine(startGridX, y, endGridX, y, 0.3)
        pass
