from operator import index
from warnings import filterwarnings
from fpdf import FPDF
import os
import os.path
from datetime import datetime
from numpy import irr


class PDF_Color():
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b


class PDF_A002V2(FPDF):

    # Page header
    def header(self):
        pass

    # Page footer
    def footer(self):
        pass

    def sColors(self, txtColor: PDF_Color = PDF_Color(0, 0, 0), drawColor: PDF_Color = PDF_Color(0, 0, 0), fillColor: PDF_Color = PDF_Color(255, 255, 255)):
        self.set_text_color(txtColor.r, txtColor.g, txtColor.b)
        self.set_draw_color(drawColor.r, drawColor.g, drawColor.b)
        self.set_fill_color(fillColor.r, fillColor.g, fillColor.b)

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
        self.set_xy(x, y)
        self.image(imagePath, w=w, h=h)


class A002V2():
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
        self.fontPath = os.path.join(
            pypath, "doc", "TaipeiSansTCBeta-Regular.ttf")  # 字型檔案位置
        self.logoPath = os.path.join(
            pypath, "doc", "SW-Logo.png")                   # logo 檔案位置
        self.maxHRDecPath = os.path.join(pypath, "doc", "hr_decrease.png")
        self.minHRPath = os.path.join(pypath, "doc", "hr_min.png")
        # self.poincarePath = os.path.join(pypath,"doc","Poincare_2022071113.jpg")
        self.pvcPath = os.path.join(pypath, "doc", "Poincare_PVC.png")
        self.persistAFPath = os.path.join(
            pypath, "doc", "Poincare_Persist_AF.png")
        self.paroxysmalAFPath = os.path.join(
            pypath, "doc", "Poincare_Paroxysmal_AF.png")
        self.flagPath = os.path.join(pypath, "doc", "flag.png")
        self.fontFamily = 'TaipeiSansTC'                              # 字型

        # 色彩
        self.black = PDF_Color(0, 0, 0)
        self.white = PDF_Color(255, 255, 255)
        self.lightGrey = PDF_Color(230, 230, 230)
        self.grey = PDF_Color(190, 190, 190)

        # grid 1~12 x軸位置
        # grid padding right
        self.grid_pr = 3
        self.gridWidth = (
            self.pageWidth - (self.pageWidth_mx*2)) / 12   # grid 每隔寬度
        self.grid1X = self.pageWidth_mx
        self.grid2X = self.grid1X + self.gridWidth
        self.grid3X = self.grid2X + self.gridWidth
        self.grid4X = self.grid3X + self.gridWidth
        self.grid5X = self.grid4X + self.gridWidth
        self.grid6X = self.grid5X + self.gridWidth
        self.grid7X = self.grid6X + self.gridWidth
        self.grid8X = self.grid7X + self.gridWidth
        self.grid9X = self.grid8X + self.gridWidth
        self.grid10X = self.grid9X + self.gridWidth
        self.grid11X = self.grid10X + self.gridWidth
        self.grid12X = self.grid11X + self.gridWidth

        # column
        ## 高 (一頁八欄)
        self.colHeight = (self.pageHeight - self.pageHeight_mt*2) / 8

        # 文字行高
        self.lineHeight = 4.5

        pass

    def genReport(self, json, file_name,locale:str, locale_data:dict, assign_poincare_path=None):
        self.locale = locale
        self.locale_data = locale_data
        if assign_poincare_path:
            json['poincare']['imagePath'] = assign_poincare_path 
        file=self.generateReport(json['header'], json['userInfo'], json['cardiovascularHealthReport'], json['notes'],
                            json['cardiovascularExamEvaluation'], json['poincare'], json['irregularHeartRateStatistics'], file_name)
        return file

    def generateReport(self, header, userInfo, healthReport, note, examEval, poincare, irregulars, file_name) -> None:
        # A4 (w:210 mm and h:297 mm)
        filterwarnings("ignore")

        # 繪製PDF
        self.report = PDF_A002V2(format='A4')
        self.report.add_font(self.fontFamily, '', self.fontPath, uni=True)
        self.header = header
        self.userInfo = userInfo
        self.__addHealthReport(healthReport)
        self.__addNote(note)
        self.__addExamEval(examEval)
        self.__addPoincare(poincare)
        for i in range(0, len(irregulars)):
            self.__addIrregular(irregulars[i])


        # 匯出PDF
        pypath = os.path.join(os.path.dirname(__file__),
                              '..', '..', 'user_pdf', 'A002V2')
        if not os.path.exists(pypath):
            os.makedirs(pypath)

        file = os.path.join(pypath, file_name)
        self.report.output(file, 'F')
        return file

    def __addPage(self) -> None:
        # y軸
        self.y = 0 + self.pageHeight_mt
        self.report.add_page()
        self.report.alias_nb_pages()
        if (self.report.page_no() == 1):
            self.__gen1PageHeader()
        else:
            self.__genHeader()
        self.__genFooter()
        pass

    def __gen1PageHeader(self) -> None:
        # 報告名稱、logo
        startHeight = self.pageHeight_mt
        cellHeightNo = 4
        self.report.dText(self.pageWidth_mx, startHeight+(self.cellW*1.5),
                          self.header['reportName'], self.fontFamily, 8)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*6),
                          startHeight+(self.cellW*1.5), self.locale_data['TestingPeriod'], self.fontFamily, 8)
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
                          (self.cellW*3), self.locale_data['Name']+':', self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx, startHeight +
                          (self.cellW*5), self.userInfo['name'], self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx, startHeight +
                          (self.cellW*9), self.locale_data['Birthday']+':', self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx, startHeight+(self.cellW*11),
                          self.userInfo['birthday'], self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*2),
                          startHeight+(self.cellW*3), self.locale_data['Age']+':', self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*2), startHeight +
                          (self.cellW*5), str(self.userInfo['age']), self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*2),
                          startHeight+(self.cellW*9), self.locale_data['Sex']+':', self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*2), startHeight +
                          (self.cellW*11), self.userInfo['gender'], self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*4),
                          startHeight+(self.cellW*3), self.locale_data['Height']+':', self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*4), startHeight +
                          (self.cellW*5), self.userInfo['height'], self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*4),
                          startHeight+(self.cellW*9), self.locale_data['Weight']+':', self.fontFamily, 7)
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
                         self.cellW, txt=self.locale_data['CardiovascularHealthReport'])
        self.report.text(self.pageWidth_mx+(self.rowWidth*4), startHeight +
                         self.cellW, txt=self.locale_data['ReportGenerationTime']+': '+self.header['reportDate'])
        self.report.text(self.pageWidth_mx+(self.rowWidth*8), startHeight +
                         self.cellW, txt=self.locale_data['TestingPeriod']+': '+self.header['testingPeriod'])
        pass

    def __genFooter(self) -> None:
        startHeight = self.pageHeight_mt+(self.cellW*140)
        self.__addDriven(self.pageWidth_mx, self.pageWidth_mx +
                         self.rowWidth*12, startHeight)
        self.report.set_font(self.fontFamily, size=7)
        self.report.text(self.pageWidth_mx, startHeight +
                         self.cellW*2, txt=self.locale_data['User']+': '+self.userInfo['name'])
        self.report.text(self.pageWidth_mx+(self.rowWidth*3),
                         startHeight+self.cellW*2, txt=self.locale_data['ReportType']+': A002V2')
        self.report.text(self.pageWidth_mx+(self.rowWidth*6), startHeight +
                         self.cellW*2, txt=self.locale_data['ReportGenerationTime']+': '+self.header['reportDate'])
        self.report.text(self.pageWidth_mx+(self.rowWidth*10), startHeight +
                         self.cellW*2, txt=self.locale_data['Page']+': '+str(self.report.page_no()))
        pass

    def __addHealthReport(self, healthReport) -> None:
        self.__addPage()
        startHeight = self.pageHeight_mt+(self.cellW*20)
        self.report.set_font(self.fontFamily, size=12)
        self.report.set_xy(self.pageWidth_mx, startHeight+self.cellW)
        self.report.cell(self.lineHeight, txt=self.locale_data['CardiovascularHealthEvaluate'])
        self.report.set_xy(self.pageWidth_mx +
                           (self.rowWidth*6), startHeight+self.cellW)
        self.report.cell(self.lineHeight, txt=str(
            healthReport['score'])+" / 100")
        self.report.set_xy(self.pageWidth_mx, startHeight+(self.cellW*4))
        self.report.cell(self.lineHeight, txt='CARDIOVASCULAR HEALTH')
        self.report.set_xy(self.pageWidth_mx, startHeight+(self.cellW*7))
        self.report.cell(self.lineHeight, txt='REPORT')

        self.report.set_font(self.fontFamily, size=7)
        self.report.set_xy(self.pageWidth_mx +
                           (self.rowWidth*6)-1, startHeight+(self.cellW*4))
        self.report.cell(self.lineHeight, txt="|")
        self.report.set_xy(self.pageWidth_mx+(self.rowWidth*6),
                           startHeight+(self.cellW*4))
        self.report.cell(self.rowWidth*2, txt=self.locale_data['Bad'], align='C')
        self.report.set_xy(self.pageWidth_mx +
                           (self.rowWidth*8)-1, startHeight+(self.cellW*4))
        self.report.cell(self.lineHeight, txt="|")
        self.report.set_xy(self.pageWidth_mx+(self.rowWidth*8),
                           startHeight+(self.cellW*4))
        self.report.cell(self.rowWidth*2, txt=self.locale_data['Good'], align='C')
        self.report.set_xy(self.pageWidth_mx+(self.rowWidth*10),
                           startHeight+(self.cellW*4))
        self.report.cell(self.lineHeight, txt="|")
        self.report.set_xy(self.pageWidth_mx+(self.rowWidth*10),
                           startHeight+(self.cellW*4))
        self.report.cell(self.rowWidth*2, txt=self.locale_data['Excellent'], align='C')
        self.report.set_xy(self.pageWidth_mx +
                           (self.rowWidth*12)-1, startHeight+(self.cellW*4))
        self.report.cell(self.lineHeight, txt="|")

        self.report.set_line_width(0.2)
        self.report.set_draw_color(230, 230, 230)
        self.report.set_fill_color(230, 230, 230)
        self.report.rect(self.pageWidth_mx+(self.rowWidth*6), startHeight +
                         (self.cellW*5.5), self.rowWidth*6+0.5, self.cellW*4, 'F')
        # scoreWidth = (self.rowWidth*6+0.5)*(healthReport['score']/100.0)
        scoreWidth = (self.rowWidth*6+0.5)*((healthReport['score']-50)/50.0)
        self.report.set_draw_color(0, 0, 0)
        self.report.set_fill_color(0, 0, 0)
        self.report.rect(self.pageWidth_mx+(self.rowWidth*6),
                         startHeight+(self.cellW*5.5), scoreWidth, self.cellW*4, 'F')

        stlen = len(healthReport['scoreText'])
        if stlen > 0:
            self.report.set_font(self.fontFamily, size=7)
            self.report.set_text_color(255, 255, 255)
            scoreTextWidth = self.report.get_string_width(
                healthReport['scoreText'])
            self.report.set_xy(self.pageWidth_mx+(self.rowWidth*6) +
                               scoreWidth-scoreTextWidth-4, startHeight+(self.cellW*7.5))
            self.report.cell(self.lineHeight, txt=healthReport['scoreText'])
            self.report.set_text_color(0, 0, 0)
        self.__addDriven(self.pageWidth_mx, self.pageWidth_mx +
                         self.rowWidth*12, startHeight+(self.cellW*12)) # 70

        # static
        staticReport = healthReport['staticHeartIndex']
        staticStartHeight = self.pageHeight_mt+(self.cellW*33)
        staticCellHeightNo = 22
        self.report.set_font(self.fontFamily, size=10)
        self.report.text(self.pageWidth_mx, staticStartHeight +
                         (self.cellW*2), self.locale_data['StaticHeartAssessment'])
        self.report.text(self.pageWidth_mx+(self.rowWidth*6),
                         staticStartHeight+(self.cellW*2), staticReport['scoreText'])
        self.report.set_font(self.fontFamily, size=7)
        descStr = staticReport['description']
        # descStr = "This method allows printing text with line breaks. They can be automatic (as soon as the text reaches the right border of the cell) or explicit (via the \n character). As many cells as necessary are output, one below the other. Text can be aligned, centered or justified. The cell block can be framed and the background painted."
        self.report.set_xy(self.pageWidth_mx, staticStartHeight+(self.cellW*4))
        self.report.multi_cell(w=self.rowWidth*5.5,
                               h=self.cellW*2, txt=descStr, align='L')
        
        # suggStr = "This method allows printing text with line breaks. They can be automatic (as soon as the text reache"
        suggStr = staticReport['evaluation']
        self.report.set_xy(self.pageWidth_mx+(self.rowWidth*6),staticStartHeight+(self.cellW*4))
        self.report.multi_cell(w=self.rowWidth*5.5,h=self.cellW*2, txt=suggStr, align='L')
        
        evalStr = staticReport['suggestion']
        # evalStr = "This method allows printing text with line breaks. They can be automatic (as soon as the text reache"
        self.report.set_xy(self.pageWidth_mx+(self.rowWidth*6),staticStartHeight+(self.cellW*16))
        self.report.multi_cell(w=self.rowWidth*5.5,h=self.cellW*2, txt=evalStr, align='L')
        
        # (234-70)/2=84
        func_index_start_height= startHeight+(self.cellW*12) +82
        
        self.__addDriven(self.pageWidth_mx, self.pageWidth_mx+self.rowWidth *
                         12, func_index_start_height)

        # index
        funcReport = healthReport['heartFunctionIndex']
        funcCellHeightNo = 20
        self.report.set_font(self.fontFamily, size=10)
        self.report.text(self.pageWidth_mx, func_index_start_height +
                         (self.cellW*3), self.locale_data['HeartFunction'])
        self.report.text(self.pageWidth_mx+(self.rowWidth*6),
                         func_index_start_height+(self.cellW*3), funcReport['scoreText'])
        self.report.set_font(self.fontFamily, size=7)
        descStr = funcReport['description']
        # descStr = "This method allows printing text with line breaks. They can be automatic (as soon as the text reaches the right border of the cell) or explicit (via the \n character). As many cells as necessary are output, one below the other. Text can be aligned, centered or justified. The cell block can be framed and the background painted."
        self.report.set_xy(self.pageWidth_mx, func_index_start_height+(self.cellW*5))
        self.report.multi_cell(w=self.rowWidth*5.5,h=self.cellW*2, txt=descStr, align='L')

        suggStr = funcReport['evaluation']
        # suggStr = "This method allows printing text with line breaks. They can be automatic (as soon as the text reache"
        self.report.set_xy(self.pageWidth_mx+(self.rowWidth*6),func_index_start_height+(self.cellW*5))
        self.report.multi_cell(w=self.rowWidth*5.5,h=self.cellW*2, txt=suggStr, align='L')

        evalStr = funcReport['suggestion']
        # evalStr = "This method allows printing text with line breaks. They can be automatic (as soon as the text reache"
        self.report.set_xy(self.pageWidth_mx+(self.rowWidth*6),func_index_start_height+(self.cellW*17))
        self.report.multi_cell(w=self.rowWidth*5.5,h=self.cellW*2, txt=evalStr, align='L')
        
        emptyCellHeightNo = 36
        pass

    def __addNote(self, note) -> None:
        startHeight = self.pageHeight_mt+(self.cellW*114)
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

    def __addExamEval(self, examEval) -> None:
        self.__addPage()
        startHeight = self.pageHeight_mt+(self.cellW*2)
        cellHeightNo = 6
        self.report.set_draw_color(0, 0, 0)
        self.report.set_fill_color(255, 255, 255)
        self.report.set_text_color(0, 0, 0)
        self.report.set_font(self.fontFamily, size=12)
        self.report.text(self.pageWidth_mx, startHeight +
                         (self.cellW*4), self.locale_data['CardiovascularHealthAnalysis'])
        self.__addDriven(self.pageWidth_mx, self.pageWidth_mx +
                         self.rowWidth*12, startHeight+(self.cellW*cellHeightNo))

        scoreRecord = examEval['scoreRecord']
        startHeight = self.pageHeight_mt+(self.cellW*8)
        cellHeightNo = 26
        self.report.set_font(self.fontFamily, size=10)
        self.report.text(self.pageWidth_mx, startHeight +
                         (self.cellW*3), self.locale_data['CardiovascularHealthScore'])
        self.report.set_font(self.fontFamily, size=7)
        descStr = scoreRecord['description']
        # descStr = "This method allows printing text with line breaks. They can be automatic (as soon as the text reache"

        self.report.set_xy(self.pageWidth_mx, startHeight+(self.cellW*5))
        self.report.multi_cell(w=self.rowWidth*3.8,
                               h=self.cellW*2, txt=descStr, align='L')

        startHeight = self.pageHeight_mt+(self.cellW*13)
        self.report.set_line_width(0.1)
        shift = 4.0
        self.report.line(self.pageWidth_mx+(self.rowWidth*shift), startHeight,
                         self.pageWidth_mx+(self.rowWidth*shift)+(self.cellW*2.5), startHeight)
        if self.locale == "tw":
            self.report.text(self.pageWidth_mx+(self.rowWidth*shift),
                            startHeight+(self.cellW*3), self.locale_data['Excellent'])
        elif self.locale == "en":
            self.report.text(self.pageWidth_mx+(self.rowWidth*3.8),
                startHeight+(self.cellW*3), self.locale_data['Excellent'])
            
        self.report.line(self.pageWidth_mx+(self.rowWidth*shift), startHeight+(self.cellW*6),
                         self.pageWidth_mx+(self.rowWidth*shift)+(self.cellW*2.5), startHeight+(self.cellW*6))
        self.report.text(self.pageWidth_mx+(self.rowWidth*shift),
                         startHeight+(self.cellW*9), self.locale_data['Good'])
        self.report.line(self.pageWidth_mx+(self.rowWidth*shift), startHeight+(self.cellW*12),
                         self.pageWidth_mx+(self.rowWidth*shift)+(self.cellW*2.5), startHeight+(self.cellW*12))
        self.report.text(self.pageWidth_mx+(self.rowWidth*shift),
                         startHeight+(self.cellW*15), self.locale_data['Bad'])
        self.report.line(self.pageWidth_mx+(self.rowWidth*shift), startHeight+(self.cellW*18),
                         self.pageWidth_mx+(self.rowWidth*shift)+(self.cellW*2.5), startHeight+(self.cellW*18))

        records = scoreRecord['records']
        recordLen = len(records)
        for i in range(0, 6):
            allWidth = 20
            space = 19.5
            self.report.set_fill_color(230, 230, 230)
            self.report.rect(self.pageWidth_mx+(self.rowWidth*4+8) +
                             (i*allWidth), startHeight, space, self.cellW*18, 'F')
            if (i < recordLen):
                self.report.set_font(self.fontFamily, size=6)
                reportName = records[i]['name']
                strLen = self.report.get_string_width(reportName)
                dateLen = self.report.get_string_width(records[i]['date'])
                self.report.text(self.pageWidth_mx+(self.rowWidth*4+8)+(i*allWidth)+(
                    space/2)-(strLen/2), startHeight+(self.cellW*19.5), reportName)
                self.report.text(self.pageWidth_mx+(self.rowWidth*4+8)+(i*allWidth)+(
                    space/2)-(dateLen/2), startHeight+(self.cellW*21), records[i]['date'])
                score = records[i]['score']
                # scoreXH = (100-score)*self.cellW*18/100
                scoreXH = (50-(score-50))*self.cellW*18/50
                self.report.set_fill_color(0, 0, 0)
                self.report.rect(self.pageWidth_mx+(self.rowWidth*4+8)+(i*allWidth),
                                 startHeight+scoreXH, space, self.cellW*18-scoreXH, 'F')
                scoreStr = str(int(score))
                scoreStrLen = self.report.get_string_width(scoreStr)
                self.report.set_text_color(255, 255, 255)
                self.report.text(self.pageWidth_mx+(self.rowWidth*4+8)+(i*allWidth)+(
                    space/2)-(scoreStrLen/2), startHeight+scoreXH+(self.cellW*1.5), scoreStr)
                self.report.set_text_color(0, 0, 0)
            else:
                self.report.set_font(self.fontFamily, size=6)
                reportName = "Report "+str(i+1)
                strLen = self.report.get_string_width(reportName)
                dateLen = self.report.get_string_width("----/--/--")
                self.report.text(self.pageWidth_mx+(self.rowWidth*4+8)+(i*allWidth)+(
                    space/2)-(strLen/2), startHeight+(self.cellW*19.5), reportName)
                self.report.text(self.pageWidth_mx+(self.rowWidth*4+8)+(i*allWidth)+(
                    space/2)-(dateLen/2), startHeight+(self.cellW*21), "----/--/--")
                
        self.__addDriven(self.pageWidth_mx, self.pageWidth_mx +
                         self.rowWidth*12, self.pageHeight_mt+(self.cellW*11)+(self.cellW*cellHeightNo))

        abnormalHeartRateStatistic = examEval['abnormalHeartRateStatistic']
        startHeight = self.pageHeight_mt+(self.cellW*37)
        cellHeightNo = 58
        self.report.set_font(self.fontFamily, size=10)
        self.report.text(self.pageWidth_mx, startHeight +
                         (self.cellW*3), self.locale_data['HeartRates/UsageTime/StatisticsofAbnormality'])
        self.report.set_font(self.fontFamily, size=7)
        self.report.text(self.pageWidth_mx, startHeight+(self.cellW*6),
                         self.locale_data['ReportGenerationTime']+": "+abnormalHeartRateStatistic['reportDate'])
        self.report.text(self.pageWidth_mx, startHeight+(self.cellW*8),
                         self.locale_data['Start']+": "+abnormalHeartRateStatistic['startDate'])
        self.report.text(self.pageWidth_mx, startHeight+(self.cellW*10),
                         self.locale_data['End']+": "+abnormalHeartRateStatistic['endDate'])
        self.report.text(self.pageWidth_mx+(self.rowWidth*3), startHeight +
                         (self.cellW*6), self.locale_data['MaxHeartRate']+": "+str(abnormalHeartRateStatistic['maxHR'])+' bpm')
        self.report.text(self.pageWidth_mx+(self.rowWidth*3), startHeight +
                         (self.cellW*8), self.locale_data['MinHeartRate']+": "+str(abnormalHeartRateStatistic['minHR'])+' bpm')
        self.report.text(self.pageWidth_mx+(self.rowWidth*5), startHeight+(self.cellW*6),
                         self.locale_data['MeanHeartRate']+": "+str(abnormalHeartRateStatistic['averageHR'])+' bpm')
        self.report.set_xy(self.pageWidth_mx+(self.rowWidth*10),
                           startHeight+(self.cellW*4.5))
        self.report.image(self.maxHRDecPath, h=4)
        self.report.set_xy(self.pageWidth_mx+(self.rowWidth*10),
                           startHeight+(self.cellW*6.5))
        self.report.image(self.minHRPath, h=4)
        self.report.text(self.pageWidth_mx+(self.rowWidth*10.3),
                         startHeight+(self.cellW*6), self.locale_data['MaxHeartRateDecrease'])
        self.report.text(self.pageWidth_mx+(self.rowWidth*10.3),
                         startHeight+(self.cellW*8), self.locale_data['MinHeartRate'])

        self.report.set_font(self.fontFamily, size=8)
        self.report.text(self.pageWidth_mx, startHeight+(self.cellW*15), self.locale_data['ECG'])
        self.report.set_font(self.fontFamily, size=7)
        self.report.text(self.pageWidth_mx, startHeight +
                         (self.cellW*17), "({})".format(self.locale_data['7DayStatistic']))
        self.report.set_font(self.fontFamily, size=8)
        self.report.text(self.pageWidth_mx, startHeight+(self.cellW*35), self.locale_data['Abnormal'])
        self.report.text(self.pageWidth_mx, startHeight+(self.cellW*37), self.locale_data['ECG'])
        self.report.set_font(self.fontFamily, size=7)
        self.report.text(self.pageWidth_mx, startHeight +
                         (self.cellW*39), "({})".format(self.locale_data['7DayStatistic']))

        hr7Ds = abnormalHeartRateStatistic['heartRate7Days']
        hrdNo = len(hr7Ds)
        maxNo = 0
        for i in range(0, hrdNo):
            irNo = hr7Ds[i]['irregular']['number']
            if (irNo > maxNo):
                maxNo = irNo
        indexArr = [[45, 36, 27, 18, 9], [90, 72, 54, 36, 18], [
            450, 360, 270, 180, 90], [900, 720, 540, 360, 180], [1350, 1080, 810, 540, 270]]
        indexId = -1
        for i in range(0, len(indexArr)):
            if (maxNo <= indexArr[i][0]):
                indexId = i
                break
        if (indexId == -1):
            indexId = len(indexArr)-1

        self.report.set_font(self.fontFamily, size=6)
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*13.5), "bpm")
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*15), "250")
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*18), "200")
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*21), "150")
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*24), "100")
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*27), "50")
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*30), "0")

        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*33.5), self.locale_data['Times'])
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*35), str(indexArr[indexId][0]))
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*38), str(indexArr[indexId][1]))
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*41), str(indexArr[indexId][2]))
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*44), str(indexArr[indexId][3]))
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*47), str(indexArr[indexId][4]))
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*50), "0")
        self.report.text(self.pageWidth_mx+(self.rowWidth*11.8),
                         startHeight+(self.cellW*33.5), self.locale_data['Hours'])
        self.report.text(self.pageWidth_mx+(self.rowWidth*11.8),
                         startHeight+(self.cellW*35), "24")
        self.report.text(self.pageWidth_mx+(self.rowWidth*11.8),
                         startHeight+(self.cellW*38.75), "18")
        self.report.text(self.pageWidth_mx+(self.rowWidth*11.8),
                         startHeight+(self.cellW*42.5), "12")
        self.report.text(self.pageWidth_mx+(self.rowWidth*11.8),
                         startHeight+(self.cellW*46.25), "6")
        self.report.text(self.pageWidth_mx+(self.rowWidth*11.8),
                         startHeight+(self.cellW*50), "0")
        if self.locale == "tw":
            self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                            startHeight+(self.cellW*53), self.locale_data['AbnormalRate'])
        elif self.locale == "en":
            self.report.text(self.pageWidth_mx+12,
                            startHeight+(self.cellW*53), self.locale_data['AbnormalRate'])
        self.report.set_line_width(0.09)
        self.report.set_draw_color(0, 0, 0)
        self.report.set_fill_color(255, 255, 255)
        self.report.rect(self.pageWidth_mx+(self.rowWidth*2.5), startHeight +
                         (self.cellW*14), (self.rowWidth*9), self.cellW*16, 'D')
        self.report.rect(self.pageWidth_mx+(self.rowWidth*2.5), startHeight +
                         (self.cellW*34), (self.rowWidth*9), self.cellW*16, 'D')
        self.report.set_line_width(0.10)
        self.report.set_draw_color(0, 0, 0)
        avgH = startHeight + \
            (self.cellW*14) + \
            ((250-abnormalHeartRateStatistic['averageHR'])*self.cellW*16/250)
        self.report.dashed_line(self.pageWidth_mx+(self.rowWidth*2.5),
                                avgH, self.pageWidth_mx+(self.rowWidth*11.5), avgH)

        #
        # tempHR7Ds = []
        # for i in range(0, len(hr7Ds)):
        #     if (hr7Ds[i]['evaluationTime']>0.0):
        #         tempHR7Ds.append(hr7Ds[i])
        # hr7Ds = tempHR7Ds
        hrHeight = startHeight+(self.cellW*14)
        ihrHeight = startHeight+(self.cellW*34)
        width = (self.rowWidth*9/7)
        startX = self.pageWidth_mx+(self.rowWidth*2.5)
        for i in range(0, 7):
            if (i > 0):
                self.report.set_draw_color(190, 190, 190)
                self.report.set_line_width(0.09)
                self.report.line(startX+(i*width), startHeight+(self.cellW*14),
                                 startX+(i*width), startHeight+(self.cellW*14)+self.cellW*16)
                self.report.line(startX+(i*width), startHeight+(self.cellW*34),
                                 startX+(i*width), startHeight+(self.cellW*34)+self.cellW*16)

            dstr = 'D'+str(i+1)
            dstrLen = self.report.get_string_width(dstr)
            self.report.text(startX+((i+0.5)*width)-(dstrLen/2),
                             startHeight+(self.cellW*13.5), dstr)

            if (i < hrdNo):
                hrRecap = hr7Ds[i]
                dstrLen = self.report.get_string_width(hrRecap['date'])
                self.report.text(startX+((i+0.5)*width)-(dstrLen/2),
                                 startHeight+(self.cellW*51.5), hrRecap['date'])
                irRateStr = str(hrRecap['irregular']['rate'])+'{}/hr'.format(self.locale_data['Times'])
                dstrLen = self.report.get_string_width(irRateStr)
                self.report.text(startX+((i+0.5)*width)-(dstrLen/2),
                                 startHeight+(self.cellW*53), irRateStr)

                maxH = startHeight+(self.cellW*14) + \
                    ((250-hrRecap['max'])*self.cellW*16/250)
                minH = startHeight+(self.cellW*14) + \
                    ((250-hrRecap['min'])*self.cellW*16/250)
                avgH = startHeight+(self.cellW*14) + \
                    ((250-hrRecap['average'])*self.cellW*16/250)
                self.report.set_fill_color(230, 230, 230)
                self.report.rect(startX+((i+0.5)*width)-2,
                                 maxH, 4, (minH-maxH), 'F')
                self.report.set_draw_color(0, 0, 0)
                self.report.set_fill_color(0, 0, 0)
                self.report.line(startX+((i+0.5)*width)-3, avgH,
                                 startX+((i+0.5)*width)+3, avgH)
                self.report.ellipse(
                    startX+((i+0.5)*width)-1, avgH-1, 2, 2, 'F')

                # Both image need to be shown
                if (hrRecap['maxDecrease'] == True and hrRecap['minHR'] == True):
                    self.report.set_xy(startX+((i+0.5)*width),
                                       startHeight+(self.cellW*31)+1)
                    self.report.image(self.maxHRDecPath, h=4)
                    self.report.set_xy(
                        startX+((i+0.5)*width)-4, startHeight+(self.cellW*31)-1)
                    self.report.image(self.minHRPath, h=4)
                elif (hrRecap['maxDecrease'] == True):
                    self.report.set_xy(
                        startX+((i+0.5)*width)-2, startHeight+(self.cellW*31))
                    self.report.image(self.maxHRDecPath, h=4)
                elif (hrRecap['minHR'] == True):
                    self.report.set_xy(
                        startX+((i+0.5)*width)-2, startHeight+(self.cellW*31))
                    self.report.image(self.minHRPath, h=4)

                et = hrRecap['evaluationTime']
                etStr = str(et)+'hrs'
                # etStrLen = self.report.get_string_width(etStr)
                # self.report.text(startX+((i+1)*width)-(etStrLen+1),
                #                  startHeight+(self.cellW*35.5), etStr)
                etH = startHeight+(self.cellW*34)+((24-et)*self.cellW*16/24)
                self.report.set_fill_color(230, 230, 230)
                self.report.rect(startX+(i*width), etH, width,
                                 startHeight+(self.cellW*50)-etH, 'F')
                irNo = hrRecap['irregular']['number']
                irNoStr = str(irNo)
                irNoH = startHeight + \
                    (self.cellW*34) + \
                    ((indexArr[indexId][0]-irNo) *
                     self.cellW*16/indexArr[indexId][0])
                self.report.set_fill_color(0, 0, 0)
                self.report.rect(startX+((i+0.5)*width)-2, irNoH,
                                 4, startHeight+(self.cellW*50)-irNoH, 'F')
                dstrLen = self.report.get_string_width(irNoStr)
                self.report.text(startX+((i+0.5)*width) -
                                 (dstrLen/2), irNoH-1, irNoStr)
                etStrLen = self.report.get_string_width(etStr)
                self.report.text(startX+((i+1)*width)-(etStrLen+1),
                                 startHeight+(self.cellW*35.5), etStr)
        pass

    def __addPoincare(self, poincare) -> None:
        self.__addPage()
        startHeight = self.pageHeight_mt+(self.cellW*2)
        cellHeightNo = 52
        self.report.set_font(self.fontFamily, size=10)
        self.report.text(self.pageWidth_mx, startHeight+(self.cellW*3), self.locale_data['PoincaréFig'])
        self.report.set_font(self.fontFamily, size=7)
        descStr = poincare['description']
        # descStr = "This method allows printing text with line breaks. They can be automatic (as soon as the text reache"
        self.report.set_xy(self.pageWidth_mx, startHeight+(self.cellW*5))
        self.report.multi_cell(
            w=self.rowWidth*5, h=self.cellW*2, txt=descStr, align='L')

        suggStr = poincare['suggestion']
        # suggStr = "This method allows printing text with line breaks. They can be automatic (as soon as the text reache"
        self.report.set_xy(self.pageWidth_mx, startHeight+(self.cellW*12))
        self.report.multi_cell(
            w=self.rowWidth*5, h=self.cellW*2, txt=suggStr, align='L')

        self.report.set_xy(self.pageWidth_mx+(self.rowWidth*6),
                           startHeight+(self.cellW*4))
        if (os.path.exists(poincare['imagePath'])):
            self.report.image(poincare['imagePath'], h=92)
        self.__addDriven(self.pageWidth_mx, self.pageWidth_mx +
                         self.rowWidth*12, startHeight+(self.cellW*cellHeightNo))

        startHeight = self.pageHeight_mt+(self.cellW*54)
        cellHeightNo = 40
        self.report.set_font(self.fontFamily, size=10)
        self.report.text(self.pageWidth_mx, startHeight+(self.cellW*3), self.locale_data['PoincaréFig'])
        self.report.set_font(self.fontFamily, size=8)
        title = self.locale_data['PVC']
        tLen = self.report.get_string_width(title)
        self.report.text(self.pageWidth_mx+(self.rowWidth*2) -
                         (tLen/2), startHeight+(self.cellW*7), title)
        self.report.set_font(self.fontFamily, size=7)
        desc = 'Premature Ventricular Comples'
        dLen = self.report.get_string_width(desc)
        self.report.text(self.pageWidth_mx+(self.rowWidth*2) -
                         (dLen/2), startHeight+(self.cellW*9), desc)
        self.report.set_font(self.fontFamily, size=8)
        title = self.locale_data['ContinueAF']
        tLen = self.report.get_string_width(title)
        self.report.text(self.pageWidth_mx+(self.rowWidth*6) -
                         (tLen/2), startHeight+(self.cellW*7), title)
        self.report.set_font(self.fontFamily, size=7)
        desc = 'Persist Atrial fibrillation'
        dLen = self.report.get_string_width(desc)
        self.report.text(self.pageWidth_mx+(self.rowWidth*6) -
                         (dLen/2), startHeight+(self.cellW*9), desc)
        self.report.set_font(self.fontFamily, size=8)
        title = self.locale_data['SometimesAF']
        tLen = self.report.get_string_width(title)
        self.report.text(self.pageWidth_mx+(self.rowWidth*10) -
                         (tLen/2), startHeight+(self.cellW*7), title)
        self.report.set_font(self.fontFamily, size=7)
        desc = 'Paroxysmal Atrial fibrillation'
        dLen = self.report.get_string_width(desc)
        self.report.text(self.pageWidth_mx+(self.rowWidth*10) -
                         (dLen/2), startHeight+(self.cellW*9), desc)
        self.report.set_xy(self.pageWidth_mx+self.cellW,
                           startHeight+(self.cellW*11))
        self.report.image(self.pvcPath, h=60)

        self.report.set_xy(self.pageWidth_mx+(self.rowWidth*4) +
                           self.cellW, startHeight+(self.cellW*11))
        self.report.image(self.persistAFPath, h=60)

        self.report.set_xy(self.pageWidth_mx+(self.rowWidth*8) +
                           self.cellW, startHeight+(self.cellW*11))
        self.report.image(self.paroxysmalAFPath, h=60)

        pass

    def __addIrregular(self, irregular) -> None:
        self.__addPage()
        startHeight = self.pageHeight_mt+(self.cellW*2)
        cellHeightNo = 6
        self.report.set_draw_color(0, 0, 0)
        self.report.set_fill_color(255, 255, 255)
        self.report.set_text_color(0, 0, 0)
        self.report.set_font(self.fontFamily, size=12)
        self.report.text(self.pageWidth_mx, startHeight +
                         (self.cellW*4), self.locale_data['AbnormalAnalysis'])
        self.__addDriven(self.pageWidth_mx, self.pageWidth_mx +
                         self.rowWidth*12, startHeight+(self.cellW*cellHeightNo))

        heartRate24Hours = irregular['heartRate24Hours']
        startHeight = self.pageHeight_mt+(self.cellW*8)
        cellHeightNo = 54
        self.report.set_font(self.fontFamily, size=7)
        self.report.text(self.pageWidth_mx, startHeight +
                         (self.cellW*4), irregular['date'])
        self.report.text(self.pageWidth_mx+(self.rowWidth*3), startHeight +
                         (self.cellW*3.5), self.locale_data['MaxHeartRate']+": "+str(irregular['maxHR'])+' bpm')
        self.report.text(self.pageWidth_mx+(self.rowWidth*3), startHeight +
                         (self.cellW*5.5), self.locale_data['MinHeartRate']+": "+str(irregular['minHR'])+' bpm')
        self.report.text(self.pageWidth_mx+(self.rowWidth*5), startHeight +
                         (self.cellW*3.5), self.locale_data['MeanHeartRate']+": "+str(irregular['averageHR'])+' bpm')
        self.report.set_xy(self.pageWidth_mx+(self.rowWidth*10),
                           startHeight+(self.cellW*2.0))
        self.report.image(self.maxHRDecPath, h=4)
        self.report.set_xy(self.pageWidth_mx+(self.rowWidth*10),
                           startHeight+(self.cellW*4))
        self.report.image(self.minHRPath, h=4)
        self.report.text(self.pageWidth_mx+(self.rowWidth*10.3),
                         startHeight+(self.cellW*3.5), self.locale_data['MaxHeartRateDecrease'])
        self.report.text(self.pageWidth_mx+(self.rowWidth*10.3),
                         startHeight+(self.cellW*5.5), self.locale_data['MinHeartRate'])

        self.report.set_font(self.fontFamily, size=8)
        self.report.text(self.pageWidth_mx, startHeight+(self.cellW*12), self.locale_data['ECG'])
        self.report.set_font(self.fontFamily, size=7)
        self.report.text(self.pageWidth_mx, startHeight +
                         (self.cellW*14), "({})".format(self.locale_data['24HoursStatistic']))
        self.report.set_font(self.fontFamily, size=8)
        self.report.text(self.pageWidth_mx, startHeight+(self.cellW*32), self.locale_data['Abnormal'])
        self.report.text(self.pageWidth_mx, startHeight+(self.cellW*34), self.locale_data['ECG'])
        self.report.set_font(self.fontFamily, size=7)
        self.report.text(self.pageWidth_mx, startHeight +
                         (self.cellW*36), "({})".format(self.locale_data['24HoursStatistic']))

        self.report.set_font(self.fontFamily, size=6)
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*10.5), "bpm")
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*12), "250")
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*15), "200")
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*18), "150")
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*21), "100")
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*24), "50")
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*27), "0")

        hrhNo = len(heartRate24Hours)
        maxNo = 0
        for i in range(0, hrhNo):
            irNo = heartRate24Hours[i]['irregular']['number']
            if (irNo > maxNo):
                maxNo = irNo
        indexArr = [[45, 36, 27, 18, 9], [90, 72, 54, 36, 18], [
            450, 360, 270, 180, 90], [900, 720, 540, 360, 180], [1350, 1080, 810, 540, 270]]
        indexId = -1
        for i in range(0, len(indexArr)):
            if (maxNo <= indexArr[i][0]):
                indexId = i
                break
        if (indexId == -1):
            indexId = len(indexArr)-1
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*30.5), self.locale_data['Times'])
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*32), str(indexArr[indexId][0]))
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*35), str(indexArr[indexId][1]))
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*38), str(indexArr[indexId][2]))
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*41), str(indexArr[indexId][3]))
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*44), str(indexArr[indexId][4]))
        self.report.text(self.pageWidth_mx+(self.rowWidth*2),
                         startHeight+(self.cellW*47), "0")
        self.report.text(self.pageWidth_mx+(self.rowWidth*11.8),
                         startHeight+(self.cellW*30.5), self.locale_data['Minutes'])
        self.report.text(self.pageWidth_mx+(self.rowWidth*11.8),
                         startHeight+(self.cellW*32), "60")
        self.report.text(self.pageWidth_mx+(self.rowWidth*11.8),
                         startHeight+(self.cellW*35.75), "45")
        self.report.text(self.pageWidth_mx+(self.rowWidth*11.8),
                         startHeight+(self.cellW*39.5), "30")
        self.report.text(self.pageWidth_mx+(self.rowWidth*11.8),
                         startHeight+(self.cellW*43.25), "15")
        self.report.text(self.pageWidth_mx+(self.rowWidth*11.8),
                         startHeight+(self.cellW*47), "0")
        if self.locale == "tw":
            self.report.text(self.pageWidth_mx+(self.rowWidth*1.8),
                            startHeight+(self.cellW*50), self.locale_data['AbnormalRate'])
        elif self.locale == "en":
            self.report.text(self.pageWidth_mx+12,
                            startHeight+(self.cellW*50), self.locale_data['AbnormalRate'])
        self.report.set_line_width(0.09)
        self.report.set_draw_color(0, 0, 0)
        self.report.set_fill_color(255, 255, 255)
        self.report.rect(self.pageWidth_mx+(self.rowWidth*2.5), startHeight +
                         (self.cellW*11), (self.rowWidth*9), self.cellW*16, 'D')
        self.report.rect(self.pageWidth_mx+(self.rowWidth*2.5), startHeight +
                         (self.cellW*31), (self.rowWidth*9), self.cellW*16, 'D')
        self.report.set_line_width(0.10)
        self.report.set_draw_color(0, 0, 0)
        avgH = startHeight+(self.cellW*11) + \
            ((250-irregular['averageHR'])*self.cellW*16/250)
        self.report.dashed_line(self.pageWidth_mx+(self.rowWidth*2.5),
                                avgH, self.pageWidth_mx+(self.rowWidth*11.5), avgH)

        hrHeight = startHeight+(self.cellW*10)
        ihrHeight = startHeight+(self.cellW*30)
        width = (self.rowWidth*9/24)
        startX = self.pageWidth_mx+(self.rowWidth*2.5)
        for i in range(0, 24):
            if (i > 0):
                self.report.set_draw_color(190, 190, 190)
                self.report.set_line_width(0.09)
                self.report.line(startX+(i*width), startHeight+(self.cellW*11),
                                 startX+(i*width), startHeight+(self.cellW*11)+self.cellW*16)
                self.report.line(startX+(i*width), startHeight+(self.cellW*31),
                                 startX+(i*width), startHeight+(self.cellW*31)+self.cellW*16)

                if (i % 6 == 0):
                    dstr = "{0:02d}".format(i)
                    # if (i == 12):
                    #     dstr = '中午'
                    dstrLen = self.report.get_string_width(dstr)
                    self.report.text(startX+(i*width)-(dstrLen/2),
                                     startHeight+(self.cellW*10.5), dstr)

            hstr = "{0:02d}".format(i)
            hstrLen = self.report.get_string_width(hstr)
            self.report.text(startX+((i+0.5)*width)-(hstrLen/2),
                             startHeight+(self.cellW*48.5), hstr)

            if (i < hrhNo):
                hrRecap = heartRate24Hours[i]
                irRateStr = str(round(hrRecap['irregular']['rate']*100))+'%'
                dstrLen = self.report.get_string_width(irRateStr)
                self.report.text(startX+((i+0.5)*width)-(dstrLen/2),
                                 startHeight+(self.cellW*50), irRateStr)

                # Both image need to be shown
                if (hrRecap['maxDecrease'] == True and hrRecap['minHR'] == True):
                    self.report.set_xy(
                        startX+((i+0.5)*width)-0.3, startHeight+(self.cellW*28)+1.2)
                    self.report.image(self.maxHRDecPath, h=3)
                    self.report.set_xy(
                        startX+((i+0.5)*width)-2.7, startHeight+(self.cellW*28)-1.2)
                    self.report.image(self.minHRPath, h=3)
                elif (hrRecap['maxDecrease'] == True):
                    self.report.set_xy(
                        startX+((i+0.5)*width)-1.5, startHeight+(self.cellW*28))
                    self.report.image(self.maxHRDecPath, h=3)
                elif (hrRecap['minHR'] == True):
                    self.report.set_xy(
                        startX+((i+0.5)*width)-1.5, startHeight+(self.cellW*28))
                    self.report.image(self.minHRPath, h=3)

                et = float(hrRecap['evaluationTime'])
                if (et > 0):
                    if (hrRecap['average'] > 0):
                        maxH = startHeight + \
                            (self.cellW*11) + \
                            ((250-hrRecap['max'])*self.cellW*16/250)
                        minH = startHeight + \
                            (self.cellW*11) + \
                            ((250-hrRecap['min'])*self.cellW*16/250)
                        avgH = startHeight + \
                            (self.cellW*11) + \
                            ((250-hrRecap['average'])*self.cellW*16/250)
                        self.report.set_fill_color(230, 230, 230)
                        self.report.rect(startX+((i+0.5)*width)-1,
                                         maxH, 2, (minH-maxH), 'F')
                        self.report.set_draw_color(0, 0, 0)
                        self.report.set_fill_color(0, 0, 0)
                        self.report.line(startX+((i+0.5)*width)-2,
                                         avgH, startX+((i+0.5)*width)+2, avgH)
                        self.report.ellipse(
                            startX+((i+0.5)*width)-0.6, avgH-0.6, 1.2, 1.2, 'F')
                    etm = round(et)
                    if etm < 60:
                        etmH = startHeight+(self.cellW*31) + \
                            ((60-etm)*self.cellW*16/60)
                        self.report.set_fill_color(230, 230, 230)
                        self.report.rect(
                            startX+(i*width), etmH, width, startHeight+(self.cellW*47)-etmH, 'F')
                        etmStr = str(etm)
                        etmStrLen = self.report.get_string_width(etmStr)
                        self.report.text(
                            startX+((i+1)*width)-(etmStrLen+0.5), startHeight+(self.cellW*32.5), etmStr)
                    elif etm >= 60:
                        etmH = startHeight+(self.cellW*31)
                        self.report.set_fill_color(230, 230, 230)
                        self.report.rect(
                            startX+(i*width), etmH, width, startHeight+(self.cellW*47)-etmH, 'F')
                    irNo = hrRecap['irregular']['number']
                    irNoStr = str(irNo)
                    irNoH = startHeight + \
                        (self.cellW*31) + \
                        ((indexArr[indexId][0]-irNo) *
                         self.cellW*16/indexArr[indexId][0])
                    self.report.set_fill_color(0, 0, 0)
                    self.report.rect(startX+((i+0.5)*width)-1, irNoH,
                                     2, startHeight+(self.cellW*47)-irNoH, 'F')
                    dstrLen = self.report.get_string_width(irNoStr)
                    self.report.text(startX+((i+0.5)*width) -
                                     (dstrLen/2), irNoH-1, irNoStr)
                else:
                    etmStr = '0'
                    etmStrLen = self.report.get_string_width(etmStr)
                    self.report.text(
                        startX+((i+1)*width)-(etmStrLen+0.5), startHeight+(self.cellW*32.5), etmStr)
        self.__addDriven(self.pageWidth_mx, self.pageWidth_mx +
                         self.rowWidth*12, startHeight+(self.cellW*cellHeightNo))

        # ecgs
        ecgs = irregular['ecgs']
        ecgsNo = len(ecgs)
        ecgHeight = 32
        if (ecgsNo >= 1):
            self.__addEcg(startHeight+(self.cellW*cellHeightNo),
                          ecgHeight, ecgs[0])

        if (ecgsNo >= 2):
            self.__addDriven(self.pageWidth_mx, self.pageWidth_mx+self.rowWidth *
                             12, startHeight+(self.cellW*(cellHeightNo+ecgHeight)))
            self.__addEcg(
                startHeight+(self.cellW*(cellHeightNo+ecgHeight)), ecgHeight, ecgs[1])

        if (ecgsNo > 2):
            extraPgNo = int((ecgsNo-2)/4)
            if ((ecgsNo-2) % 4 > 0):
                extraPgNo = extraPgNo+1
            for p in range(0, extraPgNo):
                self.__addPage()
                startHeight = self.pageHeight_mt+(self.cellW*2)
                ecgIdx = 2 + (p*4)
                for ei in range(0, 4):
                    ceIdx = ecgIdx+ei
                    if (ceIdx < ecgsNo):
                        if (ei > 0):
                            self.__addDriven(self.pageWidth_mx, self.pageWidth_mx +
                                             self.rowWidth*12, startHeight+(ei*self.cellW*ecgHeight))
                        self.__addEcg(
                            startHeight+(self.cellW*ecgHeight*ei), ecgHeight, ecgs[ceIdx])
        pass

    def __addEcg(self, startHeight, cellNoHeight, ecg):
        dt = datetime.strptime(
            ecg['date']+' '+ecg['time'], "%Y/%m/%d %H:%M:%S")
        tt = dt.timestamp()
        # ECG資料
        self.report.sColors()
        self.report.dText(self.pageWidth_mx, startHeight +
                          (self.cellW*3.5), ecg['date'], self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx, startHeight +
                          (self.cellW*5.5), ecg['time'], self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*2),
                          startHeight+(self.cellW*3.5), ecg['unit'], self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*4), startHeight +
                          (self.cellW*3.5), self.locale_data['HeartRate']+": "+str(ecg['HR'])+' bpm', self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*6), startHeight +
                          (self.cellW*3.5), "PR: "+str(ecg['PR'])+' ms', self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*6), startHeight +
                          (self.cellW*5.5), "QRS: "+str(ecg['QRS'])+' ms', self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*8), startHeight +
                          (self.cellW*3.5), "QT: "+str(ecg['QT'])+' ms', self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx+(self.rowWidth*8), startHeight +
                          (self.cellW*5.5), "QTc: "+str(ecg['QTc'])+' ms', self.fontFamily, 7)

        self.report.sColors(fillColor=self.black)
        self.report.dCircle(self.pageWidth_mx+(self.rowWidth*10)+1,
                            startHeight+(self.cellW*2)+1, 2, 0.1, 'F')
        self.report.dText(self.pageWidth_mx+(self.rowWidth*10.3),
                          startHeight+(self.cellW*3.5), "Irreqular", self.fontFamily, 7)
        self.report.dImage(self.pageWidth_mx+(self.rowWidth*10),
                           startHeight+(self.cellW*4.0), self.flagPath, w=4, h=4)
        self.report.sColors()
        self.report.dText(self.pageWidth_mx+(self.rowWidth*10.3),
                          startHeight+(self.cellW*5.5), "P", self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx, startHeight +
                          (self.cellW*11), "ECG", self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx, startHeight +
                          (self.cellW*13), "10 SEC", self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx, startHeight +
                          (self.cellW*26), "ECG", self.fontFamily, 7)
        self.report.dText(self.pageWidth_mx, startHeight +
                          (self.cellW*28), "30 SEC", self.fontFamily, 7)

        # 10秒 ECG
        espace = 0.07
        eWidth = 0.07*2499
        eHeight = eWidth/50*6
        eUnit = eHeight/6
        self.report.sColors()
        self.report.dRect(self.pageWidth_mx+(self.rowWidth)-(self.cellW),
                          startHeight+(self.cellW*10), eWidth, eHeight, 0.15, 'D')
        self.report.dRect(self.pageWidth_mx, startHeight +
                          (self.cellW*17), eUnit, eUnit, 0.15, 'D')
        self.report.dText(self.pageWidth_mx+eUnit+1, startHeight +
                          (self.cellW*17)+(eUnit/2)+1, "0.5mV", self.fontFamily, 5)
        self.report.dText(self.pageWidth_mx, startHeight +
                          (self.cellW*17)+eUnit+3, "200ms", self.fontFamily, 5)
        self.report.sColors(drawColor=self.lightGrey)
        for i in range(1, 6):
            self.report.dLine(self.pageWidth_mx+(self.rowWidth)-(self.cellW), startHeight+(self.cellW*10)+(i*eUnit),
                              self.pageWidth_mx+(self.rowWidth)-(self.cellW)+eWidth, startHeight+(self.cellW*10)+(i*eUnit), 0.09)
        for i in range(1, 50):
            self.report.dLine(self.pageWidth_mx+(self.rowWidth)-(self.cellW)+(i*eUnit), startHeight+(self.cellW*10),
                              self.pageWidth_mx+(self.rowWidth)-(self.cellW)+(i*eUnit), startHeight+(self.cellW*10)+eHeight, 0.09)
        self.report.set_font(self.fontFamily, size=5)
        for i in range(0, 11):
            tstr = datetime.fromtimestamp(tt+i).strftime('%H:%M:%S')
            tstrLen = self.report.get_string_width(tstr)
            self.report.dText(self.pageWidth_mx+(self.rowWidth)-(self.cellW)+(i*eUnit*5)-(
                tstrLen/2), startHeight+(self.cellW*22), tstr, self.fontFamily, 5)
        # Irrequlars
        irrs = ecg['Irrequlars']
        irrLen = len(irrs)
        self.report.sColors(fillColor=self.black)
        for i in range(0, irrLen):
            irrPos = irrs[i]
            self.report.dCircle(self.pageWidth_mx+(self.rowWidth)-(self.cellW) +
                                (irrPos*espace)-1, startHeight+(self.cellW*9)-1, 2, style='F')
        # PVCs
        pvcs = ecg['PVCs']
        pvcLen = len(pvcs)
        self.report.sColors()
        for i in range(0, pvcLen):
            pos = pvcs[i]
            self.report.dImage(self.pageWidth_mx+(self.rowWidth)-(self.cellW) +
                               (pos*espace)-1.5, startHeight+(self.cellW*7), self.flagPath, 3, 3)
            self.report.dLine(self.pageWidth_mx+(self.rowWidth)-(self.cellW)+(pos*espace), startHeight+(self.cellW*8),
                              self.pageWidth_mx+(self.rowWidth)-(self.cellW)+(pos*espace), startHeight+(self.cellW*10), 0.15)
        # ECGs
        yspace = eHeight/25
        sec10 = ecg['sec10']
        sec10Len = len(sec10)
        ecgY0 = startHeight+(self.cellW*10)+(yspace*15)
        ecgYStep = (yspace*10)/650
        self.report.sColors()
        preX = 0
        preY = 0
        for i in range(0, 2500):
            if (i < sec10Len):
                curX = self.pageWidth_mx + \
                    (self.rowWidth)-(self.cellW)+(espace*i)
                curY = ecgY0 - (sec10[i]*ecgYStep)
                if (i > 0):
                    self.report.dLine(preX, preY, curX, curY, 0.15)
                preX = curX
                preY = curY

        # 30秒 ECG圖形
        lastEWidth = eWidth
        espace = 0.0229
        eWidth = espace*7499
        eHeight = eWidth/150*6
        eUnit = eHeight/6
        # 外框
        self.report.sColors()
        self.report.dRect(self.pageWidth_mx+(self.rowWidth)-(self.cellW),
                          startHeight+(self.cellW*25), lastEWidth, eHeight, 0.15)
        # 陰影
        dummySpace = (lastEWidth-eWidth)/2
        self.report.sColors(fillColor=self.lightGrey)
        self.report.dRect(self.pageWidth_mx+(self.rowWidth)-(self.cellW),
                          startHeight+(self.cellW*25), dummySpace, eHeight, style='F')
        self.report.dRect(self.pageWidth_mx+(self.rowWidth)-(self.cellW)+lastEWidth -
                          dummySpace, startHeight+(self.cellW*25), dummySpace, eHeight, style='F')
        self.report.dRect(self.pageWidth_mx+(self.rowWidth)-(self.cellW)+dummySpace+(
            espace*2500), startHeight+(self.cellW*25), espace*2500, eHeight, style='F')
        # ECGs
        yspace = eHeight/25
        sec30 = ecg['sec30']
        sec30Len = len(sec30)
        ecgY0 = startHeight+(self.cellW*25)+(yspace*15)
        ecgYStep = (yspace*10)/650
        preX = 0
        preY = 0
        self.report.sColors()
        for i in range(0, 7500):
            if (i < sec30Len):
                curX = self.pageWidth_mx + \
                    (self.rowWidth)-(self.cellW)+dummySpace+(espace*i)
                curY = ecgY0 - (sec30[i]*ecgYStep)
                if (i > 0):
                    self.report.dLine(preX, preY, curX, curY, 0.15)
                preX = curX
                preY = curY
        pass

    def __addDriven(self, startGridX, endGridX, y='') -> None:
        # 分割線
        if(y == ''):
            y = self.y
        self.report.sColors()
        self.report.dLine(startGridX, y, endGridX, y, 0.3)
        pass
