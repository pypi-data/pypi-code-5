import re
import os
import cStringIO as StringIO
import cgi

__templates_temp_dir__ = 'tmp/templates_temp'
__options__ = {'use_temp_dir':False}
__nodes__ = {}   #user defined nodes

BEGIN_TAG = '{{'
END_TAG = '}}'
DEBUG = False

r_tag = re.compile('^#uliweb-template-tag:(.+?),(.+?)(:\r|\n|\r\n)')

def set_options(**options):
    """
    default use_temp_dir=False
    """
    __options__.update(options)

def get_temp_template(filename):
    if __options__['use_temp_dir']:
        f, filename = os.path.splitdrive(filename)
        filename = filename.replace('\\', '_')
        filename = filename.replace('/', '_')
        f, ext = os.path.splitext(filename)
        filename = f + '.py'
        return os.path.normpath(os.path.join(__templates_temp_dir__, filename))
    return filename

class TemplateException(Exception): pass

def parse_arguments(text, key='with'):
    r = re.compile(r'\s+%s\s+' % key)
    k = re.compile(r'^\s*([\w][a-zA-Z_0-9]*\s*)=\s*(.*)')
    b = r.split(text)
    if len(b) == 1:
        name, args, kwargs = b[0], (), {}
    else:
        name = b[0]
        s = b[1].split(',')
        args = []
        kwargs = {}
        for x in s:
            ret = k.search(x)
            if ret:
                kwargs[ret.group(1)] = ret.group(2)
            else:
                args.append(x)
                
    return name, args, kwargs

def eval_vars(vs, vars, env):
    if isinstance(vs, (tuple, list)):
        return [eval_vars(x, vars, env) for x in vs]
    elif isinstance(vs, dict):
        return dict([(x, eval_vars(y, vars, env)) for x, y in vs.iteritems()])
    else:
        return eval(vs, env, vars)

class Node(object):
    block = 0

    def __init__(self, value=''):
        self.value = value

    def __str__(self):
        return self.value
        
    def __repr__(self):
        return '<Node '+self.__str__()+'>'

    def render(self):
        return self.value

class BaseBlockNode(Node):
    block = 1

    def __init__(self, name=''):
        self.nodes = []
        self.name = name
        
    def extend(self, lines):
        self.nodes.extend(lines)
        
    def append(self, node):
        self.nodes.append(node)

    def end(self):
        pass
    
    def __repr__(self):
        s = ['{{BaseBlockNode %s}}' % self.name]
        for x in self.nodes:
            s.append(repr(x))
        s.append('{{end}}')
        return ''.join(s)
    
    def __str__(self):
        return ''.join([str(x) for x in self.render()])
    
    def render(self):
        """Output result

        It'll return a list of lines
        """
        for x in self.nodes:
            if isinstance(x, (str, unicode)):
                yield x
            else:
                for y in x.render():
                    yield y
    
class BlockNode(BaseBlockNode):        
    def merge(self, content):
        self.nodes.extend(content.nodes)
    
    def render(self, top=True):
        """
        Top: if output the toppest block node
        """
        if top and self.name in self.content.root.block_vars and self is not self.content.root.block_vars[self.name][-1]:
            return self.content.root.block_vars[self.name][-1].render(False)
        
        s = []
        for x in self.nodes:
            if x.__class__ is BlockNode:
                if x.name in self.content.root.block_vars:
                    s.extend(self.content.root.block_vars[x.name][-1].render())
                else:
                    s.extend(x.render())
            else:
                s.extend(x.render())
        if DEBUG:
            s.insert(0, 'out.write("<!-- BLOCK %s (%s) -->\\n", escape=False)' % (self.name, self.template_file.replace('\\', '/')))
            s.append('out.write("<!-- END %s -->\\n", escape=False)' % self.name)
        return s
        
class SuperNode(Node):
    def __init__(self, parent, content):
        self.parent = parent
        self.content = content
        
    def __str__(self):
        return ''.join(self.render())
    
    def __repr__(self):
        return '{{super}}'

    def render(self):
        for i, v in enumerate(self.content.root.block_vars[self.parent.name]):
            if self.parent is v:
                if i > 0:
                    return self.content.root.block_vars[self.parent.name][i-1].render(False)
        return ['']

class Out(object):
    encoding = 'utf-8'
    
    def __init__(self):
        self.buf = StringIO.StringIO()
        
    def _str(self, text):
        # if not isinstance(text, (str, unicode)):
        #     text = str(text)
        if isinstance(text, unicode):
            return text.encode(self.encoding)
        else:
            return text

    def write(self, text, escape=True):
        s = self._str(text)
        if escape:
            self.buf.write(cgi.escape(s))
        else:
            self.buf.write(s)
            
    def xml(self, text):
        self.write(self._str(text), escape=False)
        
    def getvalue(self):
        return self.buf.getvalue()

