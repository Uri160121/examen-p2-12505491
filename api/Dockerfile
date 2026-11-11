FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends openssh-client \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir -p /root/.ssh \
 && printf 'Host hadoop\n  User hadoopuser\n  IdentityFile /keys/id_ed25519\n  StrictHostKeyChecking no\n  UserKnownHostsFile /dev/null\n  LogLevel ERROR\n' > /root/.ssh/config \
 && chmod 600 /root/.ssh/config
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
ENV PYTHONUNBUFFERED=1
EXPOSE 5000
CMD ["python", "app.py"]
