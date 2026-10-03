"""Local certificate workspace. Uploaded personal data lives only in request memory."""
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from io import BytesIO, StringIO
from datetime import date
from xml.sax.saxutils import escape
import base64, csv, json, re, unicodedata, zipfile, argparse, math
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import white, HexColor

ROOT = Path(__file__).resolve().parent
ACTIVITIES = {'XII': 'Membro da Atlética XII de Março', 'Atleta': 'Atleta da XII de Março', 'Hunter': 'Hunter E-sports', 'TOC': 'Torcida Organizada Caçadores', 'Pantercats': 'Cheerleaders Pantercats', 'Panterada': 'Bateria Panterada', 'EP': 'Engenharíadas Paranaense', 'JIA': 'Jogos Interatléticas', 'Evento': 'Evento esportivo', 'Social': 'Ação social'}

def split_participations(source):
    source = re.sub(r'^\s*sim\s*,\s*', '', source, flags=re.I)
    # Keep parenthetical context intact; only known new roles start another record.
    role = r'(?:atleta|e-atleta|departamento|diretor\w*|presidente|conselheiro|membro|ep\b|jia\b|jua\b|doa[çc][aã]o|arrecada[çc][aã]o|canil\b|recep[çc][aã]o|projeto\b)'
    cuts = []
    for match in re.finditer(r'(?:[,;\n]+\s*|\s+-\s+|\s+e\s+)(?='+role+r')',source,re.I):
        prefix=source[:match.start()]
        if prefix.count('(')==prefix.count(')'): cuts.append((match.start(),match.end()))
    pieces=[]; start=0
    for a,b in cuts: pieces.append(source[start:a]); start=b
    pieces.append(source[start:]); return pieces

