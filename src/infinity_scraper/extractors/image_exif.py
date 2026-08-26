"""
Image EXIF Metadata, Camera Specifications & GPS Geotag Extractor for InfinityScrape.
"""

import io
import logging
from typing import Any, Dict, Optional
import httpx
from PIL import Image, ExifTags

from infinity_scraper.config import get_stealth_headers

logger = logging.getLogger(__name__)


def _convert_to_degrees(value) -> float:
    """Helper to convert the GPS coordinates stored in EXIF to degress in float format"""
    d = float(value[0])
    m = float(value[1])
    s = float(value[2])
    return d + (m / 60.0) + (s / 3600.0)


async def extract_image_exif_from_url(
    image_url: str,
    timeout: int = 15,
) -> Dict[str, Any]:
    """
    Download and extract full EXIF camera metadata, timestamps, and GPS geolocation from any online image.
    """
    clean_url = image_url.strip()
    headers = get_stealth_headers(clean_url)

    try:
        async with httpx.AsyncClient(headers=headers, timeout=timeout, follow_redirects=True, verify=False) as client:
            resp = await client.get(clean_url)
            resp.raise_for_status()
            img_bytes = resp.content

        img = Image.open(io.BytesIO(img_bytes))
        exif_raw = img.getexif()

        metadata: Dict[str, Any] = {
            "format": img.format,
            "dimensions": f"{img.width}x{img.height}",
            "mode": img.mode,
            "has_exif": bool(exif_raw),
        }

        gps_info: Dict[str, Any] = {}
        exif_tags_decoded: Dict[str, Any] = {}

        if exif_raw:
            for tag_id, val in exif_raw.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                if isinstance(val, (str, int, float)):
                    exif_tags_decoded[tag_name] = str(val)

            # Check IFD GPS tags
            for ifd_id in ExifTags.IFD:
                try:
                    ifd = exif_raw.get_ifd(ifd_id)
                    if ifd_id == ExifTags.IFD.GPSInfo:
                        for gps_tag_id, gps_val in ifd.items():
                            gps_tag_name = ExifTags.GPSTAGS.get(gps_tag_id, str(gps_tag_id))
                            gps_info[gps_tag_name] = gps_val
                except Exception:
                    pass

        # Calculate decimal GPS coordinates if available
        lat_dec, lon_dec = None, None
        if "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
            try:
                lat_dec = _convert_to_degrees(gps_info["GPSLatitude"])
                if gps_info.get("GPSLatitudeRef") == "S":
                    lat_dec = -lat_dec

                lon_dec = _convert_to_degrees(gps_info["GPSLongitude"])
                if gps_info.get("GPSLongitudeRef") == "W":
                    lon_dec = -lon_dec
            except Exception:
                pass

        doc = [
            f"# 📷 Image EXIF & Geotag Recon: {clean_url.split('/')[-1]}",
            f"- **Image URL:** [{clean_url}]({clean_url})",
            f"- **Format / Dimensions:** `{img.format}` ({img.width}x{img.height} px)",
        ]

        if exif_tags_decoded.get("Make") or exif_tags_decoded.get("Model"):
            doc.append(f"- **Camera Make / Model:** {exif_tags_decoded.get('Make', '')} {exif_tags_decoded.get('Model', '')}")
        if exif_tags_decoded.get("DateTime") or exif_tags_decoded.get("DateTimeOriginal"):
            doc.append(f"- **Capture Date/Time:** `{exif_tags_decoded.get('DateTimeOriginal') or exif_tags_decoded.get('DateTime')}`")
        if exif_tags_decoded.get("Software"):
            doc.append(f"- **Editing Software:** `{exif_tags_decoded.get('Software')}`")

        if lat_dec is not None and lon_dec is not None:
            osm_link = f"https://www.openstreetmap.org/?mlat={lat_dec}&mlon={lon_dec}#map=16/{lat_dec}/{lon_dec}"
            doc.append(f"\n### 📍 GPS Geotag Discovered!")
            doc.append(f"- **Latitude / Longitude:** `{lat_dec:.6f}, {lon_dec:.6f}`")
            doc.append(f"- **OpenStreetMap Location:** [View on Map]({osm_link})")
        else:
            doc.append("\n*No GPS geotags embedded in this image (stripped or not recorded).*")

        return {
            "image_url": clean_url,
            "format": img.format,
            "width": img.width,
            "height": img.height,
            "latitude": lat_dec,
            "longitude": lon_dec,
            "exif": exif_tags_decoded,
            "markdown": "\n".join(doc),
        }

    except Exception as exc:
        logger.error(f"Image EXIF extraction error for {image_url}: {exc}")
        return {
            "image_url": clean_url,
            "error": str(exc),
            "markdown": f"Failed to extract EXIF from image `{clean_url}`: {str(exc)}",
        }
