import os
import re
import json
from collections import defaultdict
from docx import Document

# --- AYARLAR ---
ANA_KLASOR_YOLU = r"C:\Users\yunus\OneDrive\Desktop\DATABASE\tbmm_tutanak"
CIKTI_YOLU = os.path.join(os.environ["USERPROFILE"], "Desktop", "veri.json")

# --- YIL HARİTASI (TBMM Dönem Başlangıçları) ---
# Mantık: Dönem başlangıç yılı + (Yasama Yılı - 1)
DONEM_BASLANGICLARI = {
    "21": 1999,
    "22": 2002,
    "23": 2007,
    "24": 2011,
    "25": 2015, # Kısa dönem
    "26": 2015, # Kasım sonrası
    "27": 2018,
    "28": 2023
}

DUR_KELIMELERI = {
    # --- YENİ EKLENEN: Liste ve Tutanak Kirliliği ---
    "sorusu", "cevabı", "ilişkin", "dair", "esas", "numaralı", "sıra", "sayısı",
    "gelen", "kağıtlar", "kâğıtlar", "yoklama", "sunuşları", "gündem", "gündemi",
    "özeti", "bölümü", "kabul", "edenler", "etmeyenler", "oylama", "oy",
    "birleşim", "oturum", "dönem", "yasama", "yılı", "cilt", "tutanak", "dergisi",
    "komisyonu", "komisyon", "bakanlığı", "bakanı", "vekili", "milletvekili",
    "açıldı", "kapandı", "verildi", "sunulmuştur", "okutuyorum", "buyurun",

    # Standart Bağlaçlar
    "ve", "veya", "ile", "bir", "bu", "şu", "o", "de", "da", "ki", "mi", "mu", "mı",
    "mü", "ama", "fakat", "lakin", "ancak", "için", "gibi", "kadar", "olan", "olarak",
    "var", "yok", "daha", "en", "çok", "az", "ise", "diye", "ne", "neden", "niçin",
    "nasıl", "ben", "sen", "o", "biz", "siz", "onlar", "bunu", "şunu", "buna", "şuna",
    "böyle", "şöyle", "her", "hepsini", "hiç", "yine", "zaten", "bile", "eğer", "sanki",
    "belki", "çünkü", "yani", "dolayı", "tarafından", "üzerine", "halde", "bütün",
    "tüm", "diğer", "bazı", "şey", "şeyler", "lazım", "gerekiyor", "dedi", "diyor", "dendi", 
    "denildi", "söyledi", "niye", "herhalde", "belli", "sanarsın", "besbelli", "sayesinde", 
    "yüzünden", "sebep", "sebebiyle", "sonucuyla", "netice", "neticesinde", 
    
    # Hitap ve Unvanlar
    "sayın", "sayin", "baskan", "başkan", "baskani", "başkanı", "değerli", "muhterem",
    "arkadaşlar", "arkadaş", "milletvekili", "vekili", "vekil", "üye", "üyeleri",
    "bakan", "bakanı", "başbakan", "cumhurbaşkanı", "divan", "katip", "efendim", "burada", 
    "şimdi", "bugün", "yüzde", "onlarca", "yine", "tane", "buyurun", "ikinci", "birinci", 
    "dün", "yarın", "orada", "milletvekilleri", "nin", "nun", "nün", "nın", "nci", "ncu", 
    "ncı", "üncü", "uncu", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", 
    "dokuz", "on", "oylarınıza", "bakanlığı", "özellikle", "sadece", "imk", "hem", "hiçbir", 
    "herşey", "maddesinin", "maddeyi", "aşağıdaki", "konunun", "saygıyla", "onun", 
    "arkadaşlarım", "biraz", "fazla", "yerine", "dolayısıyla", "rağmen", "ragmen", "hangi", 
    "süreniz", "mikrofon", "mikrofonunuz", "otomatik", "cevabı", "bakanı", "bakani", "bakan", 
    "nedeniyle", "anda", "cidd", "amacıyla", "şte", "tam", "herhangi", "smail", "bedük", 
    "geri", "adina", "adına", "müdürlük", "mudurluk", "müdürlüğü", "mudurlugu", "müdürlüğe", 
    "mudurluge", "müdürlüğüne", "mudurlugune", "müdürlüğünün", "mudurlugunun", "müdürlüğünde", 
    "mudurlugunde", "maddesinde", "maddesinin", "size", "türlü", "bilgilerinize", "kurum", 
    "kim", "ait", "ayrı", "onu", "kişi", "kamer", "başkanvekili", "baskanvekılı", "başkanlığı", 
    "size", "bize", "beri", "komple", "lişkin", "vek", "öyle", "böyle", "şöyle", "başkanım", 
    "mutlaka", "maddesine", "evvel", "peki", "maddede", "dakika", "dakikadır", "dakikanız", 
    "gündeme", "ilave", "elde", "hep", "nedir", "gündemdışı", "ayrılan", "çişleri", "önergeye", 
    "ele", "bana", "sana", "süresi", "veriyorum", "gereğince", "tip", "onaylanmasının", 
    "arkadaşının", "böylece", "dan", "maddeyle", "sonucu", "rica", "prof", "syonu", "sayı", 
    "maddeleri", "mıdır", "mudur", "midir", "müdür", "vesileyle", "lgi", "defa", "uyarınca", 
    "söylüyorum", "isteyen", "katılıyoruz", "kü", "bugünkü", "yaşını", "vardır", "yoktur", 
    "hük", "göre", "bakın", "bizim", "inci", "mill", "anda", "tek", "nce", "hasi", "imk", 
    "eli", "den", "dan", "şandır", "syonu", "deki", "daki", 
    
    # Meclis Prosedürü
    "madde", "maddesi", "fıkra", "bendi", "bent", "geçici", 
    "tasarı", "tasarısı", "teklif", "teklifi", "önerge", "önergesi",
    "komisyon", "komisyonu", "hükümet", "grubu", "parti", "partisi", "adına", "şahsı",
    "genel", "kurul", "kurulu", "birleşim", "oturum", "dönem", "yasama", "yılı",
    "gündem", "sıra", "sayısı", "esas", "usul", "hakkında", "konusunda", "ilgili", "heyet", 
    "heyetinizi", "huzurunuzda", "dışı", "dısı", "istiyorum", "isterim", "karar", "yeter", 
    "sayısı", "sayisi", "savcı", "hakim", "avukat", 
    
    # Oylama ve Kapanış Jargonu
    "kabul", "edenler", "etmeyenler", "ret", "oy", "birliği", "çokluğu",
    "arz", "ederim", "ediyorum", "sunuyorum", "saygılar", "saygılarımla", "selamlıyorum",
    "devamla", "alkışlar", "gürültüler", "konuşma", "söz", "cevap", "soru",
    
    # Gereksiz Fiilimsiler ve Zaman
    "olan", "olduğu", "olduğunu", "olmadığını", "yapılan", "edilen", "gelen", "giden",
    "yıl", "sene", "gün", "tarih", "önce", "sonra", "içinde", "arasında", "altında",
    "birinci", "ikinci", "üçüncü", "dördüncü", "beşinci"
}

