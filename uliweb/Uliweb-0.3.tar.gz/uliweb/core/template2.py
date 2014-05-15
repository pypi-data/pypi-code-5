#! /usr/bin/env python
#coding=utf-8

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

class TemplateException(Exception): pass
class ContextPopException(TemplateException):
    "pop() has been called more times than push()"
    pass

def use_tempdir(dir=''):
    global __options__, __templates_temp_dir__
    
    if dir:
        __templates_temp_dir__ = dir
        __options__['use_temp_dir'] = True
        if not os.path.exists(__templates_temp_dir__):
            os.makedirs(__templates_temp_dir__)

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

def register_node(name, node):
    assert issubclass(node, Node)
    __nodes__[name] = node

def reindent(pre, lines):
    new_lines=[]
    if pre:
        new_lines.append(pre)
    credit=k=0
    for line in lines:
        if not line or line[0]=='#':
            new_lines.append(line)
            continue
        if line[:5]=='elif ' or line[:5]=='else:' or    \
            line[:7]=='except:' or line[:7]=='except ' or \
            line[:7]=='finally:' or line[:5]=='with ':
                k=k+credit-1
        if k<0: k=0
        new_lines.append('    '*k+line)
        credit=0
        if line=='pass' or line[:5]=='pass ':
            credit=0
            k-=1
        if line[-1:]==':' or line[:3]=='if ':
            k+=1
    text='\n'.join(new_lines)
    return text

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

r_tag = re.compile('^#uliweb-template-tag:(.+?),(.+?)(:\r|\n|\r\n)')

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

class LinesNode(Node):
    def __init__(self):
        self.nodes = []

    def render(self):
        return self.nodes

    def __str__(self):
        return ''.join([str(x) for x in self.nodes])

    def __repr__(self):
        return '<LinesNode: ' + repr(self.nodes) + ' >'

class BaseBlockNode(Node):
    block = 1

    def __init__(self, name='', content=None):
        self.nodes = []
        self.name = name
        self.content = content
        
    def get_lines_node(self):
        if not self.nodes:
            top = None
        else:
            top = self.nodes[-1]
        if top.__class__ is not LinesNode:
            top = LinesNode()
            self.nodes.append(top)
        return top

    def extend(self, lines):
        top = self.get_lines_node()
        top.nodes.extend(lines)
        
    def add(self, node):
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
    def add(self, node):
        if node.__class__ is Node:
            top = self.get_lines_node()
            top.nodes.append(node)
        else:
            self.nodes.append(node)
            if node.__class__ is BlockNode and node.name:
                self.content.root.block_vars.setdefault(node.name, []).append(node)
        
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


class Content(BaseBlockNode):
    def __init__(self, root=None):
        self.nodes = []
        self.block_vars = {}
        self.begin = []
        self.end = []
        self.root = root or self
        
    def add(self, node):
        if node.__class__ is Node:
            top = self.get_lines_node()
            top.nodes.append(node)
        else:
            self.nodes.append(node)
            if node.__class__ is BlockNode and node.name:
                self.block_vars.setdefault(node.name, []).append(node)

    def merge(self, content):
        self.nodes.extend(content.nodes)
        for k, v in content.block_vars.items():
            self.block_vars.setdefault(k, []).extend(v)
        content.root = self.root
        
    def clear_content(self):
        self.nodes = []
    
    # def __str__(self):
    #     s = self.begin[:]
    #     for x in self.nodes:
    #         s.append(str(x))
    #     s.extend(self.end)
    #     return ''.join(s)
    
    # def __repr__(self):
    #     s = []
    #     for x in self.nodes:
    #         s.append(repr(x))
    #     return ''.join(s)

class Context(object):
    "A stack container for variable context"
    def __init__(self, dict_=None):
        dict_ = dict_ or {}
        self.dicts = [dict_]
        self.dirty = True
        self.result = None

    def __repr__(self):
        return repr(self.dicts)

    def __iter__(self):
        for d in self.dicts:
            yield d

    def push(self):
        d = {}
        self.dicts = [d] + self.dicts
        self.dirty = True
        return d

    def pop(self):
        if len(self.dicts) == 1:
            raise ContextPopException
        return self.dicts.pop(0)
        self.dirty = True

    def __setitem__(self, key, value):
        "Set a variable in the current context"
        self.dicts[0][key] = value
        self.dirty = True

    def __getitem__(self, key):
        "Get a variable's value, starting at the current context and going upward"
        for d in self.dicts:
            if key in d:
                return d[key]
        raise KeyError(key)

    def __delitem__(self, key):
        "Delete a variable from the current context"
        del self.dicts[0][key]
        self.dirty = True

    def has_key(self, key):
        for d in self.dicts:
            if key in d:
                return True
        return False

    __contains__ = has_key

    def get(self, key, otherwise=None):
        for d in self.dicts:
            if key in d:
                return d[key]
        return otherwise

    def update(self, other_dict):
        "Like dict.update(). Pushes an entire dictionary's keys and values onto the context."
        if not hasattr(other_dict, '__getitem__'): 
            raise TypeError('other_dict must be a mapping (dictionary-like) object.')
        self.dicts[0].update(other_dict)
