import io
import os
import fitz
from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.pdf import ContentStream
from PyPDF2.generic import TextStringObject, ArrayObject, TextStringObject, NameObject, EncodedStreamObject
from PyPDF2.utils import b_
from copy import deepcopy


class PDFContent:

  def __init__(self, path):
    with open(path, "rb") as f:
      self.stream = io.BytesIO(f.read())
      self.stream.seek(0)
      self.source = PdfFileReader(self.stream)
      self.pu_doc = fitz.open(stream=self.stream)
    if self.source.isEncrypted:
      raise Exception(f'\'{os.path.basename(path)}\' is encrypted.')
    self.path = path
    self.meta_producer = "PDF Watermark Remover"

  def remove_watermark_mupdf(self, text_list, update_stream=True):
    doc = fitz.open(stream=self.stream) # open from stream
    doc.set_metadata({})
    doc.set_metadata({
      'producer': self.meta_producer
    })
    for page in doc:
      for wm_text in text_list: # remove water marks
        rect = page.search_for(wm_text)
        for rect_t in rect:
          page.add_redact_annot(rect_t)
          page.apply_redactions() # remove the text
    
    if update_stream:
      self.stream = io.BytesIO()
      doc.save(self.stream)
      self.stream.seek(0)
      self.source = PdfFileReader(self.stream)
    return doc

  def remove_link(self, link_list, also_watermark=False, update_stream=True):
    doc = fitz.open(stream=self.stream) # open from stream
    doc.set_metadata({})
    doc.set_metadata({
      'producer': self.meta_producer
    })
    for page in doc:
      for link in page.links(kinds=(fitz.LINK_URI,)):  # iterate over internet links only
        for l_url in link_list:
          if l_url in link['uri']:
            page.delete_link(link)
            if also_watermark:
              page.add_redact_annot(link["from"])
              page.apply_redactions() # remove the text
    
    if update_stream:
      self.stream = io.BytesIO()
      doc.save(self.stream)
      self.stream.seek(0)
      self.source = PdfFileReader(self.stream)
    return doc

  def remove_watermark_pypdf(self, text_list, one_page_num_only=None, update_stream=True):
    self.stream.seek(0)
    source = PdfFileReader(self.stream)
    output = PdfFileWriter()
    range_space = range(0, self.get_num_pages())
    if one_page_num_only is not None:
      range_space = range(one_page_num_only, one_page_num_only + 1)

    for page_num in range_space:
      page = source.getPage(page_num)
      content_object = page["/Contents"]
      content_objs = self.process_contents_pypdf(page_num, source)

      for content_obj, c_text in content_objs:
        for wm_text in text_list:
          if wm_text in c_text and type(content_obj) is ArrayObject:
            content_object.remove(content_obj[0])
            break
          elif wm_text in c_text and type(content_object) is EncodedStreamObject and content_object == content_obj:
            content = ContentStream(content_object, source)
            for operands, operator in content.operations:
              if operator == b_("Tj") or operator == b_("TJ"):
                content.operations.remove((operands, operator))
            page[NameObject('/Contents')] = content
            break
      output.addPage(page)

    meta_hash = {
      '/Producer': self.meta_producer
    }
    output.addMetadata(meta_hash)
    if update_stream:
      self.stream = io.BytesIO()
      output.write(self.stream)
      self.stream.seek(0)
      self.source = PdfFileReader(self.stream)
    return output

  def process_contents_pypdf(self, page_num, source = None):
    _source = source
    if source is None:
      _source = self.source
    font_encodings, prev_font = self.get_font_encodings(page_num)
    page = _source.getPage(page_num)
    content_object = page["/Contents"]
    content_list = []
    for item_num in range(0, len(content_object)):
      content_obj = None
      if isinstance(content_object, ArrayObject):
        content_obj = ArrayObject(content_object)
      elif isinstance(content_object, EncodedStreamObject):
        content_obj = deepcopy(content_object)
      id = 0
      for i in range(0, len(content_object)):
        if i == item_num:
          id = 1
        else:
          del content_obj[id]
      content = ContentStream(content_obj, _source)
      c_text = ""
      for operands, operator in content.operations:
        # print(f"{operands, operator}")
        if operator == b_("Tf"):
          prev_font = operands[0][1:]
        elif operator == b_("Tj") or operator == b_("TJ"):
          plain_text = self.process_text(operands, operator, prev_font, font_encodings)
          if plain_text:
            c_text += plain_text
      content_list.append((content_obj, c_text))
    return content_list

  def extract_text_pypdf(self, page_num):
    source = self.source
    font_encodings, prev_font = self.get_font_encodings(page_num)
    page = source.getPage(page_num)
    content_object = page["/Contents"]
    text = ""
    content = ContentStream(content_object, source)
    for operands, operator in content.operations:
      # print(f"{operands, operator}")
      if operator == b_("Tf"):
        prev_font = operands[0][1:]
      elif operator == b_("Tj") or operator == b_("TJ"):
        plain_text = self.process_text(operands, operator, prev_font, font_encodings)
        if plain_text:
          text += plain_text
    return text

  def process_text(self, operands, operator, encoding_method, font_encodings):
    plain_text = None
    if operator == b_("Tj"):
      text = operands[0]
      if type(text) is TextStringObject:
        text = text.get_original_bytes()
      try:
        plain_text = text.decode(font_encodings[encoding_method])
      except:
        plain_text = None
      # print(f"{prev_font, plain_text, operator}")
    elif operator == b_("TJ"):
      texts = operands[0]
      texts_temp = []
      for i in range(0, len(texts)):
        if i % 2 == 0: # remove positional parameters
          texts_temp.append(texts[i])
      if len(texts_temp) > 0:
        plain_text = ""
      for text in texts_temp:
        if type(text) is TextStringObject:
          text = text.get_original_bytes()
        try:
          plain_text += text.decode(font_encodings[encoding_method])
        except:
          plain_text = None
      # print(f"{prev_font, len(texts), texts, operator}\n")
    return plain_text

  def get_font_encodings(self, page_num):
      default_encode = '_default'
      font_encodings = {
        default_encode: 'utf-8'
      }
      fonts = self.pu_doc.get_page_fonts(page_num)
      for font in fonts:
        font_tuple = font[-2:]
        font_encodings[font_tuple[0]] = self.cmap_loopup(font_tuple[1])
      return [font_encodings, default_encode]

  def get_num_pages(self):
    return self.source.getNumPages()

  @staticmethod
  def cmap_loopup(cmap_name):
    rs = 'utf-8'
    GBK_1 = [
      'Adobe-GB1-UCS2', 
      'Adobe-Japan1-UCS2',
      'Adobe-Korea1-UCS2',
      'GB-EUC-H',
      'GB-EUC-V'
    ]
    identity = [
      'Identity-H',
      'Identity-V'
    ]
    if cmap_name in GBK_1 or 'GBK' in cmap_name.upper():
      rs = 'gbk'
    elif cmap_name in identity: # will update to look for /ToUnicode table
      rs = 'utf-16'
    return rs