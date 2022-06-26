from backend import database
import matplotlib.pyplot as plt
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
import datetime
from io import BytesIO
from svglib.svglib import svg2rlg


def add_text_to_pdf_center(canvas, text, y):
    width, height = A4
    text_width = stringWidth(text, fontName='GOST', fontSize=14)
    pdf_text_object = canvas.beginText((width - text_width) / 2.0, y)
    pdf_text_object.textOut(text)


def add_text_to_pdf_left(canvas, text, x, y):
    pdf_text_object = canvas.beginText(x, y)
    pdf_text_object.textOut(text)


def report_all_sensors():
    pdfmetrics.registerFont(TTFont('GOST', 'backend\\GOST2304_TypeB.ttf'))

    db = database.SensorsBase()
    sensors_names, sensors_ids = db.list_all_sensors()
    now_date = datetime.datetime.now()
    for sensor_name, sensor_id in zip(sensors_names, sensors_ids):
        sensor = db.get_sensor_params(sensor_name, sensor_id)
        sensor = db.get_sensor_static_graph(sensor)
        x = np.array([point[0] for point in sensor.history])
        y = np.array([point[1] for point in sensor.history])
        std_y = np.array([point[2] for point in sensor.history])
        lower_y = y - 3.0 * std_y
        upper_y = y + 3.0 * std_y
        print(lower_y, upper_y)
        plt.figure(dpi=600)
        fig = plt.gcf()
        fig.set_size_inches(160 / 25.4, 120 / 25.4)
        plt.tick_params(top='off', right='off')
        plt.grid(True, linewidth=0.5, color='gray', linestyle='-')
        plt.plot(x, y, linewidth=1, color='black')
        plt.xlabel('Угловая скорость, °/с')
        plt.ylabel('Выходной сигнал, В')
        plt.fill_between(x, lower_y, upper_y, facecolor='lightgray')

        imgdata = BytesIO()
        plt.savefig(imgdata, format='svg')
        imgdata.seek(0)
        drawing = svg2rlg(imgdata)

        pdf_canvas = canvas.Canvas('sensor_{}_serial_{}.pdf'.format(sensor_name, sensor_id), pagesize=A4)
        width, height = A4
        pdf_canvas.setLineWidth(3)
        pdf_canvas.setFont('GOST', size=14)

        #renderPDF.draw(drawing, pdf_canvas, (width - 160 / 25.4 * 72) / 2, 50)

        pdf_canvas.drawCentredString(width / 2, 20, '{}.{}.{}'.format(now_date.day, now_date.month, now_date.year))
        pdf_canvas.drawCentredString(width / 2, 40, 'Лаборатория Микроприборов')
        pdf_canvas.line(width / 2 - 150, 33, width / 2 + 150, 33)
        pdf_canvas.line(width / 2 - 160, 35, width / 2 + 160, 35)

        pdf_canvas.drawCentredString(width / 2, 755, 'Паспорт датчика {}'.format(sensor_name))
        pdf_canvas.drawCentredString(width / 2, 740, 'серийный номер {}'.format(sensor_id))
        pdf_canvas.line(width / 2 - 240, 732, width / 2 + 240, 732)
        pdf_canvas.line(width / 2 - 230, 730, width / 2 + 230, 730)

        pdf_canvas.drawString(75, 650, 'Масштабный коэффициент:')
        pdf_canvas.drawString(350, 650, '{:0.3f}мВ/(°/с)'.format(sensor.scale))

        pdf_canvas.drawString(75, 625, 'Смещение нуля:')
        pdf_canvas.drawString(350, 625, '{:0.2f}°/с'.format(sensor.bias))

        pdf_canvas.drawString(75, 600, 'Нелинейность:')
        pdf_canvas.drawString(350, 600, '{:0.2f}%'.format(sensor.nonlin))

        pdf_canvas.drawString(75, 575, 'Полоса пропускания:')
        pdf_canvas.drawString(350, 575, '{:0.1f}Гц'.format(sensor.bandwidth))

        pdf_canvas.save()
    del db


if __name__ == '__main__':
    pass
