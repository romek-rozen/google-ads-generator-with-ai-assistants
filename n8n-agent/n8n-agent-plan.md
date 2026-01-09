# Plan: Google Ads Writer Agent w n8n

## Cel
Stworzyć workflow n8n, który działa jak agent do generowania reklam Google Ads (RSA) na podstawie zawartości strony internetowej.

## Architektura

```
┌─────────────────┐
│   Chat Trigger  │  ← Użytkownik podaje URL i ewentualne wytyczne
└────────┬────────┘
         ↓
┌─────────────────────────────────────────────────────┐
│                    AI Agent (GPT-4o)                │
│                                                     │
│  System prompt: Ekspert Google Ads RSA              │
│  - Zna limity znaków (headline: 30, desc: 90, etc.) │
│  - Generuje reklamy w formacie JSON                 │
│  - Waliduje przed zwróceniem wyniku                 │
└────────┬────────────────────────────────────────────┘
         │
         ├──→ [Tool 1: Web Scraper]
         │    Wywołuje istniejący workflow: Ln7kOpsx2ZzYh0Te
         │    Input: URL strony
         │    Output: markdown + meta tagi
         │
         ├──→ [Tool 2: Validate Google Ads]
         │    Code node z logiką walidacji
         │    Sprawdza: długość tekstów, liczbę elementów
         │    Zwraca: błędy lub OK
         │
         └──→ [Tool 3: Check Text Length]
              Prosty helper do sprawdzania długości tekstu
              Zwraca: tekst + liczba znaków
```

## Komponenty do stworzenia

### 1. Główny workflow: "Google Ads Writer Agent"

**Nodes:**

1. **Chat Trigger** (`@n8n/n8n-nodes-langchain.chatTrigger`)
   - Publiczny chat interface
   - Tytuł: "Google Ads Writer"
   - Opis: "Podaj URL strony, a wygeneruję reklamy Google Ads"

2. **AI Agent** (`@n8n/n8n-nodes-langchain.agent`)
   - Model: GPT-4o (OpenAI)
   - System message z instrukcjami dla agenta (poniżej)
   - Max iterations: 10
   - Podłączone tools (3 szt.)

3. **OpenAI Chat Model** (`@n8n/n8n-nodes-langchain.lmChatOpenAi`)
   - Model: gpt-4o
   - Temperature: 0.7

4. **Window Buffer Memory** (`@n8n/n8n-nodes-langchain.memoryBufferWindow`)
   - Zachowuje kontekst rozmowy

### 2. Tools dla agenta

#### Tool 1: Web Scraper (Call n8n Workflow)
- Node: `@n8n/n8n-nodes-langchain.toolWorkflow`
- Wywołuje: `Ln7kOpsx2ZzYh0Te` (_tool web scraper)
- Nazwa: `scrape_website`
- Opis: "Pobiera zawartość strony internetowej. Podaj URL."
- Input schema: `{ "query": "URL strony" }`

#### Tool 2: Validate Google Ads (Code Tool)
- Node: `@n8n/n8n-nodes-langchain.toolCode`
- Nazwa: `validate_google_ads`
- Opis: "Waliduje reklamy Google Ads. Sprawdza limity znaków i liczbę elementów."
- Kod JavaScript:

```javascript
const limits = {
  headline: 30,
  description: 90,
  path: 15
};

const countReq = {
  headlines: { min: 3, max: 15 },
  descriptions: { min: 2, max: 4 },
  paths: { min: 2, max: 2 }
};

const ads = $input.ads;
const errors = [];
const validated = {
  headlines: [],
  descriptions: [],
  paths: []
};

// Validate headlines
if (!ads.headlines || ads.headlines.length < countReq.headlines.min) {
  errors.push(`Headlines: minimum ${countReq.headlines.min} required`);
} else if (ads.headlines.length > countReq.headlines.max) {
  errors.push(`Headlines: maximum ${countReq.headlines.max} allowed`);
}

ads.headlines?.forEach((h, i) => {
  const len = h.length;
  validated.headlines.push({
    text: h,
    length: len,
    limit: limits.headline,
    valid: len <= limits.headline,
    status: len <= limits.headline ? "OK" : `TOO LONG by ${len - limits.headline} chars`
  });
});

// Validate descriptions
if (!ads.descriptions || ads.descriptions.length < countReq.descriptions.min) {
  errors.push(`Descriptions: minimum ${countReq.descriptions.min} required`);
} else if (ads.descriptions.length > countReq.descriptions.max) {
  errors.push(`Descriptions: maximum ${countReq.descriptions.max} allowed`);
}

ads.descriptions?.forEach((d, i) => {
  const len = d.length;
  validated.descriptions.push({
    text: d,
    length: len,
    limit: limits.description,
    valid: len <= limits.description,
    status: len <= limits.description ? "OK" : `TOO LONG by ${len - limits.description} chars`
  });
});

// Validate paths
if (!ads.paths || ads.paths.length !== 2) {
  errors.push("Paths: exactly 2 required");
}

ads.paths?.forEach((p, i) => {
  const len = p.length;
  validated.paths.push({
    text: p,
    length: len,
    limit: limits.path,
    valid: len <= limits.path,
    status: len <= limits.path ? "OK" : `TOO LONG by ${len - limits.path} chars`
  });
});

const allValid = errors.length === 0 &&
  validated.headlines.every(h => h.valid) &&
  validated.descriptions.every(d => d.valid) &&
  validated.paths.every(p => p.valid);

return {
  valid: allValid,
  errors: errors,
  validation: validated,
  summary: allValid ? "All ads are valid!" : "Validation failed. See errors above."
};
```

