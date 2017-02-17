from html.parser import HTMLParser

class PageParser(HTMLParser):
  '''
  This is an HTML parser! All of the hard work is done by the superclass
  (which is a Python built-in). This class puts the HTML into a hierarchy
  that's (hopefully) easier to work with than raw string parsing.
  '''

  @staticmethod
  def parse(html):
    parser = PageParser()
    parser.feed(html)
    return parser.get_root_node()

  @staticmethod
  def banlist():
    '''Commonly unclosed tags'''
    return ('br', 'img', 'meta')

  @staticmethod
  def new_node(type):
    '''An empty node of the HTML tree'''
    return {'type': type, 'attrs': {}, 'nodes': [], 'data': ''}

  @staticmethod
  def filter_all(node, filters):
    '''Applies all filters'''
    for f in filters:
        node = PageParser.filter(node, *f)
    return node

  @staticmethod
  def filter(node, type, index=0):
    '''Finds a sub-node of the given type, specified by index'''
    i = 0
    for node in node['nodes']:
      if node['type'] == type:
        if i == index:
          return node
        i += 1
    return None

  def __init__(self):
    HTMLParser.__init__(self)
    self.root = PageParser.new_node(None)
    self.stack = [self.root]
    self.indent = 0

  def get_root_node(self):
    '''After parsing, returns the abstract root node (which contains the html node)'''
    return self.root

  def handle_starttag(self, tag, attrs):
    '''Inherited - called when a start tag is found'''
    if tag in PageParser.banlist():
        return
    element = PageParser.new_node(tag)
    for (k, v) in attrs:
        element['attrs'][k] = v
    self.stack[-1]['nodes'].append(element)
    self.stack.append(element)

  def handle_endtag(self, tag):
    '''Inherited - called when an end tag is found'''
    if tag in PageParser.banlist():
        return
    x = self.stack.pop()
    #if x['type'] != tag:
    #  print('Unclosed tag!  Parent/Child:', x['type'], tag)

  def handle_data(self, data):
    '''Inherited - called when a data string is found'''
    element = self.stack[-1]
    element['data'] += data