def norm(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', str(text)) if not unicodedata.combining(c)).lower().strip()

def inactive(text):
    return norm(text) in {'', '.', '-', 'nao', 'nao fui', 'nao me enquadro', 'nao diretamente', 'apenas atleta.'}

def periods(text):
    """Only expand explicit ranges. Missing connectors and bare years need review."""
    matches = list(re.finditer(r'(?<!\d)(20\d{2})\s*[/.-]\s*0?([12])(?!\d)', text))
    if not matches:
        return [], 'Informe o semestre e o período de participação.'
    if re.search(r'\bdesde\b', norm(text)):
        return [], 'Período em aberto: confirme início e término.'
    result = []
    i = 0
    while i < len(matches):
        a = matches[i]; start = int(a[1])*2+int(a[2])-1
        if i+1 < len(matches):
            b = matches[i+1]; connector = norm(text[a.end():b.start()])
            if re.fullmatch(r'\s*(ate|a|ao|->|–|-)\s*', connector):
                end = int(b[1])*2+int(b[2])-1
                if end < start or end-start > 40:
                    return [], 'Intervalo invertido ou maior que 20 anos.'
                result.extend(f'{x//2}.{x%2+1}' for x in range(start,end+1)); i += 2; continue
            if not connector or connector.isspace():
                return [], 'Duas datas sem conexão: confirme se representam um intervalo.'
            if not re.fullmatch(r'\s*(?:e|,|;|\+)\s*', connector):
                return [], 'Conexão entre datas não reconhecida. Confirme se são semestres separados ou um intervalo.'
        result.append(f'{a[1]}.{int(a[2])}'); i += 1
    # Do not silently discard standalone years mixed with semesters.
    leftover = re.sub(r'20\d{2}\s*[/.-]\s*0?[12]', '', text)
    if re.search(r'(?<!\d)20\d{2}(?!\d)', leftover):
        return [], 'Há anos sem semestre nesta resposta. Separe e confirme os períodos.'
    return sorted(set(result)), None

def rows_from_file(filename, data):
    if filename.lower().endswith('.csv'):
        try: text = data.decode('utf-8-sig')
        except UnicodeDecodeError: text = data.decode('cp1252')
        try: dialect = csv.Sniffer().sniff(text[:12000], delimiters=',;\t')
        except csv.Error: dialect = csv.excel
        rows = list(csv.reader(StringIO(text), dialect))
    elif filename.lower().endswith('.xlsx'):
        from openpyxl import load_workbook
        with zipfile.ZipFile(BytesIO(data)) as archive:
            if sum(i.file_size for i in archive.infolist()) > 40_000_000:
                raise ValueError('Planilha descompactada excede 40 MB.')
        wb = load_workbook(BytesIO(data), read_only=True, data_only=False)
        try:
            rows = [[str(v) if v is not None else '' for v in row] for row in wb.active.iter_rows(values_only=True)]
        finally:
            wb.close()
    else: raise ValueError('Use um arquivo CSV ou XLSX.')
    if len(rows) < 2 or len(rows) > 5001: raise ValueError('O arquivo deve conter de 1 a 5.000 respostas.')
    headers = [norm(x) for x in rows[0]]
    if not any('nome completo' in h for h in headers) or not any('registro academico' in h or h == 'ra' for h in headers):
        raise ValueError('Colunas Nome Completo e R.A (Registro Acadêmico) não encontradas.')
    return headers, rows[1:]

def analyze(filename, data):
    headers, rows = rows_from_file(filename, data)
    records, seen, duplicates = [], set(), 0
    names_by_ra = {}
    for rownum, row in enumerate(rows, 2):
        if not any(row): continue
        values = list(zip(headers, row))
        name = next((v.strip() for h,v in values if 'nome completo' in h), '')
        ra = next((v.strip().removesuffix('.0') for h,v in values if 'registro academico' in h or h == 'ra'), '')
        identity_error = '' if name and re.fullmatch(r'\d{5,12}',ra) else 'Confira o nome e o RA (5 a 12 dígitos).'
        names_by_ra.setdefault(ra, set()).add(norm(name))
        for h, source in values:
            activity = None
            if 'se foi atleta/' in h: activity = 'Atleta'
            elif 'se foi membro da' in h and 'xii' in h: activity = 'XII'
            elif 'membro da hunter' in h: activity = 'Hunter'
            elif 'membro da toc' in h: activity = 'TOC'
            elif 'membro das pantercats' in h and 'ex:' in h: activity = 'Pantercats'
            elif 'se foi membro da bateria' in h: activity = 'Panterada'
            elif 'acao social' in h: activity = 'Social'
            elif 'evento esportivo' in h: activity = 'EP'
            if not activity or inactive(source): continue
            # Split different roles/modalities, while preserving comma-separated dates.
            pieces = split_participations(source)
            for piece in pieces:
                piece = piece.strip()
                if inactive(piece): continue
                kind = activity
                if activity == 'EP':
                    labels=set(re.findall(r'\b(?:ep|jia|jua)\b',norm(piece)))
                    kind = 'JIA' if labels=={'jia'} else ('EP' if labels=={'ep'} else 'Evento')
                if activity == 'Atleta':
                    if 'hunter' in norm(piece) or 'e-atleta' in norm(piece): kind = 'Hunter'
                    elif 'pantercat' in norm(piece): kind = 'Pantercats'
                semester_list, warning = periods(piece)
                if activity in {'Social','EP'}:
                    semester_list, warning = [], 'Confirme o evento, o semestre e a carga horária.'
                detail = re.split(r'20\d{2}',piece)[0].strip(' ,.-') or ACTIVITIES[kind]
                if norm(detail) in {'de','membro de','membro','sim'}: detail=ACTIVITIES[kind]
                for semester in semester_list or ['']:
                    key = (ra,norm(name),kind,semester,norm(detail))
                    if key in seen: duplicates += 1; continue
                    seen.add(key)
                    field_warning = ''
                    if len(name)>150 or len(detail)>350:
                        field_warning='Nome ou descrição excede o limite do certificado. Revise o texto.'
                    if any(str(v).lstrip().startswith('=') for v in (name,ra,piece)):
                        field_warning='Há uma fórmula na resposta. Substitua por dados confirmados.'
                    records.append(dict(id=len(records)+1,name=name,ra=ra,activity=kind,detail=detail,semester=semester,hours=48 if kind=='EP' else (0 if kind in {'Social','JIA','Evento'} else 100),source=piece,row=rownum,warning=identity_error or field_warning or warning or '',approved=False))
    for record in records:
        if len(names_by_ra[record['ra']])>1:
            record['warning']='O mesmo RA aparece com nomes diferentes. Confirme a identidade e as participações.'
    if not records: raise ValueError('Nenhuma participação encontrada nas colunas do formulário.')
    return dict(records=records,people=len({r['ra'] for r in records}),responses=len(rows),duplicates=duplicates,filename=filename)

def validate_record(record):
    if not isinstance(record,dict) or record.get('approved') is not True: raise ValueError('Aprove cada certificado antes de gerar.')
    for key, limit in [('name',150),('ra',12),('detail',350),('semester',6)]:
        if not isinstance(record.get(key),str) or not record[key].strip() or len(record[key])>limit: raise ValueError('Campo inválido: '+key)
    if not re.fullmatch(r'\d{5,12}',record['ra']): raise ValueError('RA inválido.')
    if not re.fullmatch(r'20\d{2}\.[12]',record['semester']): raise ValueError('Semestre inválido. Use 2026.1 ou 2026.2.')
    if record.get('activity') not in ACTIVITIES: raise ValueError('Atividade inválida.')
    if isinstance(record.get('hours'),bool) or not isinstance(record.get('hours'),(int,float)) or not math.isfinite(record['hours']) or not 0.5 <= record['hours'] <= 2000: raise ValueError('Horas devem estar entre 0,5 e 2.000.')

def certificate(record, issued):
    validate_record(record)
    issued = date.fromisoformat(issued)
    stream = BytesIO(); w,h=842,595
    pdf = canvas.Canvas(stream,pagesize=(w,h)); pdf.setTitle(f"{record['name']} - {record['activity']} - {record['semester']}")
    private_template=ROOT/'documentos-certificados/certificate-background.jpg'
    if private_template.is_file():
        pdf.drawImage(str(private_template),0,0,w,h)
    else:
        pdf.setFillColor(HexColor('#761b35'));pdf.rect(0,0,w,h,fill=1,stroke=0)
        pdf.setStrokeColor(HexColor('#d8b366'));pdf.setLineWidth(1.5);pdf.rect(24,24,w-48,h-48,stroke=1,fill=0)
        pdf.setFillColor(white);pdf.setFont('Helvetica-Bold',16);pdf.drawCentredString(w/2,535,'ATLÉTICA XII DE MARÇO')
        pdf.setFont('Helvetica-Bold',42);pdf.drawCentredString(w/2,470,'CERTIFICADO')
        pdf.setFont('Helvetica',11);pdf.drawCentredString(w/2,65,'Secretaria da Atlética · UTFPR Apucarana')
    months = ['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro']
    pdf.setFillColor(white); pdf.setFont('Helvetica-Bold',13)
    pdf.drawCentredString(w/2,415,f'APUCARANA, {issued.day} DE {months[issued.month-1].upper()} DE {issued.year}')
    name=escape(record['name'].upper())
    ra,detail=[escape(record[k]) for k in ('ra','detail')]
    activity=record['activity']; semester=record['semester'].replace('.','/')
    if activity in {'EP','JIA','Evento','Social'}:
        participation=f'participou de {escape(ACTIVITIES[activity])}, na atividade {detail}, no semestre {semester}.'
    else:
        participation=f'participou de {escape(ACTIVITIES[activity])}, na função/atividade {detail}, por um semestre, sendo este no ano de {semester}.'
    text=f'Declaramos para os devidos fins que <b>{name}</b>, portador(a) do R.A. (Registro Acadêmico): <b>Nº {ra}</b>, {participation}<br/><br/>Esta declaração está de acordo com a organização geral da Associação Atlética Acadêmica de Engenharia XII de Março.<br/><br/>Para tanto foram declaradas <b>{record["hours"]:g} horas</b>; totalizando <b>{record["hours"]:g} horas</b>.'
    style=ParagraphStyle('body',fontName='Helvetica',fontSize=16,leading=22,textColor=white,alignment=1)
    paragraph=Paragraph(text,style); pw,ph=paragraph.wrap(750,235)
    while ph>230 and style.fontSize>11:
        style.fontSize-=1; style.leading-=1; paragraph=Paragraph(text,style); pw,ph=paragraph.wrap(750,235)
    if ph>230: raise ValueError('Texto muito longo para o modelo. Encurte a descrição.')
    paragraph.drawOn(pdf,46,390-ph)
    pdf.showPage(); pdf.save(); return stream.getvalue()

def slug(value):
    return re.sub(r'[^a-zA-Z0-9._-]+','-',norm(value)).strip('-.')[:100] or 'certificado'

def make_zip(records, issued, naming):
    if naming not in {'name','ra'}: raise ValueError('Escolha nomes por pessoa ou RA.')
    if not records or len(records)>1000: raise ValueError('Selecione de 1 a 1.000 certificados.')
    stream=BytesIO(); manifest=[]; filenames=set()
    with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as archive:
        for r in records:
            if r.get('warning'): raise ValueError('Resolva as pendências antes de emitir.')
            body=certificate(r,issued)
            prefix=slug(r['ra'] if naming=='ra' else r['name'])
            folder=f'{prefix}/'; base=f'{prefix} - {slug(r["activity"])} - {r["semester"]}'
            filename=folder+base+'.pdf'; suffix=2
            while filename in filenames: filename=folder+base+f' - {suffix}.pdf'; suffix+=1
            filenames.add(filename); archive.writestr(filename,body)
            manifest.append({'arquivo':filename,'nome':r['name'],'ra':r['ra'],'atividade':r['activity'],'descricao':r['detail'],'semestre':r['semester'],'horas':r['hours'],'origem':r.get('source','')})
        output=StringIO(); writer=csv.DictWriter(output,fieldnames=list(manifest[0])); writer.writeheader()
        # Neutralize spreadsheet formula injection in the audit file.
        writer.writerows({k:("'"+str(v) if str(v).lstrip().startswith(('=','+','-','@')) or str(v).startswith(('\t','\r')) else v) for k,v in m.items()} for m in manifest)
        archive.writestr('relatorio.csv',output.getvalue().encode('utf-8-sig'))
    return stream.getvalue()

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def reply(self,body,kind='application/json',status=200):
        if isinstance(body,dict): body=json.dumps(body,ensure_ascii=False).encode()
        self.send_response(status); self.send_header('Content-Type',kind); self.send_header('Content-Length',str(len(body)))
        self.send_header('Cache-Control','no-store'); self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' blob:; frame-src 'self' blob:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        paths={'/':('web/index.html','text/html; charset=utf-8'),'/app.js':('web/app.js','text/javascript; charset=utf-8'),'/style.css':('web/style.css','text/css; charset=utf-8'),'/responsive.css':('web/responsive.css','text/css; charset=utf-8')}
        paths['/site.webmanifest']=('web/site.webmanifest','application/manifest+json')
        paths['/identidade']=('web/identity.html','text/html; charset=utf-8')
        paths['/identity.js']=('web/identity.js','text/javascript; charset=utf-8')
        paths['/identity.css']=('web/identity.css','text/css; charset=utf-8')
        for asset in ['xii-icon.svg','honji-symbol.svg','xii-symbol.svg','xii-logo.svg','favicon.svg','favicon.ico','apple-touch-icon.png','icon-192.png','icon-512.png','social-card.png']:
            kind='image/svg+xml' if asset.endswith('.svg') else ('image/x-icon' if asset.endswith('.ico') else 'image/png')
            paths['/assets/'+asset]=('assets/'+asset,kind)
        if self.path.split('?')[0] not in paths: return self.reply({'error':'Não encontrado'},status=404)
        self.path=self.path.split('?')[0]
        path,kind=paths[self.path]; self.reply((ROOT/path).read_bytes(),kind)
    def do_POST(self):
        try:
            # Reject cross-origin requests and DNS rebinding against the local service.
            host=self.headers.get('Host',''); origin=self.headers.get('Origin')
            if host not in {f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'} or (origin and origin not in {f'http://{host}'}): return self.reply({'error':'Origem não permitida'},status=403)
            length=int(self.headers.get('Content-Length','0'))
            if not 0 < length <= 15_000_000: raise ValueError('Limite de upload: 10 MB.')
            payload=json.loads(self.rfile.read(length))
            if self.path=='/api/analyze':
                data=base64.b64decode(payload['data'],validate=True)
                if len(data)>10_000_000: raise ValueError('Limite de upload: 10 MB.')
                return self.reply(analyze(payload['filename'],data))
            if self.path=='/api/preview': return self.reply(certificate(payload['record'],payload['issued']),'application/pdf')
            if self.path=='/api/generate': return self.reply(make_zip(payload['records'],payload['issued'],payload.get('naming','name')),'application/zip')
            return self.reply({'error':'Não encontrado'},status=404)
        except ValueError as error: self.reply({'error':str(error) or 'Dados inválidos. Confira os campos preenchidos.'},status=400)
        except (KeyError,TypeError,csv.Error,zipfile.BadZipFile): self.reply({'error':'Dados inválidos. Confira o arquivo e os campos preenchidos.'},status=400)
        except Exception: self.reply({'error':'Não foi possível processar o arquivo. Confira o formato e tente novamente.'},status=400)

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--port',type=int,default=8000); args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    print(f'XII Certificados: http://127.0.0.1:{args.port}',flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: server.server_close()
