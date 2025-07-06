from typing import List, Dict
import os
import logging

# logging.basicConfig(level=logging.INFO) # Configure in main bot.py or scheduled_update.py

FORMAT_MAP = {
    'vmess': 'vmess',       # Changed from 'v2rayNG'
    'vless': 'vless',       # Changed from 'hiddify'
    'trojan': 'trojan',
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


    logging.info(f"Building individual subscription files in directory: {output_dir}")

    all_known_protocol_links = [] # For creating an aggregated file

    for format_name, link_list in classified_buckets.items():
        if not link_list:
            continue

        file_path = os.path.join(output_dir, f"{format_name}.txt")

        try:
            content = "\n".join(link_list)
            if content and not content.endswith('\n'):
                content += '\n'
            elif not content: # Handles empty link_list for a format
                content = '\n'

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logging.info(f"Successfully wrote {len(link_list)} links to {file_path}")

            # If this format_name came from an explicit FORMAT_MAP key (not DEFAULT_FORMAT_KEY),
            # add its links to the all_known_protocol_links list.
            # We check if format_name is one of the values in FORMAT_MAP.
            if format_name in FORMAT_MAP.values():
                 all_known_protocol_links.extend(link_list)

        except IOError as e:
            logging.error(f"IOError writing to file {file_path}: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred while writing {file_path}: {e}")

    # Create the all_proxies.txt file
    if all_known_protocol_links:
        # Deduplicate again in case a link somehow appeared in multiple specific categories that map to same output file
        unique_overall_links = sorted(list(set(all_known_protocol_links)))
        all_proxies_path = os.path.join(output_dir, "all_proxies.txt")
        try:
            content = "\n".join(unique_overall_links)
            if content and not content.endswith('\n'):
                content += '\n'
            elif not content: # Should not happen if all_known_protocol_links is not empty
                content = '\n'

            with open(all_proxies_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logging.info(f"Successfully wrote {len(unique_overall_links)} links to {all_proxies_path}")
        except IOError as e:
            logging.error(f"IOError writing to file {all_proxies_path}: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred while writing {all_proxies_path}: {e}")
    else:
        logging.info("No links from known protocols to aggregate for all_proxies.txt.")
        # Optionally, create an empty all_proxies.txt
        all_proxies_path = os.path.join(output_dir, "all_proxies.txt")
        try:
            with open(all_proxies_path, 'w', encoding='utf-8') as f:
                f.write('\n') # Write an empty file with a newline
            logging.info(f"Created empty {all_proxies_path} as no known protocol links were found.")
        except IOError as e:
            logging.error(f"IOError writing empty {all_proxies_path}: {e}")
