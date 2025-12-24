import os
import shutil
import unittest
import json
from app import app, apply_rules

class TestFileRenamer(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(os.getcwd(), 'test_files')
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        
        # Create dummy files
        self.files = ['image1.jpg', 'image2.png', 'doc.txt']
        for f in self.files:
            with open(os.path.join(self.test_dir, f), 'w') as fh:
                fh.write('content')
                
        self.app = app.test_client()

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_list_files(self):
        response = self.app.post('/api/files', json={'directory': self.test_dir})
        data = response.get_json()
        self.assertEqual(len(data['files']), 3)
        self.assertIn('image1.jpg', data['files'])

    def test_apply_rules_replace(self):
        rules = [{'type': 'replace', 'old': 'image', 'new': 'photo'}]
        new_name = apply_rules('image1.jpg', rules)
        self.assertEqual(new_name, 'photo1.jpg')

    def test_apply_rules_counter(self):
        rules = [{'type': 'new_name', 'name': 'vacation'}, 
                 {'type': 'counter', 'start': 1, 'padding': 2, 'separator': '_'}]
        new_name = apply_rules('image1.jpg', rules, index=0)
        self.assertEqual(new_name, 'vacation_01.jpg')
        
        new_name_2 = apply_rules('image2.png', rules, index=1)
        self.assertEqual(new_name_2, 'vacation_02.png')

    def test_preview_api(self):
        rules = [{'type': 'replace', 'old': 'image', 'new': 'photo'}]
        response = self.app.post('/api/preview', json={'directory': self.test_dir, 'rules': rules})
        data = response.get_json()
        preview = data['preview']
        self.assertEqual(len(preview), 3)
        # Sorted: doc.txt, image1.jpg, image2.png
        self.assertEqual(preview[1]['new'], 'photo1.jpg')
        self.assertTrue(preview[1]['changed'])
        self.assertEqual(preview[0]['new'], 'doc.txt') # doc.txt doesn't have 'image'
        self.assertFalse(preview[0]['changed'])

    def test_rename_api(self):
        rules = [{'type': 'replace', 'old': 'image', 'new': 'photo'}]
        response = self.app.post('/api/rename', json={'directory': self.test_dir, 'rules': rules})
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['renamed'], 2)
        
        # Check actual files
        files = os.listdir(self.test_dir)
        self.assertIn('photo1.jpg', files)
        self.assertIn('photo2.png', files)
        self.assertIn('doc.txt', files)
        self.assertNotIn('image1.jpg', files)

if __name__ == '__main__':
    unittest.main()
