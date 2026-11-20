# 4peiron-labs の調査用コンテナ。どのラボもこのイメージに証拠を読み取り専用でつないで使う。
FROM debian:bookworm-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      python3 jq less file sqlite3 procps vim-tiny ca-certificates bsdextrautils \
      libimage-exiftool-perl \
 && rm -rf /var/lib/apt/lists/*
# イメージの版。変えたら、どのラボの compose.yaml の image: の版も同じにする（tools/check_labs.py が確かめる）。
# 動作確認用の合言葉（#405）にも入るので、古いイメージのまま動かしているとサイトで分かる
ENV LABS_IMAGE_VERSION=3
# シェルを開いたら、動作確認用の合言葉を出す（lab-check.sh）
COPY lab-check.sh /usr/local/bin/lab-check
RUN chmod 755 /usr/local/bin/lab-check \
 && printf '\n# 4peiron-labs: 動作確認用の合言葉を出す\n[ -n "$PS1" ] && /usr/local/bin/lab-check\n' >> /etc/bash.bashrc
RUN useradd -m -s /bin/bash analyst
USER analyst
WORKDIR /evidence
CMD ["sleep", "infinity"]