def get_templatefile(filename, dirs, default_template=None, skip='', skip_original=''):
    """
    Fetch the template filename according dirs
    :para skip: if the searched filename equals skip, then using the one before.
    """
    def _file(filename, dirs):
        for d in dirs:
            _f = os.path.normpath(os.path.join(d, filename))
            if os.path.exists(_f):
                yield _f
        raise StopIteration
    
    filename = os.path.normpath(filename)
    skip = os.path.normpath(skip)
    skip_original = os.path.normpath(skip_original)
    
    if os.path.exists(filename):
        return filename
    
    if filename and dirs:
        _files = _file(filename, dirs)
        if skip_original == filename:
            for f in _files:
                if f == skip:
                    break
                
        for f in _files:
            if f != skip:
                return f
            else:
                continue
            
    if default_template:
        if isinstance(default_template, (list, tuple)):
            for i in default_template:
                f = get_templatefile(i, dirs)
                if f:
                    return f
        else:
            return get_templatefile(default_template, dirs)

def register_node(name, node):
    assert issubclass(node, Node)
    __nodes__[name] = node

def reindent(pre, lines):
    new_lines=[]
    _append = new_lines.append
    if pre:
        _append(pre)
    credit=k=0
    for line in lines:
        if not line or line[0]=='#':
            _append(line)
            continue
        if line[:5]=='elif ' or line[:5]=='else:' or    \
            line[:7]=='except:' or line[:7]=='except ' or \
            line[:7]=='finally:' or line[:5]=='with ':
                k=k+credit-1
        if k<0: k=0
        _append('    '*k+line)
        credit=0
        if line=='pass' or line[:5]=='pass ':
            credit=0
            k-=1
        if line[-1:]==':' or line[:3]=='if ':
            k+=1
    text='\n'.join(new_lines)
    return text

__nodes__['block'] = BlockNode

