#!/usr/bin/env bash
set -euo pipefail

echo "=== Iniciando preparação do Cartão Micro SD (/dev/mmcblk0) ==="

# 1. Desmontar partições montadas do cartão
for m in $(lsblk -n -o MOUNTPOINT /dev/mmcblk0* 2>/dev/null | grep -v '^$'); do
    echo "Desmontando $m..."
    sudo umount -f "$m" || true
done

# 2. Criar nova tabela de partição MBR
echo "Criando tabela de partições no Micro SD..."
sudo parted -s /dev/mmcblk0 mklabel msdos
sudo parted -s -a optimal /dev/mmcblk0 mkpart primary fat32 8192s 1056767s
sudo parted -s -a optimal /dev/mmcblk0 mkpart primary ext4 1056768s 100%
sudo parted -s /dev/mmcblk0 set 1 lba on

sudo partprobe /dev/mmcblk0
sleep 2

echo "Formatando partições..."
sudo mkfs.vfat -F 32 -n bootfs /dev/mmcblk0p1
sudo mkfs.ext4 -F -L rootfs /dev/mmcblk0p2

echo "Criando diretórios temporários e montando..."
sudo mkdir -p /mnt/sd_boot /mnt/sd_root
sudo mount /dev/mmcblk0p1 /mnt/sd_boot
sudo mount /dev/mmcblk0p2 /mnt/sd_root

echo "=== Copiando partição de Boot (/boot/firmware -> /mnt/sd_boot) ==="
sudo rsync -aHAX --delete /boot/firmware/ /mnt/sd_boot/

echo "=== Copiando partição Raiz (/ -> /mnt/sd_root) com rsync ==="
sudo rsync -axHAX --delete / /mnt/sd_root/

echo "Garantindo diretórios do sistema..."
sudo mkdir -p /mnt/sd_root/boot/firmware
sudo mkdir -p /mnt/sd_root/proc /mnt/sd_root/sys /mnt/sd_root/dev /mnt/sd_root/run /mnt/sd_root/tmp /mnt/sd_root/mnt /mnt/sd_root/media
sudo chmod 1777 /mnt/sd_root/tmp

echo "=== Atualizando PARTUUIDs ==="
BOOT_PARTUUID=$(sudo blkid -s PARTUUID -o value /dev/mmcblk0p1)
ROOT_PARTUUID=$(sudo blkid -s PARTUUID -o value /dev/mmcblk0p2)

echo "Novo BOOT_PARTUUID: $BOOT_PARTUUID"
echo "Novo ROOT_PARTUUID: $ROOT_PARTUUID"

# Atualizar cmdline.txt na partição de boot do Micro SD
sudo sed -i -E "s/root=PARTUUID=[^ ]+/root=PARTUUID=${ROOT_PARTUUID}/" /mnt/sd_boot/cmdline.txt

# Atualizar fstab na partição raiz do Micro SD
OLD_BOOT_PARTUUID=$(grep '/boot/firmware' /mnt/sd_root/etc/fstab | awk '{print $1}')
OLD_ROOT_PARTUUID=$(grep -E '\s+/\s+ext4' /mnt/sd_root/etc/fstab | awk '{print $1}')

sudo sed -i "s|${OLD_BOOT_PARTUUID}|PARTUUID=${BOOT_PARTUUID}|" /mnt/sd_root/etc/fstab
sudo sed -i "s|${OLD_ROOT_PARTUUID}|PARTUUID=${ROOT_PARTUUID}|" /mnt/sd_root/etc/fstab

echo "=== Conteúdo do novo cmdline.txt ==="
cat /mnt/sd_boot/cmdline.txt

echo "=== Conteúdo do novo /etc/fstab ==="
cat /mnt/sd_root/etc/fstab

echo "Sincronizando dados em disco..."
sync

echo "Desmontando partições temporárias..."
sudo umount /mnt/sd_boot
sudo umount /mnt/sd_root

echo "=== MIGRAÇÃO CONCLUÍDA COM SUCESSO! ==="
