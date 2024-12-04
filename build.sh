# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate

# Create a superuser non-interactively with hardcoded credentials
python manage.py createsuperuser --noinput --username admin --email admin@example.com || true

# Set the password for the superuser
echo "from django.contrib.auth import get_user_model; User = get_user_model(); user = User.objects.get(username='admin'); user.set_password('1234'); user.save()" | python manage.py shell