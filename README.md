# 🧠 Edukacyjna Platforma dla Uczniów, Rodziców i Nauczycieli

Nowoczesna, ciemna, responsywna aplikacja edukacyjna tworzona w architekturze monolitycznej. 
Umożliwia zarządzanie zadaniami, ocenami, komentarzami i postępami uczniów, a także przegląd tych danych przez nauczycieli i rodziców.

---

## 🛠️ Technologie

- **Frontend**: Next.js + Tailwind CSS  
- **Backend** (planowany): Django + Django REST Framework  
- **Baza danych** (planowana): PostgreSQL  
- **Hosting**: Vercel (frontend), Railway/Render (backend)  
- **Wersjonowanie**: GitHub  

---

## 👤 Role użytkowników

### 🧑‍🎓 Uczeń
- Widzi przypisane zadania
- Przesyła rozwiązania (PDF/JPG)
- Może komentować zadania
- Otrzymuje feedback
- Widzi ranking

### 👨‍🏫 Nauczyciel
- Tworzy i zarządza zadaniami
- Ocenia prace uczniów i dodaje komentarze
- Śledzi postępy uczniów
- Ma dostęp do rankingów

### 👨‍👩‍👧 Rodzic
- Widzi postępy swojego dziecka
- Otrzymuje komentarze nauczyciela
- W przyszłości: zarządza płatnościami

---

## 📁 Struktura katalogów

`
/components
  /dashboard
    StudentDashboard.tsx
    TeacherDashboard.tsx
    ParentDashboard.tsx
  /ui
    card.tsx
    input.tsx
    button.tsx
    textarea.tsx
    dialog.tsx
/lib
  mockData.ts (planowane)
/pages
  /student
  /teacher
  /parent
`

---

## 🎯 Zasady kodowania (dla Codex/AI lub contributorów)

`
Jesteś asystentem programisty budującego platformę edukacyjną. Pisz profesjonalny, skalowalny, modularny kod:

- Stosuj Tailwind CSS z ciemną paletą (#011627 tło, #1D2D44 karty, #00FFFF akcenty)
- Komponenty pisz w React/Next.js, typuj dane (TS)
- Dane mockowane trzymamy w /lib/mockData.ts
- Backend będzie oparty o Django – przygotuj komponenty pod integrację z REST API
- Nie używaj żadnych menedżerów stanu (redux/zustand/context) bez potrzeby
- Koduj tak, jakby to był produkt SaaS sprzedawany klientom
`

---

## 🚀 Uruchomienie lokalnie

`ash
npm install
npm run dev
`

---

## 🔜 W planach

- System logowania i rejestracji (JWT / cookies)
- API backendowe (Django)
- Płatności rodziców (Stripe/Hotpay)
- Automatyczne przypisywanie zadań
- Rozbudowane rankingi z konkursami

---

## 🤝 Autor

Stanisław Korycki  
[GitHub](https://github.com/stanislawkorycki) – jeśli chcesz współtworzyć, napisz!

