# 4peiron-labs の調査用コンテナ。どのラボもこのイメージに証拠を読み取り専用でつないで使う。
FROM debian:bookworm-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      python3 jq less file sqlite3 procps vim-tiny ca-certificates bsdextrautils \
      libimage-exiftool-perl \
 && rm -rf /var/lib/apt/lists/*
RUN useradd -m -s /bin/bash analyst
USER analyst
WORKDIR /evidence
CMD ["sleep", "infinity"]
