"""Regression and HTTP checks using deliberately fictitious participation data."""
import base64
import csv
import json
import threading
import unittest
import urllib.error
import urllib.request
import zipfile
from copy import deepcopy
from io import BytesIO, StringIO
from pathlib import Path
from http.server import ThreadingHTTPServer
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from server import ACTIVITIES, AuthError, Bff, Handler, ROOT, _issuer, analyze, canonical_detail, certificate, make_zip, periods, validate_record
from pypdf import PdfReader

class FakeAuditStore:
    @staticmethod
    def digest(value): return 'fixture-digest'
    def __init__(self, bff): self.bff=bff; self.last_audit=None
    def audit(self, subject, count): self.last_audit=(subject, count)
    def delete(self, sid): self.bff.active=False

class FakeBff:
    """Authentication boundary double; no personal data or real token is used."""
    def __init__(self):
        self.active=True; self.denied=set(); self.store=FakeAuditStore(self)
        self.issuer='https://identity.example.invalid/realms/honji'
        self.public_origin='http://fixture.invalid'
        self.env={'OIDC_CLIENT_ID':'fixture-client'}
    def authorize(self, handler, action, csrf=False):
        if not self.active: raise AuthError(401, 'Sessão necessária.')
        if action in self.denied: raise AuthError(403, 'Acesso não autorizado.')
        return 'fixture-session', {'sub':'00000000-0000-4000-8000-000000000001', 'name':'Pessoa Fictícia', 'csrf_hash':'fixture-digest', 'csrf_token':'fixture-csrf'}
    def session(self, handler, touch=False):
        if not self.active: return None, None
        return self.authorize(handler, 'xii.certificates.access')
    def callback(self, handler, query): raise AuthError(400, 'Login expirado ou inválido.')

class AuthorizationStore:
    @staticmethod
    def digest(value): return 'digest'
    @staticmethod
    def get(_sid, touch=False):
        return {'sub':'00000000-0000-4000-8000-000000000001', 'name':'Pessoa Fictícia', 'csrf_hash':'digest', 'csrf_token':'fixture-csrf'}

class AuthorizationHandler:
    class Headers(dict):
        def get_all(self,name,default=None):
            value=self.get(name); return [value] if value is not None else (default or [])
    headers=Headers({'Cookie':'xii.sid=' + 'A'*43})

class JsonResponse(BytesIO):
    def __enter__(self): return self
    def __exit__(self,*_args): self.close()

CSV = ROOT/'tests/fixtures/participacoes-ficticias.csv'
XLSX = ROOT/'outputs/honji-qa-20261003/participacoes-ficticias.xlsx'

def example(**changes):
    record=dict(name='André Exemplo Fictício',ra='0012345',activity='XII',detail='Secretaria',semester='2024.2',hours=100,approved=True,warning='',source='Resposta fictícia')
    record.update(changes)
    return record

