"""Move methods out of GameScreen into a collaborator class in the same package.

Usage: python3 tools/v6/extract_methods.py <ClassName> <field> <method> [<method> ...]

The moved code reaches GameScreen state through `g.` (GameScreen members it touches
lose their `private` modifier). GameScreen keeps calling the moved methods through
the new field. Purely mechanical; correctness is checked by compiling and by the
golden-frame comparison of the desktop capture harness.
"""
import re, sys
from pathlib import Path

SRC = Path('core/src/main/java/com/arlandsofia/olu/screens')
GS = SRC / 'GameScreen.java'
cls, field, names = sys.argv[1], sys.argv[2], sys.argv[3:]
s = GS.read_text(encoding='utf-8')


def method_span(text, name):
    m = re.search(r'\n((?:    @Override\s*\n)?    (?:(?:private|protected|public|static|final|synchronized)\s+)*[\w<>\[\],. ]+\s+' + re.escape(name) + r'\s*\([^)]*\)\s*(?:throws [\w, ]+)?\{)', text)
    if not m:
        raise SystemExit('method not found: ' + name)
    start = m.start(1)
    i = text.index('{', m.end(1) - 1)
    depth, j = 0, i
    in_str = None
    while True:
        c = text[j]
        if in_str:
            if c == '\\':
                j += 2; continue
            if c == in_str:
                in_str = None
        elif text.startswith('//', j):
            j = text.index('\n', j); continue
        elif text.startswith('/*', j):
            j = text.index('*/', j) + 2; continue
        elif c in '"\'':
            in_str = c
        elif c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                break
        j += 1
    # include a javadoc/comment block directly above
    k = start
    above = text.rfind('\n', 0, start - 1)
    while True:
        line = text[above + 1:k].strip()
        if line.startswith('/**') or line.startswith('*') or line.startswith('//') or line.startswith('*/'):
            k = above + 1
            above = text.rfind('\n', 0, above)
        else:
            break
    return k, j + 1


# Members of GameScreen (fields + methods) and BaseScreen (protected ones).
members = set()
body = s[s.index('public final class GameScreen'):]
for m in re.finditer(r'\n    (?=\S)(?:(?:private|protected|public|static|final|transient|volatile)\s+)*[\w<>\[\],.? ]+?\s+(\w+)\s*(?:=|;|,)', body):
    members.add(m.group(1))
for m in re.finditer(r'\n    (?=\S)(?:@\w+\s+)?(?:\w[\w<>\[\],.? ]*?\s)?(\w+)\s*\([^)]*\)\s*(?:throws [\w, ]+)?\{', body):
    members.add(m.group(1))
# multi-declarations like "private float a, b, c;" and "private String x; private float y;"
for m in re.finditer(r'\n    (?=\S)(?:private|protected|public|final|static)[^\n(]*;', body):
    for part in m.group(0).split(';'):
        for decl in part.split(','):
            mm = re.search(r'(\w+)\s*(?:=.*)?$', decl.strip())
            if mm:
                members.add(mm.group(1))
# field lines without an initializer call: "float a, b, c;" / "String x; float y;"
for m in re.finditer(r'\n    (?=[A-Za-z])([^\n(){}]*;)', body):
    for part in m.group(1).split(';'):
        for decl in part.split(','):
            mm = re.search(r'(\w+)\s*(?:=.*)?$', decl.strip())
            if mm:
                members.add(mm.group(1))
base = (SRC / 'BaseScreen.java').read_text(encoding='utf-8')
for m in re.finditer(r'protected[^;(=]*?\s(\w+)\s*(?:\(|=|;)', base):
    members.add(m.group(1))
members -= set(names)
members -= {'null', 'true', 'false', 'this', 'super', 'else', 'int', 'float', 'boolean', 'void', 'String', 'if', 'for', 'while', 'return', 'new', 'class', 'static', 'final', 'GameScreen', 'DrawItem'}

members -= set(names)
moved = []
for name in names:
    a, b = method_span(s, name)
    moved.append(s[a:b])
    s = s[:a] + s[b:]

JAVA_KW = set('int float boolean double long char byte short void final var'.split())


def _toplevel(stmt):
    out, depth = [], 0
    for ch in stmt:
        if ch in '([{': depth += 1
        elif ch in ')]}': depth -= 1
        out.append(ch if depth == 0 else ' ')
    return ''.join(out)


