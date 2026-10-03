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
from server import ACTIVITIES, Handler, ROOT, analyze, certificate, make_zip, periods, validate_record
from pypdf import PdfReader

CSV = ROOT/'tests/fixtures/participacoes-ficticias.csv'
XLSX = ROOT/'outputs/honji-qa-20261003/participacoes-ficticias.xlsx'

def example(**changes):
    record=dict(name='André Exemplo Fictício',ra='0012345',activity='XII',detail='Secretaria',semester='2024.2',hours=100,approved=True,warning='',source='Resposta fictícia')
    record.update(changes)
    return record

class ImportRegressionTest(unittest.TestCase):
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
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.base=f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()

    def request(self,path,payload=None,headers=None):
        data=json.dumps(payload).encode() if payload is not None else None
        req=urllib.request.Request(self.base+path,data=data,headers={'Content-Type':'application/json',**(headers or {})})
        try:return urllib.request.urlopen(req,timeout=20)
        except urllib.error.HTTPError as error:return error

    def test_public_assets_and_private_files(self):
        for path in ['/','/app.js','/assets/honji-symbol.svg','/assets/xii-icon.svg','/assets/favicon.svg','/site.webmanifest']:
            response=self.request(path);self.assertEqual(response.status,200,path);self.assertEqual(response.headers['Cache-Control'],'no-store')
        for path in ['/server.py','/.git/config','/tests/fixtures/participacoes-ficticias.csv','/documentos-certificados/respostas.csv','/../server.py']:
            self.assertEqual(self.request(path).status,404,path)

    def test_origin_and_host_checks(self):
        self.assertEqual(self.request('/api/analyze',{}, {'Origin':'https://example.invalid'}).status,403)
        self.assertEqual(self.request('/api/analyze',{}, {'Host':'example.invalid'}).status,403)

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

if __name__=='__main__':unittest.main()