#### Tool 3: Check Text Length (Code Tool)
- Node: `@n8n/n8n-nodes-langchain.toolCode`
- Nazwa: `check_text_length`
- Opis: "Sprawdza długość tekstu. Użyj przed dodaniem do reklamy."
- Kod:

```javascript
const text = $input.text;
const limit = $input.limit || 30;
return {
  text: text,
  length: text.length,
  limit: limit,
  valid: text.length <= limit,
  remaining: limit - text.length
};
```

### 3. System Prompt dla AI Agent

```
Jesteś ekspertem od Google Ads RSA (Responsive Search Ads). Pomagasz tworzyć skuteczne reklamy tekstowe.

## TWOJE ZADANIA:
1. Pobierz zawartość strony za pomocą tool `scrape_website`
2. Przeanalizuj content i zaproponuj reklamy
3. Przed finalizacją ZAWSZE waliduj reklamy za pomocą `validate_google_ads`
4. Jeśli walidacja nie przejdzie - popraw teksty i waliduj ponownie

## LIMITY GOOGLE ADS (ŚCISŁE!):
- Headlines (nagłówki): 3-15 sztuk, każdy MAX 30 znaków
- Descriptions (opisy): 2-4 sztuki, każdy MAX 90 znaków
- Paths (ścieżki URL): dokładnie 2, każda MAX 15 znaków

## FORMAT REKLAMY (JSON):
{
  "campaign_name": "nazwa kampanii",
  "product": "nazwa produktu/usługi",
  "url": "URL strony",
  "headlines": ["Nagłówek 1", "Nagłówek 2", ...],
  "descriptions": ["Opis 1", "Opis 2", ...],
  "paths": ["sciezka1", "sciezka2"]
}

## ZASADY TWORZENIA REKLAM:
- Headlines: krótkie, dynamiczne, z CTA lub USP
- Descriptions: rozwiń korzyści, dodaj wezwanie do działania
- Paths: krótkie słowa kluczowe bez spacji i znaków specjalnych
- Pisz w języku strony (jeśli polska strona - po polsku)
- Unikaj powtórzeń między headlines
- Nie używaj wykrzykników nadmiernie

## FLOW PRACY:
1. Użytkownik podaje URL → wywołaj scrape_website
2. Przeanalizuj content strony
3. Wygeneruj propozycje reklam
4. Wywołaj validate_google_ads z JSON-em reklam
5. Jeśli błędy → popraw i waliduj ponownie
6. Zwróć finalny wynik z walidacją
```

## Kroki implementacji

### Krok 1: Utworzenie workflow
```
n8n_create_workflow z:
- name: "Google Ads Writer Agent"
- nodes: [Chat Trigger, AI Agent, OpenAI Model, Memory, 3x Tools]
- connections: odpowiednie połączenia
```

### Krok 2: Konfiguracja credentials
- Upewnić się, że OpenAI credentials są skonfigurowane w n8n

### Krok 3: Testowanie
1. Aktywować workflow
2. Otworzyć chat interface
3. Wpisać URL strony (np. "https://example.com")
4. Sprawdzić czy agent:
   - Pobiera stronę
   - Generuje reklamy
   - Waliduje
   - Poprawia jeśli potrzeba

## Weryfikacja

### Test 1: Podstawowy flow
- Input: "Wygeneruj reklamy dla https://kamiennewnetrza.pl"
- Oczekiwany rezultat: Agent pobiera stronę, generuje reklamy, waliduje, zwraca JSON

### Test 2: Walidacja błędów
- Ręcznie wywołać validate_google_ads z za długimi tekstami
- Sprawdzić czy zwraca poprawne błędy

### Test 3: Iteracja
- Podać URL i poprosić o "więcej kreatywnych nagłówków"
- Sprawdzić czy agent zachowuje kontekst (memory)

## Pliki do zmodyfikowania
- Brak (tworzymy nowy workflow w n8n)

## Zależności
- Istniejący workflow: `Ln7kOpsx2ZzYh0Te` (_tool web scraper)
- OpenAI API credentials w n8n
- Redis (używany przez scraper - już skonfigurowany)
