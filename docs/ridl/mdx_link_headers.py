
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension
from markdown.util import etree

def fixup(elem):
    if elem.tag.startswith('h') and elem.tag[1] >= '1' and elem.tag[1] <= '6':
        classes = elem.get('class')
        if classes is not None and 'linkable' in classes:
            if len(elem[:]) > 0:
                print 'uh oh linkable header has child nodes!'
            else:
                a = etree.Element('a')
                target = '#%s' % elem.get('id')
                a.set('href', target)
                a.text = elem.text
                elem.text = None
                elem.append(a)

                icon = etree.Element('span')
                icon.set('class', 'link-icon')
                elem.append(icon)
                
class LinkHeadersProcessor(Treeprocessor):
    def run(self, root):
        for child in root:
            fixup(child)
            self.run(child)

        return root
    
class LinkHeadersExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.treeprocessors.add('link_headers', LinkHeadersProcessor(), '_end')
    
def makeExtension(configs=None):
    return LinkHeadersExtension(configs)
