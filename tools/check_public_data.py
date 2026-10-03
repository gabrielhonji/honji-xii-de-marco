"""Check the exact publication set without printing private identifiers."""
import argparse, ast, csv, io, re, subprocess, sys, unicodedata, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GIT=['git','-c','safe.directory='+ROOT.as_posix()]
PUBLIC_DIRS={'assets','web','tools','tests','outputs','.githooks','frontend'}
PUBLIC_ROOT={'.gitignore','.gitattributes','AGENTS.md','DESIGN.md','README.md','QA.md','requirements.txt','requirements-dev.txt','server.py'}
BRAND_BINARY={'assets/favicon.ico','assets/apple-touch-icon.png','assets/icon-192.png','assets/icon-512.png','assets/social-card.png'}

def normalize(value):
    return ''.join(c for c in unicodedata.normalize('NFKD',str(value)) if not unicodedata.combining(c)).casefold().strip()

def private_values():
    values=set()
    for path in (ROOT/'documentos-certificados').glob('*.csv'):
        raw=path.read_bytes()
        try:text=raw.decode('utf-8-sig')
        except UnicodeDecodeError:text=raw.decode('cp1252')
        try:dialect=csv.Sniffer().sniff(text[:12000],delimiters=',;\t')
        except csv.Error:dialect=csv.excel
        rows=list(csv.reader(io.StringIO(text),dialect))
        if not rows:continue
        indexes=[i for i,h in enumerate(rows[0]) if 'nome completo' in normalize(h) or 'registro academico' in normalize(h) or normalize(h)=='ra']
        values.update(normalize(row[i]) for row in rows[1:] for i in indexes if i<len(row) and row[i].strip())
    for path in (ROOT/'documentos-certificados').glob('blocked-values.txt'):
        values.update(normalize(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip())
    return values

def check(entries):
    blocked=private_values(); failures=[]
    for path,data in entries:
        parts=Path(path).parts
        if 'node_modules' in parts or '.env' in parts or path.endswith('.map'):
            failures.append((path,'dependência, configuração privada ou sourcemap não permitido'));continue
        if (len(parts)==1 and path not in PUBLIC_ROOT) or (len(parts)>1 and parts[0] not in PUBLIC_DIRS):
            failures.append((path,'caminho fora da lista pública'));continue
        suffix=Path(path).suffix.lower()
        if suffix in {'.pdf','.zip','.jpg','.jpeg','.ndjson'}:
            failures.append((path,'arquivo privado ou não permitido'));continue
        if suffix in {'.png','.ico'}:
            if path not in BRAND_BINARY:failures.append((path,'imagem não aprovada'))
            continue
        if suffix=='.xlsx':
            if path!='outputs/honji-qa-20261003/participacoes-ficticias.xlsx':
                failures.append((path,'planilha não aprovada'));continue
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                text=' '.join(archive.read(n).decode('utf-8',errors='replace') for n in archive.namelist() if n.endswith('.xml'))
            from openpyxl import load_workbook
            workbook=load_workbook(io.BytesIO(data),read_only=True,data_only=False)
            try:fixture_rows=list(workbook.active.values)
            finally:workbook.close()
            if not fictitious_rows(fixture_rows):failures.append((path,'planilha deve conter somente identidades fictícias'))
        else:text=data.decode('utf-8',errors='replace')
        if suffix=='.csv' and not fictitious_rows(list(csv.reader(io.StringIO(text.lstrip('\ufeff'))))):
            failures.append((path,'CSV deve conter somente identidades fictícias'))
        normalized=normalize(text)
        if any(re.search(r'(?<!\w)'+re.escape(value)+r'(?!\w)',normalized) for value in blocked):
            failures.append((path,'dado real detectado'))
        if parts[0]=='tests':
            for name in re.findall(r"name\s*=\s*['\"]([^'\"]+)['\"]",text):
                if not any(word in normalize(name) for word in ['fict','exemplo','example']):
                    failures.append((path,'nome de teste sem marcador fictício'))
            if suffix=='.py':
                for node in ast.walk(ast.parse(text)):
                    if isinstance(node,ast.keyword) and node.arg=='name' and isinstance(node.value,ast.Constant) and isinstance(node.value.value,str):
                        if not any(word in normalize(node.value.value) for word in ['fict','exemplo','example']):
                            failures.append((path,'nome literal de teste não fictício'))
    return failures

def fictitious_rows(rows):
    if not rows:return False
    indexes=[i for i,h in enumerate(rows[0]) if 'nome completo' in normalize(h)]
    if not indexes:return False
    return all(any(marker in normalize(row[i]) for marker in ['fict','exemplo','example']) for row in rows[1:] for i in indexes if i<len(row) and row[i])

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--staged',action='store_true');parser.add_argument('--ref');parser.add_argument('--history');args=parser.parse_args()
    if args.history:
        commits=subprocess.check_output(GIT+['rev-list',args.history],cwd=ROOT,text=True).splitlines();failures=[];count=0
        for commit in commits:
            paths=subprocess.check_output(GIT+['ls-tree','-r','--name-only',commit],cwd=ROOT,text=True).splitlines()
            entries=[(p,subprocess.check_output(GIT+['show',commit+':'+p],cwd=ROOT)) for p in paths];count+=len(entries)
            failures.extend(check(entries))
        for path,reason in sorted(set(failures)):print(path+': '+reason)
        print(f'{len(commits)} commits; {count} arquivos verificados; {len(failures)} bloqueios.')
        return bool(failures)
    if args.ref:
        paths=subprocess.check_output(GIT+['ls-tree','-r','--name-only',args.ref],cwd=ROOT,text=True).splitlines()
        entries=[(p,subprocess.check_output(GIT+['show',args.ref+':'+p],cwd=ROOT)) for p in paths]
    elif args.staged:
        paths=subprocess.check_output(GIT+['ls-files'],cwd=ROOT,text=True).splitlines()
        entries=[(p,subprocess.check_output(GIT+['show',':'+p],cwd=ROOT)) for p in paths]
    else:parser.error('Use --staged, --ref ou --history para verificar o conteúdo publicado.')
    failures=check(entries)
    for path,reason in failures:print(path+': '+reason)
    print(f'{len(entries)} arquivos verificados; {len(failures)} bloqueios.')
    return bool(failures)

if __name__=='__main__':sys.exit(main())