class Template(object):
    def __init__(self, text='', vars=None, env=None, dirs=None, 
        default_template=None, use_temp=False, compile=None, skip_error=False, 
        encoding='utf-8', begin_tag=None, end_tag=None, see=None):

        self.text = text
        self.filename = None
        self.vars = vars or {}
        self.env = env
        self.dirs = dirs or '.'
        self.default_template = default_template
        self.use_temp = use_temp
        self.compile = compile
        self.writer = 'out.write'
        self.depend_files = []  #used for template dump file check
        self.callbacks = []
        self.exec_env = {}
        self.skip_error = skip_error
        self.encoding = encoding
        self.begin_tag = begin_tag or BEGIN_TAG
        self.end_tag = end_tag or END_TAG
        self.begin_tag_len = len(self.begin_tag)
        self.end_tag_len = len(self.end_tag)
        self.see = see #will used to track the derive relation of templates
        
        for k, v in __nodes__.iteritems():
            if hasattr(v, 'init'):
                v.init(self)

    def add_callback(self, callback):
        if not callback in self.root.callbacks:
            self.callbacks.append(callback)
            
    def add_exec_env(self, name, obj):
        self.exec_env[name] = obj

    def set_filename(self, filename):
        fname = get_templatefile(filename, self.dirs, self.default_template)
        if not fname:
            raise TemplateException("Can't find the template %s" % filename)
        self.filename = fname
        self.original_filename = filename

    def get_parsed_code(self):
        if self.use_temp:
            f = get_temp_template(self.filename)
            if os.path.exists(f):
                fin = file(f, 'r')
                modified = False
                files = [self.filename]
                line = fin.readline()
                if line.startswith('#uliweb-template-files:'):
                    files.extend(line[1:].split())
                else:
                    fin.seek(0)
                
                for x in files:
                    if os.path.getmtime(x) > os.path.getmtime(f):
                        modified = True
                        break
                    
                if not modified:
                    text = fin.read()
                    fin.close()
                    return True, f, text
        
        if self.filename and not self.text:
            self.text, self.begin_tag, self.end_tag = self.get_text(file(self.filename, 'rb').read())
        codes = self.parse()
        return False, self.filename, reindent('#coding=utf8', codes)
        
    def get_text(self, text, inherit_tags=True):
        """
        Detect template tag definition in the text
        If inherit_tags is True, then use current begin and end tag string, 
        or use default tag string
        """
        # b = r_tag.search(text)
        # if b:
        #     begin_tag, end_tag = b.group(1), b.group(2)
        #     text = text[b.end():]
        # else:
        #     if inherit_tags:
        #         begin_tag = self.begin_tag
        #         end_tag = self.end_tag
        #     else:
        #         begin_tag = BEGIN_TAG
        #         end_tag = END_TAG
        # return text, begin_tag, end_tag
        return text, '{{', '}}'

    def __call__(self):
        use_temp_flag, filename, code = self.get_parsed_code()
        
        if not use_temp_flag and self.use_temp:
            f = get_temp_template(filename)
            try:
                fo = file(f, 'wb')
                fo.write('#uliweb-template-files:%s\n' % ' '.join(self.depend_files))
                fo.write(code)
                fo.close()
            except:
                pass
        
        return self._run(code, filename or 'template')
        
    def _run(self, code, filename):
        def f(_vars, _env):
            def defined(v, default=None):
                _v = default
                if v in _vars:
                    _v = _vars[v]
                elif v in _env:
                    _v = _env[v]
                return _v
            return defined

        e = {}
        e.update(self.vars)
        out = Out()
        e['out'] = out
        e['xml'] = out.xml
        e['defined'] = f(self.vars, self.env)
        
        e.update(self.exec_env)
        
        if isinstance(code, (str, unicode)):
            if self.compile:
                code = self.compile(code, filename, 'exec', e)
            else:
                code = compile(code, filename, 'exec')
        exec code in e
        text = out.getvalue()
        
        for f in self.callbacks:
            text = f(text, self, self.vars, e)

        return text

    def parse(self):
        """Parse template text
        """
        code = []

        stack = [code]
        begin_tag = self.begin_tag
        end_tag = self.end_tag
        begin_tag_len = self.begin_tag_len
        end_tag_len = self.end_tag_len
        writer = self.writer
        text = self.text
        filename = self.filename

        extend = False  #if need to process extend node

        pos = 0
        while 1:
            try:
                top = stack[-1]
            except:
                raise TemplateException("The 'end' tag is unmatched, "
                    "please check if you have more '{{end}}'")

            _append = top.append

            #parse tag
            begin_pos = text.find(begin_tag, pos)
            end_pos = text.find(end_tag, begin_pos+begin_tag_len)

            if end_pos == -1:
                raise TemplateException("Template tag is not closed!")

            if begin_pos >= pos:
                _append("%s(%r, escape=False)" % (writer, text[pos:begin_pos]))
            elif begin_pos == -1:
                _append("%s(%r, escape=False)" % (writer, text[pos:]))
                break

            pos = end_pos + end_tag_len

            #parse tagname and text
            b = begin_pos + begin_tag_len
            e = end_pos

            line = text[b:e]

            #test if comments
            if not line or line[:2] == '##':
                continue

            line = line.strip()

            if line[0] == '=':
                name, value = '=', line[1:]
            elif line[:2] == '<<':
                name, value = '<<', line[2:]
            else:
                v = line.split(' ', 1)
                name, value = (v + [''])[:2]

            if name in __nodes__:
                node_cls = __nodes__[name]
                #this will pass top template instance and top content instance to node_cls
                node = node_cls(value)
                if node.block:
                    node.template_file = filename
                    stack.append(node.add)
                _append(node)
            # elif name == 'super':
            #     t = self.stack[-1]
            #     if isinstance(t, BaseBlockNode):
            #         node = SuperNode(t, self.content)
            #         top_add(node)
            elif name == 'end':
                #add block.end process
                #if end() return something, it'll be append to top node
                t = stack.pop()
                top = self.stack[-1]
                _append = top.append
                if t.block and hasattr(t, 'end'):
                    buf = t.end()
                    if buf:
                        _append(buf)
            elif name == '=':
                _append("%s(%s)" % (writer, value))
            elif name == 'BEGIN_TAG':
                _append("%s('%s')" % (writer, begin_tag))
            elif name == 'END_TAG':
                _append("%s('%s')" % (writer, end_tag))
            elif name == '<<':
                _append("%s(%s, escape=False)" % (writer, value))
            # elif name == 'include':
            #     self._parse_include(top, value)
            # elif name == 'embed':
            #     self._parse_text(top, value)
            # elif name == 'extend':
            #     extend = value
            else:
                top.extend(line.splitlines())


        return code


def template_file(filename, vars=None, env=None, dirs=None, default_template=None, compile=None, **kwargs):
    t = Template('', vars, env, dirs, default_template, use_temp=__options__['use_temp_dir'], compile=compile, **kwargs)
    t.set_filename(filename)
    return t()

def template(text, vars=None, env=None, dirs=None, default_template=None, **kwargs):
    t = Template(text, vars, env, dirs, default_template, **kwargs)
    return t()

if __name__ == '__main__':
    text = """<h1>Hello, {{=name}}
<div>
{{for i in items:}}
<li>{{=i}}</li>
{{pass}}
</div>
"""
    print template(text, {'name':'guest', 'items':['1', '2']})