class ImportRegressionTest(unittest.TestCase):
    def test_oidc_issuer_requires_the_exact_honji_realm(self):
        self.assertEqual(_issuer('https://acesso-gabriel.honji.com.br/realms/honji'),
                         'https://acesso-gabriel.honji.com.br/realms/honji')
        for value in ['https://acesso-gabriel.honji.com.br',
                      'https://acesso-gabriel.honji.com.br/realms/master',
                      'https://user:password@acesso-gabriel.honji.com.br/realms/honji']:
            with self.assertRaises(ValueError): _issuer(value)

    def test_authorization_failures_keep_safe_stage_and_status(self):
        env={'OIDC_CLIENT_ID':'browser','OIDC_CLIENT_SECRET':'x'*32,
             'AUTHORIZATION_SERVICE_CLIENT_ID':'service','AUTHORIZATION_SERVICE_CLIENT_SECRET':'y'*32,
             'AUTHORIZATION_SERVICE_ORIGIN':'http://authorization.internal'}
        bff=Bff(AuthorizationStore(),env,'http://fixture.invalid')
        cases=[
            ([urllib.error.HTTPError('http://identity',401,'',{},None)],503,'service_credentials_rejected'),
            ([JsonResponse(b'{"access_token":"fixture"}'),urllib.error.HTTPError('http://authorization',401,'',{},None)],503,'integration_service_unauthorized'),
            ([JsonResponse(b'{"access_token":"fixture"}'),urllib.error.HTTPError('http://authorization',403,'',{},None)],403,'integration_configuration_mismatch'),
            ([JsonResponse(b'{"access_token":"fixture"}'),JsonResponse(b'{"allowed":false}')],403,'capability_denied'),
        ]
        for responses,status,code in cases:
            with self.subTest(code=code):
                queue=iter(responses)
                def request(*_args,**_kwargs):
                    response=next(queue)
                    if isinstance(response,Exception): raise response
                    return response
                bff._request=request
                with self.assertRaises(AuthError) as raised:bff.authorize(AuthorizationHandler(),'xii.certificates.access')
                self.assertEqual((raised.exception.status,raised.exception.code),(status,code))

    def response(self,column,value):
        output=StringIO();writer=csv.writer(output);writer.writerows([['Nome Completo','RA',column],['Participante Fictício','0012345',value]])
        return analyze('exemplo-ficticio.csv',output.getvalue().encode())['records']

    def test_alias_deduplication_and_multiple_modalities(self):
        records=self.response('Se foi atleta/','fut7 2024/1; atleta de Fut7 2024/1')
        self.assertEqual(len(records),1);self.assertEqual(records[0]['detail'],'Futebol 7')
        record=self.response('Se foi atleta/','Fut7 e futsal 2024/1')[0]
        self.assertIn('modalidade',record['warning'])

    def test_description_after_period_and_explicit_event_information(self):
        record=self.response('Se foi atleta/','2024/1 até 2024/2 - atleta de Fut7')[0]
        self.assertEqual(record['detail'],'Futebol 7');self.assertFalse(record['warning'])
        record=self.response('Ação social','Arrecadação 2024/2 12,5 horas')[0]
        self.assertEqual((record['semester'],record['hours']),('2024.2',12.5));self.assertTrue(record['warning'])

    def test_conflicting_hours_and_unconfirmed_period_stay_pending(self):
        for value in ['Fut7 2024/1 150 horas','Fut7 2024 100 horas','Fut7 2024/1 10 h e 20 h']:
            record=self.response('Se foi atleta/',value)[0]
            self.assertTrue(record['warning']);self.assertFalse(record['approved'])

    def test_fictitious_fixture_exact_counts_and_pending_cases(self):
        result=analyze(CSV.name,CSV.read_bytes())
        self.assertEqual((result['responses'],len(result['records']),result['duplicates'],result['people']),(14,31,5,11))
        self.assertEqual(sum(bool(r['warning']) for r in result['records']),12)
        counts={ra:sum(r['ra']==ra for r in result['records']) for ra in ['1000001','1000002','1000003','1000004','1000005','0012345']}
        self.assertEqual(counts,{'1000001':6,'1000002':4,'1000003':6,'1000004':4,'1000005':4,'0012345':1})
        self.assertTrue(all(not r['approved'] for r in result['records']))
        self.assertTrue(all(r['warning'] for r in result['records'] if r['ra']=='1000001'))

    def test_fictitious_xlsx_and_csv_match(self):
        self.assertTrue(XLSX.exists(),'The public fictitious workbook must be included.')
        a=analyze(CSV.name,CSV.read_bytes()); b=analyze(XLSX.name,XLSX.read_bytes())
        self.assertEqual(a['records'],b['records'])
        self.assertEqual(a['duplicate_records'],b['duplicate_records'])

    def test_duplicate_candidates_preserve_source_and_pending_identity(self):
        result=analyze(CSV.name,CSV.read_bytes())
        self.assertEqual(len(result['duplicate_records']),result['duplicates'])
        originals={r['id']:r for r in result['records']}
        for candidate in result['duplicate_records']:
            original=originals[candidate['duplicate_of']]
            self.assertFalse(candidate['approved'])
            self.assertTrue(candidate['source'])
            self.assertTrue(candidate['row'])
            self.assertNotEqual(candidate['id'],original['id'])
            self.assertEqual(candidate['warning'],original['warning'])
            for field in ['name','ra','activity','semester','detail']:
                self.assertEqual(candidate[field],original[field])

    def test_duplicate_response_keeps_conflicting_hours_warning(self):
        output=StringIO();writer=csv.writer(output)
        writer.writerows([['Nome Completo','RA','Se foi atleta/'],
            ['Participante Fictício','0012345','fut7 2024/1'],
            ['Participante Fictício','0012345','atleta de Fut7 2024/1 150 horas']])
        result=analyze('duplicatas-ficticias.csv',output.getvalue().encode())
        self.assertEqual((len(result['records']),result['duplicates']),(1,1))
        self.assertFalse(result['records'][0]['warning'])
        self.assertTrue(result['duplicate_records'][0]['warning'])
        self.assertIn('150',result['duplicate_records'][0]['source'])

    def test_pending_event_editions_do_not_collapse_as_duplicates(self):
        output=StringIO();writer=csv.writer(output)
        writer.writerows([['Nome Completo','RA','Evento esportivo'],
            ['Participante Fictício','0012345','EP 2019'],
            ['Participante Fictício','0012345','EP 2022'],
            ['Participante Fictício','0012345','EP 2023'],
            ['Participante Fictício','0012345','EP 2019']])
        result=analyze('eventos-ficticios.csv',output.getvalue().encode())
        self.assertEqual((len(result['records']),result['duplicates']),(3,1))
        self.assertEqual(
            {record['source'] for record in result['records']},
            {'EP 2019','EP 2022','EP 2023'},
        )
        self.assertEqual(result['duplicate_records'][0]['source'],'EP 2019')

    def test_csv_encodings_and_delimiters(self):
        for delimiter,encoding in [(';','cp1252'),('\t','utf-8-sig'),(',','utf-8')]:
            with self.subTest(delimiter=delimiter,encoding=encoding):
                output=StringIO();writer=csv.writer(output,delimiter=delimiter)
                writer.writerows([['Nome Completo','RA','Se foi membro da XII'],['Érica Exemplo','0012345','Secretaria 2024/1 até 2024/2']])
                records=analyze('ficticio.csv',output.getvalue().encode(encoding))['records']
                self.assertEqual([r['semester'] for r in records],['2024.1','2024.2'])
                self.assertTrue(all(r['ra']=='0012345' and r['name']=='Érica Exemplo' for r in records))

    def test_unknown_date_connector_is_not_treated_as_two_certificates(self):
        for value in ['2023/1 .. 2024/2','2023/1 / 2024/2','2023/1 durante 2024/2']:
            self.assertTrue(periods(value)[1],value)

    def test_import_limits_and_missing_headers(self):
        for data in [b'Nome,RA\nExemplo,12345\n',b'Nome Completo,RA\n',b'Nome Completo,RA\nExemplo,12345\n']:
            with self.assertRaises(ValueError):analyze('ficticio.csv',data)
        with self.assertRaises(ValueError):analyze('ficticio.pdf',b'not a spreadsheet')
        with self.assertRaises(ValueError):analyze('ficticio.csv',('Nome Completo,RA\n'+'Exemplo,12345\n'*5001).encode())

    def test_formula_like_participation_requires_review(self):
        output=StringIO();writer=csv.writer(output);writer.writerows([['Nome Completo','RA','Se foi membro da XII'],['Exemplo','12345','=2024/1']])
        records=analyze('formulas.csv',output.getvalue().encode())['records']
        self.assertIn('fórmula',records[0]['warning'])

