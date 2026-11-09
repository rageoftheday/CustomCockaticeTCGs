#!/usr/bin/env python3
"""Stage explicitly authorized local Pokemon artwork and rewrite matching Cockatrice XML URLs."""
import argparse, csv, hashlib, pathlib, re, xml.etree.ElementTree as ET

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--manifest",required=True,type=pathlib.Path)
    a.add_argument("--xml",required=True,type=pathlib.Path)
    a.add_argument("--out",required=True,type=pathlib.Path)
    a.add_argument("--branch",default="main")
    args=a.parse_args()
    base=args.manifest.parent.resolve()
    if args.out.exists() and any(args.out.iterdir()):
        raise SystemExit("Output folder must be empty; nothing overwritten.")
    tree=ET.parse(args.xml)
    cards={}
    for card in tree.findall(".//cards/card"):
        m=re.search(r"\[([^\]]+)\]$",card.findtext("name",""))
        if m: cards.setdefault(m.group(1).lower(),[]).append(card)
    images=args.out/"images"/"pokemon"
    images.mkdir(parents=True)
    records=[]
    with args.manifest.open(encoding="utf-8-sig",newline="") as f:
        for r in csv.DictReader(f):
            cid=(r.get("card_id") or "").strip().lower()
            if not re.fullmatch(r"[a-z0-9][a-z0-9_.-]{0,100}",cid): raise ValueError("Invalid card_id: "+cid)
            if not (r.get("rights_note") or "").strip(): raise ValueError("Missing image redistribution authorization note: "+cid)
            src=(base/(r.get("image_file") or "")).resolve()
            if not src.is_relative_to(base) or not src.is_file(): raise ValueError("Image outside manifest folder or missing: "+str(src))
            if src.stat().st_size > 15*1024*1024: raise ValueError("Image exceeds 15MB: "+str(src))
            data=src.read_bytes()
            ext=(".jpg" if data.startswith(bytes.fromhex("ffd8ff")) else
                 ".png" if data.startswith(bytes.fromhex("89504e470d0a1a0a")) else
                 ".webp" if data[:4]==b"RIFF" and data[8:12]==b"WEBP" else None)
            if ext is None or len(data)<256: raise ValueError("Invalid or tiny image: "+str(src))
            selected=cards.get(cid,[])
            if len(selected)!=1: raise ValueError("XML card ID missing or ambiguous: "+cid)
            slots=selected[0].findall("set")
            if r.get("set_code"): slots=[s for s in slots if (s.text or "").strip()==r["set_code"].strip()]
            if r.get("set_num"): slots=[s for s in slots if s.get("num","")==r["set_num"].strip()]
            if len(slots)!=1: raise ValueError("Multiple printings; add set_code and set_num: "+cid)
            name=cid+"-"+hashlib.sha256(data).hexdigest()[:12]+ext
            (images/name).write_bytes(data)
            url="https://raw.githubusercontent.com/rageoftheday/CustomCockaticeTCGs/"+args.branch+"/images/pokemon/"+name
            old=slots[0].get("picurl","")
            slots[0].set("picurl",url)
            records.append({"card_id":cid,"set_code":(slots[0].text or "").strip(),"set_num":slots[0].get("num",""),"old_url":old,"new_url":url,"image_file":"images/pokemon/"+name,"rights_note":r["rights_note"]})
    tree.write(args.out/"01.PokemonTCG.hosted.xml",encoding="utf-8",xml_declaration=True)
    with (args.out/"artwork-hosting-manifest.csv").open("w",newline="",encoding="utf-8") as f:
        cols=["card_id","set_code","set_num","old_url","new_url","image_file","rights_note"]
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(records)
    print("Staged",len(records),"approved images. Commit files and XML together after review.")

if __name__=="__main__": main()
