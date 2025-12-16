# Headball Voli UAS

Game 2D sederhana bertema voli menggunakan karakter kepala (headball) yang dibuat dengan Python dan Pygame sebagai tugas UAS. [file:12][web:16]

## Fitur

- Mode 2 pemain lokal (P1 vs P2) di satu keyboard. [file:12]  
- Fisika bola dengan gravitasi, pantulan dinding, dan interaksi dengan net. [file:12]  
- Gerakan karakter: berjalan, lompat, dan smash di udara. [file:12]  
- Sistem skor hingga 25 poin dengan layar kemenangan dan efek suara. [file:12]  
- Power up acak yang menambah kecepatan gerak pemain. [file:12]  
- Penerapan OOP Python: superclass GameObject, turunan Character, Player, Ball, PowerUp, serta enkapsulasi dengan method get_...() dan set_...(). [file:12][web:9]

## Teknologi

- *Python 3.x*  
- *Pygame* sebagai library utama untuk grafis, input, dan audio. [file:12][web:16]

## Cara Instalasi

1. Pastikan Python 3 sudah terpasang di komputer. [web:16]  
2. Pasang Pygame melalui pip
3. Clone atau download repositori ini, lalu pastikan struktur folder seperti berikut: [file:12][web:18]


## Cara Menjalankan

Masuk ke folder proyek, lalu jalankan: [file:12][web:22]


Kontrol default:

- *P1*: A (kiri), D (kanan), W (lompat), S (smash). [file:12]  
- *P2*: ← (kiri), → (kanan), ↑ (lompat), ↓ (smash). [file:12]

Bola yang jatuh di sisi kiri memberi poin ke Player 2, dan sebaliknya; pemain pertama yang mencapai 25 poin menang. [file:12]

## Struktur Kode (Singkat)

- GameObject  
  - Kelas dasar dengan posisi, ukuran, dan method get_...()/set_...() untuk enkapsulasi. [file:12][web:9]  
- Character  
  - Mengatur fisika karakter (gravitasi, lompat, batas layar) dan efek squash/stretch saat lompat. [file:12]  
- Player  
  - Meng-handle input keyboard, smash, dan skor. [file:12]  
- Ball  
  - Mengatur fisika bola, pantulan dinding/net, dan tabrakan dengan pemain (kepala, badan, smash). [file:12]  
- PowerUp  
  - Muncul secara acak dan menambah kecepatan pemain yang menyentuhnya. [file:12]
