import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

def extract_section_links(url, target_sections):
    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"Failed to fetch the page. Status code: {response.status_code}")
        return pd.DataFrame()

    soup = BeautifulSoup(response.text, 'html.parser')
    data = []

    for section_id in target_sections:
        span = soup.find("span", {"id": section_id})
        if not span:
            continue

        heading_tag = span.find_parent(["h2", "h3"])
        if not heading_tag:
            continue

        for sibling in heading_tag.find_next_siblings():
            if sibling.name and sibling.name.startswith("h"):
                break

            for link in sibling.find_all("a", href=True):
                anchor = link.get_text(strip=True)
                href = urljoin(url, link["href"])

                if anchor and href:
                    link_type = "internal" if link["href"].startswith("/wiki/") else "external"
                    data.append({
                        "Section": section_id,
                        "Anchor": anchor,
                        "Link": href,
                        "Type": link_type
                    })

    return pd.DataFrame(data)

# -----------------------
# Streamlit App Starts
# -----------------------
st.title("🧠 Wikipedia Section Link Extractor")

url = st.text_input("Enter Wikipedia URL:", "https://en.wikipedia.org/wiki/August_1")

sections = [
    'Events',
    'Births',
    'Deaths',
    'Holidays_and_observances'
]

selected_sections = st.multiselect(
    "Select Sections to Extract:",
    options=sections,
    default=sections
)

if st.button("Extract Links"):
    with st.spinner("Scraping in progress..."):
        df = extract_section_links(url, selected_sections)
        if not df.empty:
            st.success(f"Found {len(df)} links.")
            st.dataframe(df)
            csv = df.to_csv(index=False)
            st.download_button("Download CSV", csv, "wikipedia_links.csv", "text/csv")
        else:
            st.warning("No links found in the selected sections.")
