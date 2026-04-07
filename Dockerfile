FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Create entrypoint script for migrations
RUN echo '#!/bin/bash\n\
echo "Starting ReadVault..."\n\
echo "Checking database migrations..."\n\
python migrate_add_type_column.py || true\n\
echo "Starting API server..."\n\
python api.py' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