def cop_satir_mi(satir):
    s = satir.lower().strip()
    if len(s) < 5: return True
    if "ilişkin sorusu" in s and "cevabı" in s: return True
    if re.match(r"^[ivx]+\.\-", s): return True
    if s.startswith(("dönem :", "yasama yılı :", "cilt :", "t. b. m. m.")): return True
    return False

def docx_oku_ve_temizle(dosya_yolu):
    kelimeler = []
    try:
        doc = Document(dosya_yolu)
        for para in doc.paragraphs:
            satir = para.text
            if cop_satir_mi(satir): continue
            bulunanlar = re.findall(r'[a-zçğıöşü]+', satir.lower())
            for k in bulunanlar:
                if k not in DUR_KELIMELERI and len(k) > 2:
                    kelimeler.append(k)
    except Exception as e:
        print(f"Hata ({os.path.basename(dosya_yolu)}): {e}")
    return kelimeler

def yil_hesapla(donem_str, yasama_yili_str):
    try:
        # Klasör adından sayıları ayıklama (Düzeltilmiş Versiyon)
        # Örn: "21_donem" -> 21'i alır.
        donem_no = donem_str.split('_')[0] 
        
        # Örn: "21_2_yasama_yili" -> Alt çizgileri ayırır, ortadaki "2"yi alır.
        # ["21", "2", "yasama", "yili"] -> 1. indeks "2" olur.
        if "_" in yasama_yili_str:
            yasama_no = yasama_yili_str.split('_')[1]
        else:
            # Eğer klasör adı farklıysa (eski usul regex)
            yasama_no = re.search(r'\d+', yasama_yili_str).group()

        baslangic = DONEM_BASLANGICLARI.get(donem_no)
        
        if baslangic:
            # 25. ve 26. dönem özel durumları
            if donem_no == "25": return 2015
            if donem_no == "26": return 2016 + (int(yasama_no) - 1)
            
            gercek_yil = baslangic + int(yasama_no) - 1
            return gercek_yil
        else:
            return f"{donem_no}-{yasama_no}"
            
    except Exception as e:
        print(f"Yıl hesaplama hatası: {e} (Klasör: {yasama_yili_str})")
        return "Bilinmeyen"

