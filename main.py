import os
from flexx import flx
from components.analyzer import Analyzer
from components.usage import Usage
from lib.pdf_content import PDFContent
from lib.easy_qt import EasyQt
from lib.utils import get_screen_size, get_central_pos



class Main(flx.PyWidget):

  def init(self):
    self.qt = EasyQt()
    with flx.VBox():
      with flx.HBox(style='background:#f8f8f8;', flex=1):
        with flx.VBox(flex=1):
          self.open = flx.Button(text='Open')
          self.save = flx.Button(text='Save')
          self.usage = flx.Button(text='Usage')
          flx.Widget(flex=1)
        with flx.TabLayout(flex=9) as self.tab:
          with flx.VBox(title='pypdf', style='background:#3870a1;'):
            flx.Label(text="watermark text (keyword):", style='color:#ffd241;text-align:center;font-weight:bold;')
            self.wmtext1 = flx.MultiLineEdit(flex=1)
            with flx.HBox():
              self.rm1 = flx.Button(text='Remove', flex=1)
              self.analyzer = flx.Button(text='Analyzer', flex=1)
          with flx.VBox(title='mupdf', style='background:#ffd241;'):
            flx.Label(text="watermark text:", style='color:#3870a1;text-align:center;font-weight:bold;')
            self.wmtext2 = flx.MultiLineEdit(flex=1)
            with flx.HBox():
              self.rm2 = flx.Button(text='Remove', flex=1)
            flx.Widget(style='background:#eabd2d;max-height:5px;min-height:5px;')
            flx.Label(text="hyperlinks:", style='color:#3870a1;text-align:center;font-weight:bold;')
            self.links = flx.MultiLineEdit(flex=1)
            with flx.HBox():
              self.rm3 = flx.Button(text='Remove Link', flex=1)
              self.cbox = flx.CheckBox()
              with flx.Widget(style='color:#75aa10;font-size:13px;font-weight:bold;'):
                flx.Label(text="Also remove text?", style="margin-top:5px;")
              flx.Widget(flex=0.1, style='max-width:15px;min-width:15px;')
      with flx.Widget():
        with flx.HBox(style="border:3px solid red;color:gray;font-size:12px;"):
          flx.Widget(flex=1)
          flx.Label(text="Status:", style='font-weight:bold;')
          self.status = flx.Label(text="no file.")
          flx.Widget(flex=1)
    self.pdf_file = None

  def check_pdf_file_exist(self):
    if self.pdf_file is None:
      return False
    return True

  def process_input_data(self, data):
    data_list = list(set(data.split('\n')))
    for data in data_list:
      if data.strip() == "":
        data_list.remove(data)
    return data_list

  @flx.action
  def set_status_ready(self):
    fname = os.path.basename(self.pdf_file.path)
    fname = f"{fname[:31]}..." if len(fname) > 35 else fname
    self.status.set_text(f"[{fname}] is ready.")

  @flx.action
  def open_pdf(self, path):
    try:
      pdf_file = PDFContent(path)
      self.pdf_file = pdf_file
      self.set_status_ready()
    except Exception as error:
      msg = f"<b style='color:mediumblue'>{error}</b>"
      width, height = (350, 100)
      pos_x, pos_y = get_central_pos((width, height), get_screen_size())
      self.qt.msg_box(msg, (width, height), (pos_x, pos_y), True)

  @flx.action
  def save_pdf(self, path):
    self.status.set_text("saving")
    with open(path, "wb") as f:
      f.write(self.pdf_file.stream.getbuffer())
    self.set_status_ready()

  @flx.reaction('open.pointer_click')
  def open_clicked(self, *events):
    width, height = (650, 425)
    pos_x, pos_y = get_central_pos((width, height), get_screen_size())
    filename = self.qt.file_box((width, height), (pos_x, pos_y), "PDF Files (*.pdf)", True)
    if filename and os.path.exists(filename):
      self.open_pdf(filename)

  @flx.reaction('save.pointer_click')
  def save_clicked(self, *events):
    if not self.check_pdf_file_exist():
      return
    width, height = (650, 425)
    pos_x, pos_y = get_central_pos((width, height), get_screen_size())
    filename = self.qt.file_box((width, height), (pos_x, pos_y), "PDF Files (*.pdf)", True, True)
    if filename and not os.path.basename(filename).lower().endswith('.pdf'):
      count = 1
      filename_temp = filename + '.pdf'
      while filename_temp and os.path.exists(filename_temp):
        filename_temp = f"{filename}_{count}.pdf"
        count += 1
      filename = filename_temp
    if filename:
      self.save_pdf(filename)

  @flx.reaction('usage.pointer_click')
  def usage_clicked(self, *events):
    window_size = (500, 500)
    window_pos = (round((screen_width - window_size[0]) / 2), round((screen_height - window_size[1]) / 2))
    app = flx.App(Usage)
    app.launch('app', title="Instructions for use", icon="icon.png", size=window_size, pos=window_pos)

  @flx.reaction('rm1.pointer_click')
  def pypdf_watermark_remove_clicked(self, *events):
    if not self.check_pdf_file_exist():
      return
    text_list = self.process_input_data(self.wmtext1.text)
    self.status.set_text("removing watermark text...")
    self.pdf_file.remove_watermark_pypdf(text_list)
    msg = f'<b style="color:mediumseagreen">Completed!</b>'
    width, height = (200, 100)
    pos_x, pos_y = get_central_pos((width, height), get_screen_size())
    self.qt.msg_box(msg, (width, height), (pos_x, pos_y), True)
    self.set_status_ready()

  @flx.reaction('rm2.pointer_click')
  def mupdf_watermark_remove_clicked(self, *events):
    if not self.check_pdf_file_exist():
      return
    text_list = self.process_input_data(self.wmtext2.text)
    self.status.set_text("removing watermark text...")
    self.pdf_file.remove_watermark_mupdf(text_list)
    msg = f'<b style="color:mediumseagreen">Completed!</b>'
    width, height = (200, 100)
    pos_x, pos_y = get_central_pos((width, height), get_screen_size())
    self.qt.msg_box(msg, (width, height), (pos_x, pos_y), True)
    self.set_status_ready()

  @flx.reaction('rm3.pointer_click')
  def mupdf_link_remove_clicked(self, *events):
    if not self.check_pdf_file_exist():
      return
    link_list = self.process_input_data(self.links.text)
    also_watermark = False
    if self.cbox.checked:
      also_watermark = True
    self.status.set_text("removing links...")
    self.pdf_file.remove_link(link_list, also_watermark)
    msg = f'<b style="color:mediumseagreen">Completed!</b>'
    width, height = (200, 100)
    pos_x, pos_y = get_central_pos((width, height), get_screen_size())
    self.qt.msg_box(msg, (width, height), (pos_x, pos_y), True)
    self.set_status_ready()

  @flx.reaction('analyzer.pointer_click')
  def analyzer_clicked(self, *events):
    if not self.check_pdf_file_exist():
      return
    screen_width, screen_height = get_screen_size()
    window_size = (400, 680)
    window_pos = (round((screen_width - window_size[0]) / 2), round((screen_height - window_size[1]) / 2))
    app = flx.App(Analyzer, self.pdf_file)
    app.launch('app', title="PDF Watermark Analyzer", icon="icon.png", size=window_size, pos=window_pos)


if __name__ == '__main__':
  abspath = os.path.abspath(__file__)
  os.chdir(os.path.dirname(abspath))
  screen_width, screen_height = get_screen_size()
  window_size = (550, 350)
  window_pos = (round((screen_width - window_size[0]) / 2), round((screen_height - window_size[1]) / 2))
  
  app = flx.App(Main)
  # app.launch('chrome', title="PDF Watermark Remover", icon="icon.png")
  app.launch('app', title="PDF Watermark Remover", icon="icon.png", size=window_size, pos=window_pos)
  flx.run()