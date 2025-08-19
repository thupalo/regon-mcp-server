# MCP Tools Enum Documentation Examples

## Różne sposoby dokumentowania wartości enum w specyfikacji narzędzi MCP

### Option 1: oneOf z const (Najbardziej szczegółowe - ZALECANE)
```json
"report_name": {
  "type": "string",
  "description": "Typ raportu z dostępnych opcji - wybierz odpowiedni raport w zależności od typu podmiotu",
  "oneOf": [
    {
      "const": "BIR11OsFizycznaDaneOgolne",
      "title": "Osoba fizyczna - dane ogólne",
      "description": "📋 Podstawowe dane osoby fizycznej prowadzącej działalność gospodarczą"
    },
    {
      "const": "BIR11OsPrawna",
      "title": "Osoba prawna - dane podstawowe", 
      "description": "🏛️ Podstawowe informacje o osobie prawnej (spółka, fundacja, stowarzyszenie)"
    }
  ]
}
```

### Option 2: enum z rozszerzoną description (Prostsze)
```json
"report_name": {
  "type": "string",
  "description": "Typ raportu z dostępnych opcji:\n• BIR11OsFizycznaDaneOgolne - 📋 Dane ogólne osoby fizycznej\n• BIR11OsPrawna - 🏛️ Dane podstawowe osoby prawnej\n• BIR11OsPrawnaPkd - 📊 Kody PKD osoby prawnej\n• BIR11TypPodmiotu - 🔍 Typ podmiotu",
  "enum": [
    "BIR11OsFizycznaDaneOgolne",
    "BIR11OsPrawna", 
    "BIR11OsPrawnaPkd",
    "BIR11TypPodmiotu"
  ]
}
```

### Option 3: enum z examples (Dla najczęściej używanych)
```json
"report_name": {
  "type": "string",
  "description": "Typ raportu z dostępnych opcji",
  "enum": [
    "BIR11OsFizycznaDaneOgolne",
    "BIR11OsPrawna",
    "BIR11OsPrawnaPkd", 
    "BIR11TypPodmiotu"
  ],
  "examples": [
    "BIR11OsPrawna",
    "BIR11TypPodmiotu"
  ],
  "default": "BIR11OsPrawna"
}
```

### Option 4: anyOf z kategoriami (Grupowanie logiczne)
```json
"report_name": {
  "type": "string", 
  "description": "Typ raportu - wybierz kategorię i odpowiedni raport",
  "anyOf": [
    {
      "title": "📋 Raporty dla osób fizycznych",
      "enum": [
        "BIR11OsFizycznaDaneOgolne",
        "BIR11OsFizycznaDzialalnoscCeidg",
        "BIR11OsFizycznaDzialalnoscRolnicza"
      ]
    },
    {
      "title": "🏛️ Raporty dla osób prawnych", 
      "enum": [
        "BIR11OsPrawna",
        "BIR11OsPrawnaPkd",
        "BIR11OsPrawnaListaJednLokalnych"
      ]
    },
    {
      "title": "🔍 Raporty ogólne",
      "enum": [
        "BIR11TypPodmiotu"
      ]
    }
  ]
}
```

## Zalecenia:

1. **oneOf z const** - Najlepsza opcja dla szczegółowej dokumentacji
2. **enum z rozszerzoną description** - Dobra dla prostszych przypadków  
3. **examples i default** - Ułatwia wybór najczęściej używanych wartości
4. **anyOf z kategoriami** - Przydatne gdy enum ma wiele logicznych grup

## Korzyści każdego podejścia:

- **oneOf**: Najbogatsze metadane, wsparcie dla IDE, najlepsza dokumentacja
- **description**: Proste w implementacji, czytelne w kodzie
- **examples**: Ułatwia użytkownikom wybór popularnych opcji
- **anyOf**: Logiczne grupowanie dla złożonych enum-ów

Zastosowałem **Option 1 (oneOf z const)** w tools_polish.json jako najlepsze rozwiązanie.
