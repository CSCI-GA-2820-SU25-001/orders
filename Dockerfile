##################################################
# Create production image
##################################################
FROM quay.io/rofrano/python:3.11-slim

# Set up the Python production environment
WORKDIR /app
COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip pipenv && \
    pipenv install --system --deploy

# Copy the application contents
COPY wsgi.py .
COPY service ./service

# Switch to a non-root user and set file ownership
RUN useradd --uid 1001 flask && \
    chown -R flask /app
USER flask

# Expose any ports the app is expecting in the environment
ENV FLASK_APP="wsgi:app"
ENV PORT=8080
EXPOSE $PORT

ENTRYPOINT ["gunicorn"]
CMD ["--bind=0.0.0.0:8080", "--log-level=info", "wsgi:app"]