def ana_islem():
    print("--- GELİŞMİŞ ANALİZ (YIL BAZLI) BAŞLIYOR ---")
    
    # Yeni Yapı: { "kelime": { "1999": {"count": 50, "meta": "21. Dönem...", "files": 10} } }
    GENEL_SOZLUK = defaultdict(lambda: defaultdict(lambda: {"count": 0, "meta": "", "files": 0}))
    
    # Yıllara göre dosya sayılarını tutmak için
    DOSYA_SAYACLARI = defaultdict(int)

    for kok_dizin, alt_dizinler, dosyalar in os.walk(ANA_KLASOR_YOLU):
        docx_dosyalari = [d for d in dosyalar if d.endswith(".docx")]
        
        if not docx_dosyalari: continue

        # Klasör isminden yıl bulmaca
        try:
            yol_parcalari = kok_dizin.split(os.sep)
            # Klasör yapına göre son iki klasörü alıyoruz
            donem = yol_parcalari[-2] # 21_donem
            yasama = yol_parcalari[-1] # 21_1_yasama_yili
            
            hesaplanan_yil = str(yil_hesapla(donem, yasama))
            meta_etiket = f"{donem.replace('_', ' ').title()} - {yasama.replace('_', ' ').title()}"
            
            # Bu klasördeki dosya sayısını ekle
            DOSYA_SAYACLARI[f"{hesaplanan_yil}_{meta_etiket}"] += len(docx_dosyalari)

            print(f"📂 İşleniyor: {hesaplanan_yil} ({meta_etiket}) - {len(docx_dosyalari)} Dosya")

            for dosya in docx_dosyalari:
                tam_yol = os.path.join(kok_dizin, dosya)
                temiz_kelimeler = docx_oku_ve_temizle(tam_yol)
                
                for kelime in temiz_kelimeler:
                    entry = GENEL_SOZLUK[kelime][hesaplanan_yil]
                    entry["count"] += 1
                    entry["meta"] = meta_etiket
                    # Dosya sayısı döngü sonunda eklenecek
                    
        except Exception as e:
            print(f"Atlandı: {kok_dizin} - {e}")

    print("\n💾 Dosya sayıları birleştiriliyor...")
    
    # Dosya sayılarını ana sözlüğe göm
    for kelime, yillar in GENEL_SOZLUK.items():
        for yil, detay in yillar.items():
            # Yıl ve Meta etiketine göre dosya sayısını bul
            key = f"{yil}_{detay['meta']}"
            detay["files"] = DOSYA_SAYACLARI[key]

    print("💾 JSON kaydediliyor...")
    
    OPTIMIZE_SOZLUK = {}
    for kelime, yillar in GENEL_SOZLUK.items():
        # Toplamda 150'den az geçen kelimeleri at
        toplam = sum(d["count"] for d in yillar.values())
        if toplam > 150:
            OPTIMIZE_SOZLUK[kelime] = yillar

    with open(CIKTI_YOLU, "w", encoding="utf-8") as f:
        json.dump(OPTIMIZE_SOZLUK, f, ensure_ascii=False)

    print(f"✅ BİTTİ! 'veri.json' hazır.")

if __name__ == "__main__":
    ana_islem()