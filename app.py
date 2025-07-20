from flask import Flask, render_template, request, redirect, url_for
from models import db, Professor
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import redirect, url_for
from flask import render_template_string
import csv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///danisman.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# ------------- Veri Yükleme -------------
def load_data():
    df = pd.read_csv('data/professors.csv')  # id,name,publications sütunlu
    for _, row in df.iterrows():
        prof = Professor(id=row['id'], name=row['name'],
                         publications=row['publications'])
        db.session.merge(prof)
    db.session.commit()

    # -- 5) Hoca Ekleme formu ve işlemi --
@app.route('/add', methods=['GET', 'POST'])
def add_professor():
    if request.method == 'POST':
        # Formdan gelen verileri al
        new_id = int(request.form['id'])
        new_name = request.form['name']
        new_pubs = request.form['publications']
        # Veritabanına ekle
        prof = Professor(id=new_id, name=new_name, publications=new_pubs)
        db.session.add(prof)
        db.session.commit()
         # --- 2) CSV dosyasına da ekle ---
        # 'data/professors.csv' dosyasını append modunda açıp yeni satırı yazıyoruz
        with open('data/professors.csv', mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            # publications alanında ; kullanıldığı için tırnaklamak yeterli
            writer.writerow([new_id, new_name, new_pubs])
        return redirect(url_for('index'))
    # GET ise formu göster
    return """
    <h2>Yeni Hoca Ekle</h2>
    <form method="post">
      <label>ID:</label><input name="id"><br>
      <label>Ad Soyad:</label><input name="name"><br>
      <label>Yayınlar (;) ile ayır:</label><br>
      <textarea name="publications" rows="4" cols="50"></textarea><br>
      <button type="submit">Ekle</button>
    </form>
    """
@app.route('/list')
def list_profs():
    profs = Professor.query.all()
    return '<br>'.join(f"{p.id}: {p.name}" for p in profs)

# ------------- TF-IDF Hesaplama (Başlangıçta) -------------
def build_tfidf():
    profs = Professor.query.all()
    texts = [p.publications for p in profs]
    vec = TfidfVectorizer()
    tfidf_matrix = vec.fit_transform(texts)
    return vec, tfidf_matrix, profs

# ------------- Eşleştirme Fonksiyonu -------------
def match_professor(user_text, vec, tfidf_matrix, profs, top_n=3):
    user_vec = vec.transform([user_text])
    sims = cosine_similarity(user_vec, tfidf_matrix)[0]
    # en yüksek benzerlik skoruna göre sırala
    ranked = sorted(zip(profs, sims), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]

# ------------- Route’lar -------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        proje_descr = request.form['proje']
        vec, tfidf_matrix, profs = build_tfidf()
        matches = match_professor(proje_descr, vec, tfidf_matrix, profs)
        return render_template('result.html', matches=matches)
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Veritabanı ve tablolar oluşturuldu: danisman.db")
        load_data()
    app.run(debug=True)
