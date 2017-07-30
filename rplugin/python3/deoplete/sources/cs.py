import re
import json
import urllib
import urllib.request
import urllib.parse
from .base import Base
from deoplete.util import get_simple_buffer_config, error

class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'cs'
        self.mark = '[CS]'
        self.rank = 500
        self.filetypes = ['cs']
        self.input_pattern = '\.\w*'
        self.is_bytepos = True

    def get_complete_position(self, context):
        m = re.search(r'\w*$', context['input'])
        return m.start() if m else -1

    def gather_candidates(self, context):
        host = self.vim.eval('g:OmniSharp_host')
        url = "%s/autocomplete" % host
        cur = self.vim.current
        win = cur.window
        cursor = win.cursor
        buf = cur.buffer
        lines = [str(i) for i in buf[:]]

        params = {
            'line': str(cursor[0]),
            'column': str(cursor[1]+1),
            'buffer': '\n'.join(lines),
            'filename': str(cur.buffer.name),
            'wordToComplete': context['complete_str'],
            'WantMethodHeader': True,
            'WantReturnType': True,
            'WantDocumentationForEveryCompletionResult': True
        }
        data = bytes(json.dumps(params), 'utf-8')

        req = urllib.request.Request(
            url, data, headers={'Content-Type': 'application/json; charset=UTF-8'},
            method='POST')
        with urllib.request.urlopen(req) as f:
            r = str(f.read(), 'utf-8')

        if r is None or len(r) == 0:
            return []
        l = json.loads(r)
        if l is None:
            return []

        completions = []
        for item in l:
            display = item['MethodHeader'] or ''
            kind_str = item['ReturnType'] or item['DisplayText']

            completionText = item['CompletionText']
            # TODO: Fix
            #description = item['Description'].replace('\r\n', '\n') or ''

            completions.append(dict(
                word=completionText,
                abbr=completionText,
                info=description,
                menu=display,
                kind=kind_str,
                icase=1,
                dup=1))

        return completions


