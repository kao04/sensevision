#!/usr/bin/env bash
set -euo pipefail

echo "Aplicando novos identificadores de boot (PARTUUID)..."
sudo sed -i 's/075c3a1b/2b11452a/g' /mnt/sd_boot/cmdline.txt
sudo sed -i 's/075c3a1b/2b11452a/g' /mnt/sd_root/etc/fstab
sudo chmod 1777 /mnt/sd_root/tmp

echo "Conteúdo atualizado de cmdline.txt:"
cat /mnt/sd_boot/cmdline.txt
echo ""

echo "Conteúdo atualizado de fstab:"
cat /mnt/sd_root/etc/fstab
echo ""

echo "Sincronizando disco..."
sync

echo "Desmontando partições do cartão..."
sudo umount /mnt/sd_boot
sudo umount /mnt/sd_root

echo "=== TUDO PRONTO COM SUCESSO! ==="
