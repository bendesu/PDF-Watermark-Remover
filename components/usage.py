from flexx import flx


class Usage(flx.PyWidget):

  def init(self):
    with flx.TabLayout(style='background:#f8f8f8;'):
      with flx.Widget(title='basis', style='background:white;color:black;'):
        UsageBasis(style="padding-left:5%;padding-right:5%;")
      with flx.Widget(title='pypdf', style='background:#3870a1;color:#ffd241;'):
        UsagePy(style="padding-left:5%;padding-right:5%;")
      with flx.Widget(title='mupdf', style='background:#ffd241;color:#3870a1;'):
        UsageMu(style="padding-left:5%;padding-right:5%;")
    

class UsageBasis(flx.Widget):

    def _create_dom(self):
      return flx.create_element('div')

    def _render_dom(self):
      text_1 = "The <b>PDF Watermark Remover</b> allows you to remove watermarks in text format. You " \
        "have two modes to choose from to remove the watermark: <b>pypdf</b> and <b>mupdf</b>."
      text_2 = "There isn't much difference between the two modes. However, if you want to remove " \
        "hyperlinks, only <b>mupdf</b> can do that. Moreover, <b>mupdf</b> may take up more space to " \
        "store the processed pdf file."
      text_3 = "Lastly, each text (watermarks, hyperlinks) input box allows multiple lines of input. " \
        "Each line of input will be text (watermarks, hyperlinks) that the program needs to remove in turn."

      text_1 = _process_text(text_1)
      text_2 = _process_text(text_2)
      text_3 = _process_text(text_3)

      return [
        flx.create_element('p', {}, text_1),
        flx.create_element('p', {}, text_2),
        flx.create_element('p', {}, text_3)
      ]

class UsagePy(flx.Widget):

    def _create_dom(self):
      return flx.create_element('div')

    def _render_dom(self):
      text_1 = "In the <b>pypdf</b> mode, the watermark text that can be removed may not be utf-8 encoded."
      text_2 = "Therefore, you should use <b>Analyzer</b> to check for potential watermarks (the text may " \
        "look different from within PDF viewers because the program may encode them using a different " \
        "encoding set), then copy-paste the potential watermark text back to the <b>watermark text " \
        "(keyword)</b> section."
      text_3 = "Fianlly, click the <b>Remove</b> button. After completion, you can save it to a local " \
        "file and view it"

      text_1 = _process_text(text_1)
      text_2 = _process_text(text_2)
      text_3 = _process_text(text_3)

      return [
        flx.create_element('p', {}, text_1),
        flx.create_element('p', {}, text_2),
        flx.create_element('p', {}, text_3)
      ]

class UsageMu(flx.Widget):

    def _create_dom(self):
      return flx.create_element('div')

    def _render_dom(self):
      text_1 = "In the <b>mupdf</b> mode, there are no encoding restrictions like <b>pypdf</b>, which means it " \
        "can remove watermarks you see in PDF viewers without having to use tools like <b>Analyzer</b> to help." 
      text_2 = "It should be noted that <b>mupdf</b> not only supports watermark removal, but also any other " \
        "type of text. Hence, when you cut off some text from the middle, the entire page of the pdf will be " \
        "rebuilt as a result, which may cause additional storage space to be required."
      text_3 = "Furthermore, if you want to remove hyperlinks, you can do so in this mode, and there is " \
        "also a checkbox where you can select to remove the text that accompanies those hyperlinks."

      text_1 = _process_text(text_1)
      text_2 = _process_text(text_2)
      text_3 = _process_text(text_3)

      return [
        flx.create_element('p', {}, text_1),
        flx.create_element('p', {}, text_2),
        flx.create_element('p', {}, text_3)
      ]

def _process_text(self, text):
  f_text = []
  temp_text = ""
  is_open = 0
  open_tag_name = ""
  open_tag_text = ""
  close_tag_name  = ""
  for char in text:
    if char == '<' and is_open == 0:
      is_open = 1
      f_text.append(temp_text)
      temp_text = ""
    elif char == '>' and is_open == 1:
      is_open = 2
    elif is_open == 1:
      open_tag_name += char
    elif char == '<' and is_open == 2:
      is_open = 3
    elif is_open == 2:
      open_tag_text += char
    elif char == '>' and is_open == 3:
      if open_tag_name == close_tag_name[1:]:
        f_text.append(flx.create_element(open_tag_name, {}, open_tag_text))
        is_open = 0
        open_tag_name = ""
        open_tag_text = ""
        close_tag_name = ""
      else:
        raise Exception(f'Open tag <{open_tag_name}> does not match close tag <{close_tag_name}>')
    elif is_open == 3:
      close_tag_name += char
    else:
      temp_text += char
  f_text.append(temp_text)
  return f_text