# 🪄 Scrollforge API

Welcome to **Scrollforge** — an open-source, Elder Scrolls-inspired fantasy character generator API powered by original, rich lore, modular JSON data, and dynamic logic. It lets you conjure up fully fleshed-out characters with names, races, factions, classes, faiths, origins, and unique backstories — all with a single request.

Created by **Vishwas Sharma**

---

## ✨ Features

* 🎲 Procedural character generation with deep lore ties
* 🧬 Lore-driven JSON databases for races, factions, classes, etc.
* ⚔️ Faction compatibility and hostility logic
* 🌎 Region- and place-based origin system
* 🗌 Deity matching per race and personality
* 📜 Backstory generation using context-aware sentence templates
* 💡 Custom filtering using query parameters (`race`, `class`, etc.)

---

## 🏠 Project Structure

```
Scrollforge-API/
├── app.py                  # Flask entry point
├── requirements.txt        # Dependencies
├── .gitignore              # Ignored files
└── scrollforge/
    ├── __init__.py         # Flask app factory
    ├── routes.py           # API endpoints
    ├── generator.py        # Core character generation logic
    ├── filters.py          # Filtering helpers and lore logic
    └── data/
        ├── races.json
        ├── classes.json
        ├── factions.json
        └── ...
```

---

## 🔌 API Endpoints

### `GET /generate`

Generates a fully random character with all available fields: name, race, class, gender, faction, region, deity, and backstory.

---

### `GET /custom_generate`

Generate a character with specific filters using query parameters:

```http
/custom_generate?race=Canari&class=runeweaver&gender=Male&place=Esmoria
```

#### Available parameters:

* `race` – e.g., Canari, Vaelari, Ashkai, etc.
* `class` – must be compatible with selected race
* `gender` – Male, Female or Non-Binary
* `region` – like "Varkuun Hollow", "Esmoria", etc.

Scrollforge automatically enforces lore logic — if your inputs are invalid or incompatible, it'll gracefully randomize or fallback.

---

## 🧠 How It Works

* **`generator.py`** handles assembling the final character data.
* **`filters.py`** ensures lore rules are followed:

  * Faction vs. Faction hostility logic
  * Race-to-class compatibility filtering
  * Deities matched by race and personality
  * Locations matched by race region origin
* Backstories are dynamically built using placeholders like `{name}`, `{faction}`, `{place}`, and `{deity}` to sound natural and unique every time.

---

## 🧪 Example Output

```json
{
  "name": "Kaerwyn",
  "race": "Vaelari",
  "class": "Soulweaver",
  "gender": "Female",
  "region": "Esmoria",
  "origin": {
    "name": "Ivory Hollow",
    "place": "The Hollow Temple"
  },
  "birthsign": "The Whispering Flame",
  "faction": "The Quiet Hand",
  "deity": "Alari the Silent Watcher",
  "backstory": "Kaerwyn was raised by a wandering Quiet Hand monk in the bleak hills of Ivory Hollow, where Kaerwyn first whispered the name of Alari the Silent Watcher."
}
```

---

## 🛠️ Running Locally

```bash
git clone https://github.com/vishwassharma38/Scrollforge-API.git
cd Scrollforge-API
pip install -r requirements.txt
python app.py
```

Then visit: `http://localhost:5000/generate`

---

## 🤝 Contributing

We welcome lore nerds, JSON tinkerers, and logic-loving devs!

* Fork this repo
* Add your enhancements (new races, factions, classes, etc.)
* Submit a Pull Request with a clear description

All contributions must follow the existing format and maintain the integrity of the Scrollforge worldbuilding.

---

## 🚫 License

This project is covered under a **Custom Non-Commercial Attribution License**:

* ✅ Free to use, modify, and share
* ✅ Contributions welcome!
* ❌ **Commercial use is strictly prohibited** unless you're **Creator**
* 🗪 Must credit the original author in all uses and forks

🔗 See the full [LICENSE](License) for legal terms.
Contact [Vishwassharma741@gmail.com] for commercial use discussions.

---

> "A world of whispers and fire, forged with a scroll and a spark."
