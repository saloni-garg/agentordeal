FROM python:3.12-slim
LABEL org.opencontainers.image.title="agent-ordeal" \
      org.opencontainers.image.description="Adversarial testing harness for AI agents and MCP servers, with a graded scorecard" \
      org.opencontainers.image.licenses="MIT"
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY agentordeal ./agentordeal
RUN pip install --no-cache-dir . && rm -rf /app
WORKDIR /work
ENTRYPOINT ["agentordeal"]
CMD ["--help"]
