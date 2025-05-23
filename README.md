# 🧾 Conversor OFX/OFC para CSV – API Flask

Este projeto é uma API REST simples construída com Flask que converte extratos bancários no formato `.ofx` ou `.ofc` para `.csv`. A API aceita tanto um único arquivo `.ofx` ou `.ofc`, quanto um `.zip` contendo vários desses arquivos. O resultado é um único `.csv` consolidado com todas as transações.

---

## 🚀 Funcionalidades

- ✅ Upload de **arquivo `.zip` com múltiplos `.ofx`/`.ofc`**
- ✅ Upload de **um único arquivo `.ofx` ou `.ofc` diretamente**
- ✅ Conversão para `.csv` com colunas:
  - `Date`, `Amount`, `Payee`, `Memo`, `Arquivo`
- ✅ Resposta direta com o `.csv` para download

---

## 🛠️ Requisitos

- Python 3.10+
- Docker (opcional)

---

## 🔧 Instalação manual (modo dev)

```bash
git clone https://github.com/thimisul/conversor-ofx-api.git
cd conversor-ofx-api

python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

pip install -r requirements.txt

python app.py
```

---

## ▶️ Executar com Docker

```bash
docker build -t conversor-ofx-csv .
docker run -p 5000:5000 conversor-ofx-csv

```
## Api
```bash
POST /upload
curl -X POST -F 'file=@extratos.zip' http://localhost:5000/upload --output resultado.csv
```

## 🔄 Casos de uso comuns
-  Automação de rotinas financeiras
- Conversão em massa de extratos bancários
