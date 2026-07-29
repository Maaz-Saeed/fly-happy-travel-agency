# Contributing to Fly Happy International Travels

Thanks for your interest in improving this project. This guide covers how to get set up and submit changes.

## Getting Started

1. Fork the repo and clone your fork.
2. Set up the environment:
   ```bash
   pip install -r requirements.txt
   set FLASK_APP=run.py          # Windows CMD; PowerShell: $env:FLASK_APP="run.py"
   python -m flask init-db       # creates + seeds instance/flyhappy.db
   python run.py                 # http://127.0.0.1:5000
   ```
3. Log in with the demo accounts listed in [README.md](README.md) to explore the customer and admin sides.

## Making Changes

- Create a branch off `main` for your change: `git checkout -b your-feature-name`.
- Keep pull requests focused — one feature or fix per PR.
- Match the existing code style (Flask blueprints under `app/routes/`, SQLAlchemy models in `app/models.py`, Jinja2 templates under `app/templates/`).
- If you change a model, make sure `app/seed.py` still produces valid sample data.

## Before Submitting a PR

Run the same checks CI runs (see `.github/workflows/ci.yml`):
```bash
python -m compileall -q app config.py run.py scripts
flask init-db
python -c "from app import create_app; app = create_app(); assert app.url_map._rules"
```

Push your branch and open a pull request against `main`, describing what changed and why.

## Reporting Issues

Open a [GitHub issue](https://github.com/Maaz-Saeed/fly-happy-travel-agency/issues) with:
- Steps to reproduce
- Expected vs. actual behavior
- Relevant logs or screenshots

## Code of Conduct

This project follows the [Code of Conduct](CODE_OF_CONDUCT.md). Be respectful and constructive, and keep discussion focused on the code and the project.
