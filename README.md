# Joe Web

## Setting up a new instance
### Creating a virtual environment
1. Install `pipenv` and install the requirements:

   ```bash
   pip install pipenv
   pipenv install -r requirements.txt
   pipenv shell
   ```

### Creating a superuser
2. Create a superuser with `manage.py`

   ```bash
   python manage.py createsuperuser
   ```

### Setting Up Environment Variables
3. Copy `.env.template` to `.env`:

   ```bash
   cp .env.template .env
   ```
   Then replace any fields labelled `# REPLACE`.

   These can be found in the directories: `joeweb` and `statusdisplay`.
