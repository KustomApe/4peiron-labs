#!/bin/sh
# 動作確認用の合言葉を出す（4peiron.dev #405）。
# シェルを開いたときに出る（/etc/bash.bashrc）。あとから `lab-check` と打っても出る。
#
# 合言葉は、ラボごとの LAB_CHECK（compose.yaml）と、このイメージの版（LABS_IMAGE_VERSION）でできている。
# サイトのラボのページに入れると、「正しいラボを、新しいイメージで、証拠をつないで起動できた」ことが分かる。
# 点数にはならない。証拠がつながっていないときは、合言葉の代わりに直し方を出す。
if [ -z "$LAB_CHECK" ]; then
  echo "このコンテナには動作確認用の合言葉がありません（compose.yaml の LAB_CHECK）。"
  echo "This container has no check phrase (LAB_CHECK in compose.yaml)."
  exit 1
fi
if [ -z "$(ls -A /evidence 2>/dev/null)" ]; then
  echo "/evidence が空です。ラボのディレクトリ（compose.yaml のある所）で docker compose up -d を流したかを確かめてください。"
  echo "/evidence is empty. Make sure you ran docker compose up -d in the lab directory (where compose.yaml is)."
  exit 1
fi
echo "---------------------------------------------------------------"
echo " 動作確認用の合言葉 / Check phrase:  4P-CHECK{${LAB_CHECK}-v${LABS_IMAGE_VERSION}}"
echo " サイトのラボのページに入れると、環境が正しく動いているかを確かめられます（点数にはなりません）。"
echo " Enter it on the lab page to confirm your environment works (no points)."
echo "---------------------------------------------------------------"
