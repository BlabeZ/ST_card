#!/usr/bin/env python3

import argparse
import base64
import json
import struct
from pathlib import Path

from PIL import Image, ImageOps, PngImagePlugin


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def encode_card(card: dict, original_text: str) -> tuple[str, str]:
    if card.get("spec") != "chara_card_v2" or card.get("spec_version") != "2.0":
        raise ValueError("character JSON must use Character Card V2")

    v3_card = dict(card)
    v3_card["spec"] = "chara_card_v3"
    v3_card["spec_version"] = "3.0"
    v3_text = json.dumps(v3_card, ensure_ascii=False, separators=(",", ":"))

    def to_base64(value: str) -> str:
        return base64.b64encode(value.encode("utf-8")).decode("ascii")

    return to_base64(original_text), to_base64(v3_text)


def read_text_chunks(path: Path) -> dict[str, str]:
    chunks: dict[str, str] = {}
    with path.open("rb") as file:
        if file.read(len(PNG_SIGNATURE)) != PNG_SIGNATURE:
            raise ValueError("output is not a PNG file")

        while True:
            length_bytes = file.read(4)
            if len(length_bytes) != 4:
                raise ValueError("truncated PNG chunk length")
            length = struct.unpack(">I", length_bytes)[0]
            chunk_type = file.read(4)
            payload = file.read(length)
            crc = file.read(4)
            if len(chunk_type) != 4 or len(payload) != length or len(crc) != 4:
                raise ValueError("truncated PNG chunk")

            if chunk_type == b"tEXt":
                keyword, separator, value = payload.partition(b"\0")
                if separator:
                    chunks[keyword.decode("latin-1")] = value.decode("latin-1")
            if chunk_type == b"IEND":
                break

    return chunks


def decode_json(value: str) -> dict:
    return json.loads(base64.b64decode(value, validate=True).decode("utf-8"))


def verify_card(path: Path, expected_v2: dict) -> None:
    chunks = read_text_chunks(path)
    if "chara" not in chunks or "ccv3" not in chunks:
        raise ValueError("PNG must contain both chara and ccv3 tEXt chunks")

    actual_v2 = decode_json(chunks["chara"])
    actual_v3 = decode_json(chunks["ccv3"])
    expected_v3 = dict(expected_v2)
    expected_v3["spec"] = "chara_card_v3"
    expected_v3["spec_version"] = "3.0"

    if actual_v2 != expected_v2:
        raise ValueError("chara payload does not match the source Character Card V2")
    if actual_v3 != expected_v3:
        raise ValueError("ccv3 payload does not match the converted Character Card V3")


def build_card(image_path: Path, json_path: Path, output_path: Path) -> None:
    original_text = json_path.read_text(encoding="utf-8")
    card = json.loads(original_text)
    chara, ccv3 = encode_card(card, original_text)

    metadata = PngImagePlugin.PngInfo()
    # Match SillyTavern's current writer: tEXt/chara plus a V3-compatible tEXt/ccv3.
    # Source: https://github.com/SillyTavern/SillyTavern/blob/release/src/character-card-parser.js
    metadata.add_text("chara", chara, zip=False)
    metadata.add_text("ccv3", ccv3, zip=False)

    temporary_path = output_path.with_name(f".{output_path.name}.tmp")
    try:
        with Image.open(image_path) as source:
            icc_profile = source.info.get("icc_profile")
            image = ImageOps.exif_transpose(source).convert("RGB")
            save_options = {"pnginfo": metadata, "optimize": True}
            if icc_profile:
                save_options["icc_profile"] = icc_profile
            image.save(temporary_path, format="PNG", **save_options)

        verify_card(temporary_path, card)
        temporary_path.replace(output_path)
    finally:
        temporary_path.unlink(missing_ok=True)


def parse_args() -> argparse.Namespace:
    package_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(
        description="Embed a Character Card V2 JSON into a PNG image."
    )
    parser.add_argument("--image", type=Path, default=package_root / "user.jpg")
    parser.add_argument(
        "--json",
        type=Path,
        default=package_root / "boundless-private-collection.character.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=package_root / "boundless-private-collection.character.png",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_card(args.image.resolve(), args.json.resolve(), args.output.resolve())
    print(f"Created and verified: {args.output.resolve()}")


if __name__ == "__main__":
    main()