def locals_of(code):
    loc = set()
    sig = code[:code.index('{')]
    for p in re.findall(r'(\w+)\s*(?:,|\))', sig[sig.index('('):]):
        loc.add(p)
    for m in re.finditer(r'(?:^|[;{(]|\n)\s*(?:final\s+)?([A-Za-z_][\w.\[\]]*(?:<[^;{}()]*?>)?(?:\[\])*)\s+(\w+)\s*(=|:|;|,)', code):
        if m.group(1) in ('return', 'new', 'else', 'throw', 'case'):
            continue
        loc.add(m.group(2))
        if m.group(3) in '=,':
            # further declarators of the same statement: "float a = 1, b = 2;"
            stmt = (',' if m.group(3) == ',' else '') + code[m.end():code.find(';', m.end())]
            for part in re.findall(r',\s*(\w+)\s*(?==|,|$)', _toplevel(stmt)):
                loc.add(part)
    # parameters of anonymous-class / lambda-style methods inside the body
    for m in re.finditer(r'[(,]\s*(?:final\s+)?[A-Za-z_][\w.\[\]]*(?:<[^;{}()]*?>)?\s+(\w+)\s*(?=[,)])', code):
        loc.add(m.group(1))
    return loc - JAVA_KW


def qualify(code, full):
    loc = locals_of(full)
    out = []
    i = 0
    tok = re.compile(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|//[^\n]*|/\*.*?\*/|\b[A-Za-z_]\w*\b|.', re.S)
    prev_sig = ''
    for m in tok.finditer(code):
        t = m.group(0)
        if re.fullmatch(r'[A-Za-z_]\w*', t) and t in members and t not in loc and prev_sig != '.':
            # a declaration "Type name" right before? skip if previous token is a type-like identifier
            out.append('g.' + t)
        else:
            out.append(t)
        if not t.isspace():
            prev_sig = t
    return ''.join(out)


NESTED = ['DrawItem']
new_methods = []
for code in moved:
    head, rest = code[:code.index('{')], code[code.index('{'):]
    head = re.sub(r'\b(private|protected|public)\s+', '', head)
    head = head.replace('@Override', '')
    body2 = qualify(rest, code)
    for t in NESTED:
        body2 = re.sub(r'(?<![.\w])' + t + r'\b', 'GameScreen.' + t, body2)
    new_methods.append(head + body2)

# GameScreen: route calls to the moved methods through the new field; open members up.
for name in names:
    s = re.sub(r'(?<![.\w])' + re.escape(name) + r'\s*\(', field + '.' + name + '(', s)
# open every class-level member of GameScreen to the package (collaborators share its state)
_lines = s.split('\n')
for _i, _l in enumerate(_lines):
    if re.match(r'    (?=\S)', _l) and not _l.lstrip().startswith(('*', '/')):
        _lines[_i] = re.sub(r'\bprivate\s+(?!static final class)', '', _l)
s = '\n'.join(_lines)
decl = '    final %s %s = new %s(this);\n' % (cls, field, cls)
if decl not in s:
    anchor = s.index('public final class GameScreen')
    anchor = s.index('\n', s.index('{', anchor)) + 1
    s = s[:anchor] + decl + s[anchor:]
GS.write_text(s, encoding='utf-8')

# Overrides of BaseScreen hooks keep a delegating shim so the framework still calls them.
OVERRIDES = {'drawWorld': 'protected void drawWorld()', 'drawUi': 'protected void drawUi()', 'update': 'protected void update(float dt)'}
for name in names:
    if name in OVERRIDES:
        arg = 'dt' if name == 'update' else ''
        shim = '    @Override\n    %s { %s.%s(%s); }\n' % (OVERRIDES[name], field, name, arg)
        end = s.rindex('}')
        s = s[:end] + shim + s[end:]
for t in NESTED:
    s = s.replace('private static final class ' + t, 'static final class ' + t)
GS.write_text(s, encoding='utf-8')
imports = ''.join(l + '\n' for l in s.split('\n') if l.startswith('import '))
target = SRC / (cls + '.java')
if target.exists():
    cur = target.read_text(encoding='utf-8')
    cut = cur.rstrip().rindex('}')
    target.write_text(cur[:cut].rstrip() + '\n\n' + '\n\n'.join(new_methods) + '\n}\n', encoding='utf-8')
    print('appended', len(names), 'methods to', cls)
    raise SystemExit(0)
out = 'package com.arlandsofia.olu.screens;\n\n' + imports + '\n/** Extracted from GameScreen in v6 (mechanical move; state stays on GameScreen). */\nfinal class %s {\n    private final GameScreen g;\n    %s(GameScreen g) { this.g = g; }\n\n' % (cls, cls)
out += '\n\n'.join(new_methods) + '\n}\n'
(SRC / (cls + '.java')).write_text(out, encoding='utf-8')
print('moved', len(names), 'methods to', cls, '; members known:', len(members))
