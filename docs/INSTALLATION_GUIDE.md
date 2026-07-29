# Installation Guide

## 1. Prerequisites
- Python 3.10 or newer
- pip (bundled with Python)
- Windows, macOS or Linux

## 2. Get the Project
The project already lives at:
```
C:\Users\HP\OneDrive\Documents\travel-agency
```

## 3. Create a Virtual Environment (recommended)
```bash
# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

## 4. Install Dependencies
```bash
pip install -r requirements.txt
```

## 5. Initialize & Seed the Database
This creates `instance/flyhappy.db` and fills it with 85 destinations, 28 airlines, packages, hotels, testimonials, team members, FAQs, news, gallery images, an admin account, a demo customer account, and sample bookings/payments.

```bash
# Windows PowerShell
$env:FLASK_APP = "run.py"
python -m flask init-db

# macOS / Linux
export FLASK_APP=run.py
python -m flask init-db
```

> Re-running `init-db` **drops and recreates** all tables — use it any time you want a fresh demo dataset.

## 6. Generate Placeholder Images (already done, re-run only if needed)
The repository ships with generated placeholder photography (logo, favicon, hero banner, destination/airline/package/hotel/testimonial/team/news/gallery images) so the site never shows broken images. To regenerate them:
```bash
python scripts/generate_placeholders.py
```
Replace `app/static/images/logo.png` with the real Fly Happy logo whenever it's supplied, then re-run the script if you want the favicon regenerated from it, or simply drop your own `favicon.ico` into `app/static/`.

## 7. Run the Application
```bash
python run.py
```
The site will be available at **http://127.0.0.1:5000**.

## 8. Demo Accounts
| Role | Email | Password |
|---|---|---|
| Admin | admin@flyhappytravels.com | Admin@123 |
| Customer | customer@flyhappytravels.com | Customer@123 |
| Employees (6 staff) | e.g. ahmed.raza@flyhappytravels.com | Employee@123 |

## 9. Common Issues
| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Ensure the virtual environment is activated and `pip install -r requirements.txt` completed successfully. |
| Database appears empty | Run `flask init-db` again — it seeds fresh sample data every time. |
| Port 5000 already in use | Edit `run.py` and change `port=5000` to another port, e.g. `5050`. |
| Images missing | Re-run `python scripts/generate_placeholders.py`. |

## 10. Production Notes
For a real deployment, run behind a production WSGI server instead of the Flask dev server, e.g.:
```bash
pip install waitress
waitress-serve --port=8080 run:app
```
Set a strong, unique `SECRET_KEY` via the `SECRET_KEY` environment variable and set `FLASK_ENV=production` before deploying.
