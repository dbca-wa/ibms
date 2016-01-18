import os
from fabric.api import cd, run
from fabric.contrib.files import exists, upload_template

DEPLOY_REPO_URL = os.environ['DEPLOY_REPO_URL']
DEPLOY_TARGET = os.environ['DEPLOY_TARGET']
DEPLOY_VENV_PATH = os.environ['DEPLOY_VENV_PATH']
DEPLOY_VENV_NAME = os.environ['DEPLOY_VENV_NAME']
DEPLOY_DEBUG = os.environ['DEPLOY_DEBUG']
DEPLOY_DATABASE_URL = os.environ['DEPLOY_DATABASE_URL']
DEPLOY_SECRET_KEY = os.environ['DEPLOY_SECRET_KEY']
DEPLOY_CSRF_COOKIE_SECURE = os.environ['DEPLOY_CSRF_COOKIE_SECURE']
DEPLOY_SESSION_COOKIE_SECURE = os.environ['DEPLOY_SESSION_COOKIE_SECURE']
DEPLOY_USER = os.environ['DEPLOY_USER']
DEPLOY_DB_NAME = os.environ['DEPLOY_DB_NAME']
DEPLOY_DB_USER = os.environ['DEPLOY_DB_USER']
DEPLOY_SUPERVISOR_NAME = os.environ['DEPLOY_SUPERVISOR_NAME']


def _get_latest_source():
    run('mkdir -p {}'.format(DEPLOY_TARGET))
    if exists(os.path.join(DEPLOY_TARGET, '.hg')):
        run('cd {} && hg pull -u'.format(DEPLOY_TARGET))
    else:
        run('hg clone {} {}'.format(DEPLOY_REPO_URL, DEPLOY_TARGET))
        run('cd {} && hg update'.format(DEPLOY_TARGET))


def _create_dirs():
    # Ensure that required directories exist.
    with cd(DEPLOY_TARGET):
        run('mkdir -p logs && mkdir -p media')


def _update_venv():
    # Assumes that virtualenv is installed system-wide.
    with cd(DEPLOY_VENV_PATH):
        if not exists('{}/bin/pip'.format(DEPLOY_VENV_NAME)):
            run('virtualenv {}'.format(DEPLOY_VENV_NAME))
        run('{}/bin/pip install -r requirements.txt'.format(DEPLOY_VENV_NAME))


def _setup_env():
    with cd(DEPLOY_TARGET):
        context = {
            'DEPLOY_DEBUG': DEPLOY_DEBUG,
            'DEPLOY_DATABASE_URL': DEPLOY_DATABASE_URL,
            'DEPLOY_SECRET_KEY': DEPLOY_SECRET_KEY,
            'DEPLOY_CSRF_COOKIE_SECURE': DEPLOY_CSRF_COOKIE_SECURE,
            'DEPLOY_SESSION_COOKIE_SECURE': DEPLOY_SESSION_COOKIE_SECURE,
        }
        upload_template('templates/env.jinja', '.env', context, use_jinja=True, backup=False)


def _setup_supervisor_conf():
    with cd(DEPLOY_TARGET):
        context = {
            'DEPLOY_SUPERVISOR_NAME': DEPLOY_SUPERVISOR_NAME,
            'DEPLOY_USER': DEPLOY_USER,
            'DEPLOY_TARGET': DEPLOY_TARGET,
            'DEPLOY_VENV_PATH': DEPLOY_VENV_PATH,
            'DEPLOY_VENV_NAME': DEPLOY_VENV_NAME,
        }
        upload_template(
            'templates/supervisor.jinja', '{}.conf'.format(DEPLOY_SUPERVISOR_NAME),
            context, use_jinja=True, backup=False)


def _chown():
    # Assumes that the DEPLOY_USER user exists on the target server.
    run('chown -R {0}:{0} {1}'.format(DEPLOY_USER, DEPLOY_TARGET))


def _collectstatic():
    with cd(DEPLOY_TARGET):
        run_str = 'source {}/{}/bin/activate && honcho run python manage.py collectstatic --noinput'
        run(run_str.format(DEPLOY_VENV_PATH, DEPLOY_VENV_NAME), shell='/bin/bash')


def _create_db():
    # This script assumes that PGHOST and PGUSER are set.
    db = {
        'NAME': os.environ['DEPLOY_DB_NAME'],
        'USER': os.environ['DEPLOY_DB_USER'],
    }
    sql = '''CREATE DATABASE {NAME} OWNER {USER};
        \c {NAME}'''.format(**db)
    run('echo "{}" | psql -d postgres'.format(sql))


def _migrate():
    with cd(DEPLOY_TARGET):
        run_str = 'source {}/{}/bin/activate && honcho run python manage.py migrate'
        run(run_str.format(DEPLOY_VENV_PATH, DEPLOY_VENV_NAME), shell='/bin/bash')


# --------------------------------------------------
# IBMS-specific scripts
# --------------------------------------------------
def deploy_env():
    """Normally used to deploy a new environment. Won't harm an existing one.
    Example usage: honcho run fab deploy_env --user=root --host=aws-oim-001
    """
    _get_latest_source()
    _create_dirs()
    _update_venv()
    _setup_env()
    _chown()
    _setup_supervisor_conf()  # After the _chown step.
    _collectstatic()


def deploy_db():
    """Normally used to deploy a new database (idempotent).
    Example usage: honcho run fab deploy_db --user=root --host=aws-oim-001
    """
    _create_db()
    _migrate()


def deploy_all():
    """Deploy to a new environment in one step. Non-destructive, but will
    raise lots of errors for an existing environment.
    """
    deploy_env()
    deploy_db()


def deploy_update():
    """Update only: pulls repo changes, runs migrations, runs collectstatic.
    """
    _get_latest_source()
    _update_venv()
    _migrate()
    _collectstatic()
