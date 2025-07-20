import os
import csv
from PyPDF2 import PdfReader

# ---------------- AYARLAR ----------------
PUBLICATIONS_DIR = os.path.join('data', 'publications')
OUTPUT_CSV      = os.path.join('data', 'professors.csv')
# -----------------------------------------

# 1) CSV dosyasını baştan yaz: başlık satırı ekle
with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as fout:
    writer = csv.writer(fout)
    writer.writerow(['id', 'name', 'publications'])

    prof_id = 1

    # 2) Her profesör klasörünü dolaş
    for prof_name in sorted(os.listdir(PUBLICATIONS_DIR)):
        prof_folder = os.path.join(PUBLICATIONS_DIR, prof_name)
        if not os.path.isdir(prof_folder):
            continue

        titles = []
        # 3) Her PDF’i oku
        for fname in os.listdir(prof_folder):
            if not fname.lower().endswith('.pdf'):
                continue
            path = os.path.join(prof_folder, fname)
            try:
                reader = PdfReader(path)
                meta = reader.metadata or {}
                # 4) Metadata.title varsa al, yoksa ilk satırı
                title = meta.get('/Title', None)
                if not title:
                    text = reader.pages[0].extract_text() or ''
                    title = text.strip().split('\n')[0]
                titles.append(title)
            except Exception as e:
                print(f"⚠️ Hata {fname} için:", e)

        # 5) Yayınları noktalı virgülle birleştir
        pubs_str = '; '.join(titles)
        # 6) CSV’ye satırı yaz
        writer.writerow([prof_id, prof_name, pubs_str])
        print(f"✔️ {prof_name} ({len(titles)} yayın) eklendi.")
        prof_id += 1

print(f"\n🎉 Tamamlandı! {prof_id-1} öğretim üyesi CSV’ye yazıldı.")
