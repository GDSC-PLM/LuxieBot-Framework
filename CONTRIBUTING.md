### Environment Setup

#### Create Virtual Environment (venv)

```bash
cd ./services/core/
python -m venv .venv
```

#### Activate the Virtual Environment

Depending on your operating system, run **one** of the following:

- **Linux / macOS:**
  ```bash
  source .venv/bin/activate
  ```
- **Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- **Windows (Command Prompt):**
  ```cmd
  .venv\Scripts\activate.bat
  ```

#### Install Dependencies

Make sure your virtual environment is active before running this:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```