class CertificateRegressionTest(unittest.TestCase):
    def test_explicit_aliases_have_one_canonical_description(self):
        for detail in ['fut7','Fut7','FUT 7','atleta de Fut7','futebol society']:
            self.assertEqual(canonical_detail('Atleta',detail),'Futebol 7')
        self.assertEqual(canonical_detail('Atleta','atleta de FUTSAL'),'Futsal')
        self.assertEqual(canonical_detail('Atleta','Fut7 e futsal'),'Fut7 e futsal')
        self.assertEqual(canonical_detail('Atleta','Capitão de Fut7'),'Capitão de Fut7')
        self.assertEqual(canonical_detail('XII','Departamento de secretaria'),'Secretaria')

    def test_duplicate_aliases_cannot_issue_twice(self):
        with self.assertRaisesRegex(ValueError,'repetidas'):
            make_zip([example(activity='Atleta',detail='fut7'),example(activity='Atleta',detail='atleta de Fut7')],'2026-10-03','name')

    def test_normalized_description_matches_pdf_and_manifest(self):
        record=example(activity='Atleta',detail='atleta de Fut7')
        archive=zipfile.ZipFile(BytesIO(make_zip([record],'2026-10-03','name')))
        name=next(n for n in archive.namelist() if n.endswith('.pdf'))
        text=PdfReader(BytesIO(archive.read(name))).pages[0].extract_text()
        self.assertIn('Futebol 7',text);self.assertNotIn('Fut7',text)
        row=next(csv.DictReader(StringIO(archive.read('relatorio.csv').decode('utf-8-sig'))))
        self.assertEqual(row['descricao'],'Futebol 7')

    def test_approval_must_be_boolean_and_pending_cannot_be_exported(self):
        for approval in ['true','false',1,0,None]:
            with self.assertRaises(ValueError):validate_record(example(approved=approval))
        with self.assertRaises(ValueError):make_zip([example(warning='Revisar')],'2026-10-03','name')

    def test_invalid_fields_and_hours_are_rejected(self):
        for changes in [{'hours':True},{'hours':float('nan')},{'hours':float('inf')},{'hours':0.1},{'hours':2001},{'name':'x'*151},{'detail':'x'*351},{'ra':'abc123'},{'semester':'2024.3'},{'activity':'Desconhecida'}]:
            with self.subTest(changes=changes),self.assertRaises(ValueError):validate_record(example(**changes))
        validate_record(example(hours=0.5));validate_record(example(hours=2000))

    def test_all_activity_pdfs_contain_identity_semester_hours_and_date(self):
        for activity in ACTIVITIES:
            with self.subTest(activity=activity):
                document=PdfReader(BytesIO(certificate(example(activity=activity,hours=48.5),'2026-10-03')))
                self.assertEqual(len(document.pages),1)
                text=document.pages[0].extract_text()
                for value in ['ANDRÉ EXEMPLO FICTÍCIO','0012345','2024/2','48.5 horas','3 DE OUTUBRO DE 2026']:
                    self.assertIn(value,text)
                self.assertEqual(tuple(map(int,document.pages[0].mediabox[2:])),(842,595))

    def test_special_characters_are_literal_and_name_uppercase_is_safe(self):
        record=example(name='Ana & Bia <Exemplo>',detail='Secretaria & eventos <fictícios>')
        text=' '.join(PdfReader(BytesIO(certificate(record,'2026-10-03'))).pages[0].extract_text().split())
        self.assertIn('ANA & BIA <EXEMPLO>',text);self.assertIn('Secretaria & eventos <fictícios>',text)

    def test_csv_report_neutralizes_formulas_with_leading_whitespace(self):
        for value in ['=1+1','  =1+1','\t=1+1','+1','-1','@SUM(A1)']:
            archive=zipfile.ZipFile(BytesIO(make_zip([example(source=value)],'2026-10-03','name')))
            report=list(csv.DictReader(StringIO(archive.read('relatorio.csv').decode('utf-8-sig'))))[0]
            self.assertTrue(report['origem'].startswith("'"))

    def test_batch_of_75_pdfs_and_manifest_names_are_consistent(self):
        records=[example(name=f'Participante Fictício {i:03}',ra=f'{1000000+i}') for i in range(75)]
        archive=zipfile.ZipFile(BytesIO(make_zip(records,'2026-10-03','ra')))
        pdfs=[p for p in archive.namelist() if p.endswith('.pdf')]
        report=list(csv.DictReader(StringIO(archive.read('relatorio.csv').decode('utf-8-sig'))))
        self.assertEqual(len(pdfs),75);self.assertEqual(set(pdfs),{r['arquivo'] for r in report})
        self.assertTrue(all(not p.startswith('/') and '..' not in p for p in pdfs))
        self.assertEqual(archive.testzip(),None)

    def test_invalid_date_naming_and_batch_size(self):
        with self.assertRaises(ValueError):certificate(example(),'2026-02-30')
        with self.assertRaises(ValueError):make_zip([example()],'2026-10-03','other')
        with self.assertRaises(ValueError):make_zip([example()]*1001,'2026-10-03','name')

class HttpRegressionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.server.bff=FakeBff()
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.base=f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()

    def request(self,path,payload=None,headers=None):
        data=json.dumps(payload).encode() if payload is not None else None
        req=urllib.request.Request(self.base+path,data=data,headers={'Content-Type':'application/json',**(headers or {})})
        try:return urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req,timeout=20)
        except urllib.error.HTTPError as error:return error

    def setUp(self):
        self.server.bff=FakeBff()

    def test_public_assets_and_private_files(self):
        for path in ['/','/healthz','/assets/honji-symbol.svg','/assets/xii-icon.svg','/assets/favicon.svg','/site.webmanifest']:
            response=self.request(path);self.assertEqual(response.status,200,path);self.assertEqual(response.headers['Cache-Control'],'no-store')
        import re
        html=self.request('/').read().decode()
        compiled=re.findall(r'(?:src|href)="(/static/[^\"]+)"',html)
        self.assertEqual(len(compiled),2)
        for path in compiled:self.assertEqual(self.request(path).status,200,path)
        for path in ['/server.py','/.git/config','/tests/fixtures/participacoes-ficticias.csv','/documentos-certificados/respostas.csv','/../server.py','/frontend/src/App.tsx','/static/../server.py','/static/missing.js','/static/index.js.map']:
            self.assertEqual(self.request(path).status,404,path)

    def test_origin_and_host_checks(self):
        self.assertEqual(self.request('/api/analyze',{}, {'Origin':'https://example.invalid'}).status,403)
        self.assertEqual(self.request('/api/analyze',{}, {'Host':'example.invalid'}).status,403)

    def test_sessionless_and_invalid_callback_are_rejected(self):
        self.server.bff.active=False
        self.assertEqual(self.request('/api/session').status,401)
        self.assertEqual(self.request('/auth/callback?state=invalid&code=ficticio').status,400)

    def test_central_denial_blocks_access_and_issuance(self):
        self.server.bff.denied={'xii.certificates.access'}
        self.assertEqual(self.request('/api/analyze',{}).status,403)
        self.server.bff.denied={'xii.certificates.issue'}
        result=analyze(CSV.name,CSV.read_bytes()); record=next(dict(item,approved=True) for item in result['records'] if not item['warning'])
        self.assertEqual(self.request('/api/generate',{'records':[record],'issued':'2026-10-03','naming':'ra'}).status,403)
        self.assertIsNone(self.server.bff.store.last_audit)

    def test_authorized_issuance_audits_only_subject_and_quantity(self):
        result=analyze(CSV.name,CSV.read_bytes()); record=next(dict(item,approved=True) for item in result['records'] if not item['warning'])
        response=self.request('/api/generate',{'records':[record],'issued':'2026-10-03','naming':'ra'})
        self.assertEqual(response.status,200); response.read()
        self.assertEqual(self.server.bff.store.last_audit,('00000000-0000-4000-8000-000000000001',1))

    def test_logout_invalidates_the_local_session(self):
        headers={'Origin':self.base, 'X-CSRF-Token':'fixture-csrf'}
        self.assertEqual(self.request('/auth/logout',{},headers).status,200)
        self.assertEqual(self.request('/api/session').status,401)

    def test_explicit_public_origin(self):
        self.server.public_origin='https://xii-gabriel.honji.com.br'
        try:
            headers={'Host':'xii-gabriel.honji.com.br','Origin':'https://xii-gabriel.honji.com.br'}
            response=self.request('/api/analyze',{},headers)
            self.assertEqual(response.status,400)
            self.assertNotEqual(json.load(response).get('error'),'Origem não permitida')
            self.assertEqual(self.request('/api/analyze',{}, {'Host':'xii-gabriel.honji.com.br','Origin':'https://example.invalid'}).status,403)
        finally:
            self.server.public_origin=None

    def test_http_import_preview_export_and_clear_validation_errors(self):
        response=self.request('/api/analyze',{'filename':CSV.name,'data':base64.b64encode(CSV.read_bytes()).decode()})
        self.assertEqual(response.status,200);result=json.load(response)
        ready=[dict(r,approved=True) for r in result['records'] if not r['warning']]
        self.assertEqual(len(ready),19)
        preview=self.request('/api/preview',{'record':ready[0],'issued':'2026-10-03'})
        self.assertEqual(preview.headers['Content-Type'],'application/pdf');self.assertEqual(len(PdfReader(BytesIO(preview.read())).pages),1)
        generated=self.request('/api/generate',{'records':ready,'issued':'2026-10-03','naming':'ra'})
        archive=zipfile.ZipFile(BytesIO(generated.read()));self.assertEqual(len([p for p in archive.namelist() if p.endswith('.pdf')]),19)
        invalid=self.request('/api/generate',{'records':[example(approved=False)],'issued':'2026-10-03','naming':'name'})
        self.assertEqual(invalid.status,400);self.assertIn('Aprove',json.load(invalid)['error'])

    def test_normalization_keeps_pending_hours_period_and_approval(self):
        record=example(activity='Atleta',detail='Fut7',approved=False,hours=0,semester='',warning='Confirme período')
        response=self.request('/api/normalize',{'records':[record]})
        result=json.load(response);self.assertEqual(result['changed'],1)
        self.assertEqual(result['records'][0],{**record,'detail':'Futebol 7'})

if __name__=='__main__':unittest.main()
