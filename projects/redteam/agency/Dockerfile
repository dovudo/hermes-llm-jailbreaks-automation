FROM python:3.12-slim
WORKDIR /srv
COPY tool_server.py /srv/tool_server.py
EXPOSE 8123
# no shell tools, no curl — container cannot reach out
USER 65534:65534
CMD ["python3", "/srv/tool_server.py"]