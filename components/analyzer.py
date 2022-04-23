from flexx import flx


class Analyzer(flx.PyWidget):

  page_num = flx.IntProp(1, settable=True)

  def init(self, pdf_file):
    with flx.HBox(style='background:#f8f8f8;'):
      flx.Widget(flex=0.1, style="max-width:5px;min-width:5px;")
      with flx.VBox(flex = 1):
        with flx.HBox(style="border-bottom:3px solid lightgray;"):
          flx.Widget(flex=1)
          with flx.Widget(style="font-size:18px;font-weight:bold;"):
            flx.Label(text="Page number:", style="margin-top:6px;")
          self.page_num_edit = flx.LineEdit(text=str(self.page_num), flex=0.1, style='text-align:center;max-width:60px;min-width:60px;')
          with flx.Widget(style="font-size:13px;color:gray;"):
            flx.Label(text=f"Out of {pdf_file.get_num_pages()}", style="margin-top:10px;")
          flx.Widget(flex=1)
        with flx.Widget(style="text-align:center;"):
          flx.Label(text="Potential watermarks", style="font-size:18px;font-weight:bold;margin-top:3px;")
          flx.Label(text="(select one to view full text)", style="font-size:13px;color:gray;")
        with flx.Widget(flex = 1) as self.list_p:
          with flx.TreeWidget(max_selected = 1, style="background: white;") as self.list:
            self.show_contents(self.page_num - 1, pdf_file)
        with flx.Widget(style="text-align:center;"):
          flx.Label(text="watermark text", style="font-size:18px;font-weight:bold;")
          flx.Label(text="(copy the following and return)", style="font-size:13px;color:gray;")
        self.wmtext = flx.MultiLineEdit(flex=1)
        flx.Widget(flex=0.1, style="max-height:5px;min-height:5px;")
      flx.Widget(flex=0.1, style="max-width:5px;min-width:5px;")
      self.pdf_file = pdf_file
      self.prev_page_num = self.page_num

  def show_contents(self, page_num, pdf_file = None):
    if pdf_file is None:
      pdf_file = self.pdf_file
    
    content_list = self.process_content_list(pdf_file.process_contents_pypdf(page_num))
    for idx in range(0, len(content_list)):
      content = content_list[idx]
      content_obj, c_text = content
      text = c_text if len(c_text) < 21 else f"{c_text[:18]}..."
      text = f"{idx + 1}. [\"{text}\"]"
      p = flx.TreeItem(text=text, checked=None)
      p.reaction(self._reaction(content),'pointer_up')
      
  def process_content_list(self, content_list):
    for content in content_list:
      _, c_text = content
      if c_text.strip() == "":
        content_list.remove(content)
    return content_list

  @flx.action
  def change_content(self, content):
    content_obj, c_text = content
    self.wmtext.set_text(c_text)

  @flx.action
  def change_page(self, page_num):
    self.prev_page_num = page_num
    self.list.dispose()
    with flx.TreeWidget(max_selected = 1, style="background: white;", parent=self.list_p, flx_session=self.session) as self.list:
      self.show_contents(page_num - 1)
    self.wmtext.set_text("")

  @flx.reaction('page_num_edit.user_done')
  def page_num_changed(self, *events):
    if not self.page_num_edit.text.isnumeric():
      self.page_num_edit.set_text(str(self.prev_page_num))
      return
    page_num = int(self.page_num_edit.text)
    if page_num < 1 or page_num > self.pdf_file.get_num_pages():
      self.page_num_edit.set_text(str(self.prev_page_num))
      return
    self.change_page(page_num)

  def _reaction(self, content):
    def on_event(*events):
      self.change_content(content)
    return on_event