from typing import List, Dict
import os
import logging

# logging.basicConfig(level=logging.INFO) # Configure in main bot.py or scheduled_update.py

FORMAT_MAP = {
    'vmess': 'v2rayNG',
    'vless': 'hiddify',
    'trojan': 'trojan', # Changed from 'npv' for more general name
    'ss': 'shadowsocks',
    'ssr': 'shadowsocksr',
    'tuic': 'tuic',
    'hy2': 'hysteria2',
    'hysteria': 'hysteria',
}
DEFAULT_FORMAT_KEY = 'clashMetaCore' # Fallback filename/category for unmatched protocols

def classify_links(links: List[str]) -> Dict[str, List[str]]:
    """
    Classifies a list of subscription links into buckets based on their protocol.
    """
    buckets: Dict[str, List[str]] = {}
    if not links:
        return buckets

    for link in links:
        if not isinstance(link, str) or '://' not in link:
            logging.debug(f"Skipping invalid or non-string link: {str(link)[:100]}")
            continue

        try:
            # Extract protocol part (e.g., "vmess" from "vmess://...")
            proto_part = link.split('://', 1)[0]
            protocol = proto_part.lower() # Normalize to lowercase for matching
        except IndexError:
            # This case should be rare if '://' check passed, but good for safety
            logging.debug(f"Skipping link with unexpected format (no '://' after split): {link[:100]}")
            continue

        format_key = FORMAT_MAP.get(protocol, DEFAULT_FORMAT_KEY)
        buckets.setdefault(format_key, []).append(link)

    return buckets

def build_sub_files(links: List[str], output_dir: str):
    """
    Builds subscription files from a list of links, categorized by protocol.
    Each category gets its own .txt file in the specified output directory.
    """
    if not links:
        logging.info("No links provided to build_sub_files. No files will be generated.")
        return

    classified_buckets = classify_links(links)
    if not classified_buckets:
        logging.info("No valid links were classified. No subscription files will be generated.")
        return

    # Ensure output_dir exists
    try:
        if os.path.exists(output_dir) and not os.path.isdir(output_dir):
            logging.error(f"Output path {output_dir} exists but is not a directory. Cannot create files.")
            return
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        logging.error(f"OSError creating output directory {output_dir}: {e}")
        return # Cannot proceed if directory creation fails
    except Exception as e: # Catch any other unexpected error during makedirs
        logging.error(f"Unexpected error creating directory {output_dir}: {e}")
        return


    logging.info(f"Building {len(classified_buckets)} subscription file(s) in directory: {output_dir}")

    for format_name, link_list in classified_buckets.items():
        if not link_list:
            continue # Should not happen due to setdefault logic

        file_path = os.path.join(output_dir, f"{format_name}.txt")

        try:
            content = "\n".join(link_list)
            # Ensure a final newline, as many tools/parsers expect it.
            if content and not content.endswith('\n'):
                content += '\n'
            # If content is empty (e.g. empty list of links somehow), write an empty file with a newline.
            elif not content:
                content = '\n'

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logging.info(f"Successfully wrote {len(link_list)} links to {file_path}")
        except IOError as e:
            logging.error(f"IOError writing to file {file_path}: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred while writing {file_path}: {e}")
