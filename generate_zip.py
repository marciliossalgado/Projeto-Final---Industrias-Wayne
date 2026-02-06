import zipfile
import os

def make_zip(output_filename='entrega.zip', source_dir='.'):
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(source_dir):
            # skip venv folder
            if 'venv' in root.split(os.sep):
                continue
            for f in files:
                # skip python cache and hidden files
                if f.endswith('.pyc') or f.startswith('.'):
                    continue
                filepath = os.path.join(root, f)
                arcname = os.path.relpath(filepath, source_dir)
                zf.write(filepath, arcname)
    print(f'Zip criado: {output_filename}')

if __name__ == '__main__':
    make_zip()
