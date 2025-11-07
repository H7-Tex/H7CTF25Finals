FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    socat \
    uuid-runtime \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash ctfuser

COPY src/ /home/ctfuser/
COPY entrypoint.sh /entrypoint.sh

WORKDIR /home/ctfuser

RUN chown -R ctfuser:ctfuser /home/ctfuser
RUN chmod +x /entrypoint.sh

EXPOSE 4000

ENTRYPOINT ["/entrypoint.sh"]
