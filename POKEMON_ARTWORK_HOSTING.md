# Approved Pokémon artwork hosting

This repository can host **authorized** Pokémon artwork under `images/pokemon/` and reference it in Cockatrice via raw GitHub URLs. **Do not download and republish Bulbagarden or third-party catalog images without permission.** Public access does not establish redistribution rights.

Create `manifest.csv` alongside your authorized image files with columns:
`card_id,image_file,rights_note,set_code,set_num`

- `card_id`: value inside the final `[...]` of the XML card name.
- `image_file`: local file path relative to the CSV directory.
- `rights_note`: how you are allowed to rehost the image.
- `set_code` and `set_num`: narrow the exact printing, required for grouped cards.

Run locally:
```powershell
python tools/host_pokemon_artwork.py --manifest C:\Artwork\manifest.csv --xml 01.PokemonTCG.xml --out C:\Artwork\Staged
```

Review `Staged\artwork-hosting-manifest.csv`, the generated image files and `Staged\01.PokemonTCG.hosted.xml`. Commit images under `images/pokemon/`, then merge the XML only once the image URLs work. Do not replace the existing XML until reviewed.

This tool does **not scrape image sites**, overwrite existing repository files or upload anything automatically. It requires explicit files and provenance, rejects invalid images and preserves card records. GitHub raw image hosting may be inconvenient for tens of thousands of images; a dedicated CDN or object store is preferable at that scale.
