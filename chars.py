#!/usr/bin/env python


import json
from bs4 import BeautifulSoup

# Source of W3Cs list of entities, stored locally.
CHAR_HTML = 'dat/chars.html'
CHAR_JSON = 'dat/chars.json'
CHAR_LESS = 'dat/chars.less'


def gen_dict():
  """ Generate dict from original w3c file. """

  def parse_tr(tr):
    data = {}
    data['title']     = ' '.join(tr['title'].split()[1:])
    data['codepoint'] = tr['title'].split()[0][2:]
    data['block']     = tr['data-block']
    data['category']  = tr['data-category']
    data['sets']      = tr['data-set'].split()
    data['entities']  = tr.code.text.split()
    return data

  charlist = []

  # Load lxml tree.
  with open(CHAR_HTML) as chars:
    soup = BeautifulSoup(chars.read())
    for tr in soup.find_all('tr'):
      charlist.append(parse_tr(tr))

  return [parse_tr(tr) for tr in soup.find_all('tr')]


def gen_less(chars):
  """ Generate less variable table.

    Example:
      @html_yen   = "\000a5";
      @html_grave = "\00060";
  """

  def rzpad(s):
    """ pad unicode code points to 8 chars.
      e.g. 000a0 -> 000000a0
    """
    return '0' * (8 - len(s)) + s

  # Scan entities for max field length
  max_entity= lambda c: len(max(c['entities']))
  chars.sort(key=max_entity)
  name_field_width = max_entity(chars[-1]) + 3

  prefix = 'html_'

  lines = []
  for char in chars:
    for entity in char['entities']:

      # format string with field width.
      fmt = '@%%-%ds' % name_field_width

      # &nbsp; -> html_nbsp
      entity = prefix + entity[1:-1]

      codepoint = rzpad(char['codepoint'])

      line = ' '.join([fmt % entity, '=', '"\\%s";' % codepoint])

      glyph = (r'\U' + codepoint).decode('unicode-escape')

      lines.append(unicode(line) + r' \\ ' + glyph)


  return '\n'.join(line.encode('utf-8') for line in
      sorted(lines, key=lambda x: x.lower()))

chars = gen_dict()

with open(CHAR_JSON, 'wb') as f:
  f.write(json.dumps(chars))

with open(CHAR_LESS, 'wb') as f:
  f.write(gen_less(chars))
