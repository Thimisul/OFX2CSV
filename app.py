from flask import Flask, request, send_file
import tempfile
import zipfile
from pathlib import Path
import ofxparse
import csv
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return '''
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <title>Conversor OFX para CSV</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f9fafb;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }

                .container {
                    background-color: #ffffff;
                    padding: 2rem 3rem;
                    border-radius: 1rem;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                    width: 100%;
                    max-width: 400px;
                }

                h1 {
                    text-align: center;
                    color: #111827;
                    margin-bottom: 1.5rem;
                    font-size: 1.5rem;
                }

                form {
                    display: flex;
                    flex-direction: column;
                    gap: 1rem;
                }

                input[type="text"],
                input[type="file"] {
                    padding: 0.75rem;
                    border: 1px solid #d1d5db;
                    border-radius: 0.5rem;
                    font-size: 1rem;
                }

                input[type="submit"] {
                    padding: 0.75rem;
                    background-color: #3b82f6;
                    color: white;
                    font-size: 1rem;
                    border: none;
                    border-radius: 0.5rem;
                    cursor: pointer;
                    transition: background-color 0.3s ease;
                }

                input[type="submit"]:hover {
                    background-color: #2563eb;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Conversor OFX para CSV</h1>
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <input type="text" name="bank" placeholder="Banco" required>
                    <input type="file" name="file" accept=".zip,.ofx,.ofc" required>
                    <input type="submit" value="Enviar">
                </form>
            </div>
        </body>
        </html>
    '''


def write_ofx_to_csv(writer, file_path, bank):
    try:
        with open(file_path, 'r', encoding='utf-8') as ofx_file:
            ofx = ofxparse.OfxParser.parse(ofx_file)
            for txn in ofx.account.statement.transactions:
                bank_deposit = ''
                bank_withdraw = ''
                if txn.amount < 0:
                    bank_withdraw = bank
                else:
                    bank_deposit = bank
                writer.writerow([
                    txn.date.strftime('%Y-%m-%d'),
                    txn.amount,
                    txn.memo or '',
                    bank_withdraw,
                    bank_deposit,
                    Path(file_path).name
                ])
    except Exception as e:
        print(f"Erro no arquivo {file_path}: {e}")

def convert_zip_to_csv(bank, zip_file_path):
    tmp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")

    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        all_files = list(Path(tmpdir).rglob('*.[Oo][Ff][Xx]')) + list(Path(tmpdir).rglob('*.[Oo][Ff][Cc]'))

        with open(tmp_output.name, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Date', 'Amount', 'Memo', 'BankWithdraw', 'BankDeposit', 'Arquivo'])

            for file_path in all_files:
                write_ofx_to_csv(writer, file_path, bank)

    return tmp_output.name

def convert_single_ofx(bank, file_path):
    tmp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")

    with open(tmp_output.name, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Date', 'Amount', 'Memo', 'BankWithdraw', 'BankDeposit', 'Arquivo'])
        write_ofx_to_csv(writer, file_path, bank)

    return tmp_output.name

@app.route('/upload', methods=['POST'])
def upload_file():
    bank = request.form.get('bank')
    if 'file' not in request.files:
        return {'error': 'Nenhum arquivo enviado'}, 400

    uploaded_file = request.files['file']
    filename = uploaded_file.filename.lower()

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, filename)
        uploaded_file.save(file_path)

        if filename.endswith('.zip'):
            output_csv = convert_zip_to_csv(bank, file_path)
        elif filename.endswith('.ofx') or filename.endswith('.ofc'):
            output_csv = convert_single_ofx(bank, file_path)
        else:
            return {'error': 'Formato de arquivo não suportado. Use .zip, .ofx ou .ofc'}, 400

        return send_file(output_csv, mimetype='text/csv', as_attachment=True, download_name='saida.csv')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
