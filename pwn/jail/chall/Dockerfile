FROM ubuntu:22.04

RUN apt update --fix-missing && \
 apt install -y socat uuid-runtime && \
 rm -rf /var/lib/apt/lists/*

RUN groupadd -r ctf && useradd -r -g ctf ctf

COPY challenge /home/ctf/challenge
COPY docker-entrypoint.sh /docker-entrypoint.sh

RUN chown root:root /docker-entrypoint.sh && \
    chmod 755 /docker-entrypoint.sh && \
    chown ctf:ctf /home/ctf/challenge && \
    chmod 555 /home/ctf/challenge

USER ctf
EXPOSE 1337

ENTRYPOINT ["/docker-entrypoint.sh"]
