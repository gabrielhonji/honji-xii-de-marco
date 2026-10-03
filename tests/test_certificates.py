import unittest
import sys
from pathlib import Path
from io import BytesIO
import zipfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from server import periods, split_participations, analyze, make_zip, validate_record, ROOT

class CertificatesTest(unittest.TestCase):
    def test_roles_and_parentheses_preserve_context(self):
        self.assertEqual(len(split_participations('Departamento de E-sports (antes da hunter, quando era junto ainda) de 2020/1 a 2021/1')),1)
        self.assertEqual(len(split_participations('presidente 2024/1 até 2024/2 e conselheiro 2024/2 até 2025/2')),2)
        self.assertEqual(split_participations('Sim, membro de 2023/1 até 2024/1'),['membro de 2023/1 até 2024/1'])
    def test_inclusive_range_and_zero_padded_semester(self):
        self.assertEqual(periods('E-atleta 2020/02 até 2023/02')[0],['2020.2','2021.1','2021.2','2022.1','2022.2','2023.1','2023.2'])
    def test_ambiguous_periods_stay_pending(self):
        for value in ['secretaria 2022/2 2023/2','membro desde junho/2024','Atleta 2023','Atleta 2022, 2023, 2024/1','2025/2 até 2024/1']:
            self.assertTrue(periods(value)[1],value)
    def test_single_semesters_are_not_filled_in(self):
        self.assertEqual(periods('2023/1 e 2024/2')[0],['2023.1','2024.2'])
    def test_csv_and_xlsx_agree(self):
        csvfile=ROOT/'tests/fixtures/participacoes-ficticias.csv'
        xlsxfile=ROOT/'outputs/honji-qa-20261003/participacoes-ficticias.xlsx'
        a=analyze(csvfile.name,csvfile.read_bytes());b=analyze(xlsxfile.name,xlsxfile.read_bytes())
        self.assertEqual(a['responses'],14)
        self.assertEqual([(r['ra'],r['activity'],r['semester']) for r in a['records']],[(r['ra'],r['activity'],r['semester']) for r in b['records']])
        self.assertTrue(all(not r['approved'] for r in a['records']))
    def test_zip_collision_and_pdf_content(self):
        from pypdf import PdfReader
        r=dict(name='Marina Exemplo Fictícia',ra='0012345',activity='Pantercats',semester='2022.1',detail='Cheerleader',hours=100,approved=True)
        archive=zipfile.ZipFile(BytesIO(make_zip([r,r],'2026-10-02','ra')))
        pdfs=[n for n in archive.namelist() if n.endswith('.pdf')]
        self.assertEqual(len(set(pdfs)),2)
        self.assertIn('0012345 - pantercats - 2022.1.pdf',pdfs[0])
        page=PdfReader(BytesIO(archive.read(pdfs[0]))).pages[0]
        self.assertIn('0012345',page.extract_text());self.assertIn('2022/1',page.extract_text())
        self.assertIn('relatorio.csv',archive.namelist())
    def test_invalid_or_unapproved_cannot_be_issued(self):
        with self.assertRaises(ValueError):validate_record({'approved':False})
        with self.assertRaises(ValueError):make_zip([],'2026-10-02','name')

if __name__=='__main__':unittest.main()