#        self.dicts = [other_dict] + self.dicts
        self.dirty = True
        return other_dict
    
    def to_dict(self):
        if not self.dirty:
            return self.result
        else:
            d = {}
            for i in reversed(self.dicts):
                d.update(i)
            self.result = d
            self.dirty = False
        return d
        
__nodes__['block'] = BlockNode

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
        
#    def json(self, text):
#        from datawrap import dumps
#        self.write(dumps(text))
#
    def getvalue(self):
        return self.buf.getvalue()

class Template(object):
    def __init__(self, text='', vars=None, env=None, dirs=None, 
        default_template=None, use_temp=False, compile=None, skip_error=False, 
        encoding='utf-8', begin_tag=None, end_tag=None, see=None):
        self.text = text
        self.filename = None
        self.vars = vars or {}
        if not isinstance(env, Context):
            env = Context(env)
        self.env = env
        self.dirs = dirs or '.'
        self.default_template = default_template
        self.use_temp = use_temp
        self.compile = compile
        self.writer = 'out.write'
        self.content = Content()
        self.stack = [self.content]
        self.depend_files = []  #used for template dump file check
        self.callbacks = []
        self.exec_env = {}
        self.root = self
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
            self.root.callbacks.append(callback)
            
    def add_exec_env(self, name, obj):
        self.root.exec_env[name] = obj
        
    def add_root(self, root):
        self.root = root
        
    def set_filename(self, filename):
        fname = get_templatefile(filename, self.dirs, self.default_template)
        if not fname:
            raise TemplateException, "Can't find the template %s" % filename
        self.filename = fname
        self.original_filename = filename
        
    def _get_parameters(self, value):
        def _f(*args, **kwargs):
            return args, kwargs
        d = self.env.to_dict()
        d['_f'] = _f
        try:
            args, kwargs = eval("_f(%s)" % value, d, self.vars)
        except:
            if self.skip_error:
                return (None,), {}
            else:
                raise
        return args, kwargs
    
    def parse(self):
        text = self.text
        extend = None  #if need to process extend node
        pos = 0
        bufs = []
        n = 0
        while 1:
            if not self.stack:
                raise TemplateException, "The 'end' tag is unmatched, please check if you have more '{{end}}'"
            top = self.stack[-1]

            top_add = top.add

            #parse tag
            begin_pos = text.find(self.begin_tag, pos)
            end_pos = text.find(self.end_tag, begin_pos+self.begin_tag_len)

            if end_pos == -1:
                raise TemplateException("Template tag is not closed!")

            if begin_pos >= pos:
                top_add("%s(%r, escape=False)" % (self.writer, text[pos:begin_pos]))
            elif begin_pos == -1:
                top_add("%s(%r, escape=False)" % (self.writer, text[pos:]))
                break

            pos = end_pos + self.end_tag_len

            #parse tagname and text
            b = begin_pos + self.begin_tag_len
            e = end_pos

            line = text[b:e].strip()
            # while text[b] in (' ', '\t', '\r', '\n') and b<e:
            #     b += 1
            # while text[e-1] in (' ', '\t', '\r', '\n') and e>b:
            #     e -= 1

            #test if comments
            if not line or line[2] == '##':
                continue

            if line[0] == '=':
                name, value = '=', line[1:]
            elif line[:2] == '<<':
                name, value = '<<', line[2:]
            else:
                v = line.split(' ', 1)
                if len(v) == 1:
                    name = line
                    value = ''
                else:
                    name, value = v

            if name in __nodes__:
                node_cls = __nodes__[name]
                #this will pass top template instance and top content instance to node_cls
                node = node_cls(value, self.content)
                if node.block:
                    node.template_file = self.filename
                    top_add(node)
                    self.stack.append(node)
                else:
                    buf = str(node)
                    if buf:
                        top_add(buf)
            elif name == 'super':
                t = self.stack[-1]
                if isinstance(t, BaseBlockNode):
                    node = SuperNode(t, self.content)
                    top_add(node)
            elif name == 'end':
                #add block.end process
                #if end() return something, it'll be append to top node
                t = self.stack.pop()
                top = self.stack[-1]
                if t.block and hasattr(t, 'end'):
                    buf = t.end()
                    if buf:
                        top.add(buf)
            elif name == '=':
                top_add("%s(%s)" % (self.writer, value))
            elif name == 'BEGIN_TAG':
                top_add("%s('%s')" % (self.writer, self.begin_tag))
            elif name == 'END_TAG':
                top_add("%s('%s')" % (self.writer, self.end_tag))
            elif name == '<<':
                top_add("%s(%s, escape=False)" % (self.writer, value))
            elif name == 'include':
                self._parse_include(top, value)
            elif name == 'embed':
                self._parse_text(top, value)
            elif name == 'extend':
                extend = value
            else:
                top.extend(line.splitlines())


            n += 1

        if extend:
            self._parse_extend(extend)
        if self.encoding:
            pre = '#coding=%s\n' % self.encoding
        else:
            pre = ''

        return reindent(pre, self.content.render())
    
    def _parse_template(self, content, var):
        if var in self.vars:
            v = self.vars[var]
        else:
            return False
        
        #add v.__template__ support
        if hasattr(v, '__template__'):
            text = str(v.__template__(var))
            if text:
                t = Template(text, self.vars, self.env, self.dirs)
                t.parse()
                t.add_root(self)
                content.merge(t.content)
                return True
        
        return False

    def _parse_text(self, content, var):
        try:
            text = str(eval(var, self.env.to_dict(), self.vars))
        except:
            if self.skip_error:
                text = ''
            else:
                raise
        if text:
            t = Template(text, self.vars, self.env, self.dirs)
            t.parse()
            t.add_root(self)
            content.merge(t.content)
    
    def _parse_include(self, content, value):
        self.env.push()
        try:
            args, kwargs = self._get_parameters(value)
            filename = args[0]
            self.env.update(kwargs)
            fname = get_templatefile(filename, self.dirs, skip=self.filename, skip_original=self.original_filename)
            if not fname:
                raise TemplateException, "Can't find the template %s" % filename
            
            self.depend_files.append(fname)
            
            #track template tree
            if self.see:
                self.see('include', self.filename, fname)
                
            f = open(fname, 'rb')
            text, begin_tag, end_tag = self.get_text(f.read(), inherit_tags=False)
            f.close()
            t = Template(text, self.vars, self.env, self.dirs, begin_tag=begin_tag, end_tag=end_tag, see=self.see)
            t.set_filename(fname)
            t.add_root(self)
            t.parse()
            content.merge(t.content)
        finally:
            self.env.pop()
        
    def _parse_extend(self, value):
        """
        If the extend template is the same name with current file, so it
        means that it should use parent template
        """
        self.env.push()
        try:
            args, kwargs = self._get_parameters(value)
            filename = args[0]
            self.env.update(kwargs)
            fname = get_templatefile(filename, self.dirs, skip=self.filename, skip_original=self.original_filename)
            if not fname:
                raise TemplateException, "Can't find the template %s" % filename
            
            self.depend_files.append(fname)
            
            #track template tree
            if self.see:
                self.see('extend', self.filename, fname)
            
            f = open(fname, 'rb')
            text, begin_tag, end_tag = self.get_text(f.read(), inherit_tags=False)
            f.close()
            t = Template(text, self.vars, self.env, self.dirs, begin_tag=begin_tag, end_tag=end_tag, see=self.see)
            t.set_filename(fname)
            t.add_root(self)
            t.parse()
            self.content.clear_content()
            t.content.merge(self.content)
            self.content = t.content
        finally:
            self.env.pop()
            
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
        return False, self.filename, self.parse()
        
    def get_text(self, text, inherit_tags=True):
        """
        Detect template tag definition in the text
        If inherit_tags is True, then use current begin and end tag string, 
        or use default tag string
        """
        b = r_tag.search(text)
        if b:
            begin_tag, end_tag = b.group(1), b.group(2)
            text = text[b.end():]
        else:
            if inherit_tags:
                begin_tag = self.begin_tag
                end_tag = self.end_tag
            else:
                begin_tag = BEGIN_TAG
                end_tag = END_TAG
        return text, begin_tag, end_tag
    
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
        if isinstance(self.env, Context):
            new_e = self.env.to_dict()
        else:
            new_e = self.env
        e.update(new_e)
        e.update(self.vars)
        out = Out()
        e['out'] = out
        e['Out'] = Out
        e['xml'] = out.xml
        e['_vars'] = self.vars
        e['defined'] = f(self.vars, self.env)
        e['_env'] = e
        
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
    
def template_file(filename, vars=None, env=None, dirs=None, default_template=None, compile=None, **kwargs):
    t = Template('', vars, env, dirs, default_template, use_temp=__options__['use_temp_dir'], compile=compile, **kwargs)
    t.set_filename(filename)
    return t()

def template(text, vars=None, env=None, dirs=None, default_template=None, **kwargs):
    t = Template(text, vars, env, dirs, default_template, **kwargs)
    return t()
