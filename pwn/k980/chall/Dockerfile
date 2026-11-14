FROM ubuntu:22.04

RUN apt update --fix-missing && \
 apt install -y socat uuid-runtime && \
 rm -rf /var/lib/apt/lists/*

RUN groupadd -r ctf && useradd -r -g ctf ctf

# Copy the challenge binary and required libraries
COPY challenge /home/ctf/challenge
COPY libc.so.6 /home/ctf/libc.so.6
COPY ld-2.35.so /home/ctf/ld-2.35.so
COPY docker-entrypoint.sh /docker-entrypoint.sh

RUN chown root:root /docker-entrypoint.sh && \
    chmod 755 /docker-entrypoint.sh && \
    chown ctf:ctf /home/ctf/challenge && \
    chown ctf:ctf /home/ctf/libc.so.6 && \
    chown ctf:ctf /home/ctf/ld-2.35.so && \
    chmod 777 /home/ctf/challenge && \
    chmod 755 /home/ctf/libc.so.6 && \
    chmod 755 /home/ctf/ld-2.35.so

USER ctf
EXPOSE 1337

ENTRYPOINT ["/docker-entrypoint.sh"]
