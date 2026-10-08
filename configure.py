from pathlib import Path
import secrets
path=Path(__file__).parent
out=path/'.env'
if out.exists():
    print('.env already exists; keeping your current configuration.')
else:
    template=(path/'.env.example').read_text()
    for placeholder in ['replace-with-a-random-64-character-secret','replace-with-a-long-random-secret']:
        template=template.replace(placeholder,secrets.token_urlsafe(48))
    out.write_text(template);out.chmod(0o600)
    print('Created local .env with a new random secret.')
