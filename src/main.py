"""Barnstormers.com Aircraft Classifieds Scraper"""
import os
import re
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlencode, urljoin

import httpx
from apify import Actor
from bs4 import BeautifulSoup


def extract_number(text: str) -> Optional[float]:
    """Extract numeric value from text string."""
    if not text:
        return None
    # Remove commas and dollar signs, extract first number
    cleaned = re.sub(r'[,$]', '', text)
    match = re.search(r'[\d,]+\.?\d*', cleaned)
    if match:
        try:
            return float(match.group().replace(',', ''))
        except (ValueError, AttributeError):
            return None
    return None


def parse_listing_row(row, base_url: str) -> Optional[dict]:
    """Parse a single listing table row."""
    try:
        cells = row.find_all('td')
        if len(cells) < 6:
            return None
        
        # Extract basic info
        link_cell = cells[1]
        link = link_cell.find('a')
        if not link:
            return None
        
        url = urljoin(base_url, link.get('href', ''))
        title = link.get_text(strip=True)
        
        # Parse title for make/model/year
        # Common format: "1975 Cessna 172M" or "Piper Cherokee 180"
        title_parts = title.split()
        year = None
        make = None
        model = None
        
        # Try to extract year (4-digit number at start)
        if title_parts and re.match(r'^\d{4}$', title_parts[0]):
            year = int(title_parts[0])
            title_parts = title_parts[1:]
        
        # First remaining word is usually make
        if title_parts:
            make = title_parts[0]
        
        # Rest is model
        if len(title_parts) > 1:
            model = ' '.join(title_parts[1:])
        
        # Extract other fields
        category = cells[0].get_text(strip=True) if len(cells) > 0 else None
        price_text = cells[2].get_text(strip=True) if len(cells) > 2 else None
        price = extract_number(price_text)
        
        location = cells[3].get_text(strip=True) if len(cells) > 3 else None
        
        # Try to extract tail number (N-number pattern)
        tail_number = None
        desc_text = cells[4].get_text(strip=True) if len(cells) > 4 else ''
        tail_match = re.search(r'N\d+[A-Z]*', desc_text, re.IGNORECASE)
        if tail_match:
            tail_number = tail_match.group().upper()
        
        # Try to extract total time
        total_time = None
        time_patterns = [
            r'(\d+(?:,\d+)?)\s*(?:TT|TTAF|Total\s*Time|Hours?)',
            r'(?:TT|TTAF|Total\s*Time)[:\s]*(\d+(?:,\d+)?)'
        ]
        for pattern in time_patterns:
            time_match = re.search(pattern, desc_text, re.IGNORECASE)
            if time_match:
                total_time = extract_number(time_match.group(1))
                break
        
        return {
            'url': url,
            'listingTitle': title,
            'make': make,
            'model': model,
            'year': year,
            'price': price,
            'category': category,
            'tailNumber': tail_number,
            'totalTimeHours': total_time,
            'location': location,
            'description': desc_text,
            'sellerName': None,
            'sellerPhone': None,
            'sellerEmail': None,
            'imageUrl': None,
            'scrapedAt': datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        Actor.log.warning(f'Failed to parse listing row: {e}')
        return None


def enrich_listing_detail(listing: dict, html_content: str) -> dict:
    """Enrich listing with details from detail page."""
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Extract seller information
        # Look for contact info patterns
        text_content = soup.get_text()
        
        # Try to find phone number
        phone_match = re.search(r'(?:Phone|Tel|Call)[:\s]*(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})', text_content, re.IGNORECASE)
        if phone_match:
            listing['sellerPhone'] = phone_match.group(1)
        
        # Try to find email
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text_content)
        if email_match:
            listing['sellerEmail'] = email_match.group()
        
        # Try to find seller name (often near contact info)
        seller_patterns = [
            r'(?:Contact|Seller)[:\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)(?:\s+[-–]\s+)?(?:Phone|Email|Contact)'
        ]
        for pattern in seller_patterns:
            seller_match = re.search(pattern, text_content)
            if seller_match:
                listing['sellerName'] = seller_match.group(1).strip()
                break
        
        # Extract main image
        img_tag = soup.find('img', src=re.compile(r'\.(jpg|jpeg|png|gif)', re.IGNORECASE))
        if img_tag and img_tag.get('src'):
            listing['imageUrl'] = urljoin(listing['url'], img_tag['src'])
        
        # Get fuller description
        desc_div = soup.find('div', class_=re.compile(r'description|details|content', re.IGNORECASE))
        if desc_div:
            listing['description'] = desc_div.get_text(strip=True, separator=' ')[:5000]
        
    except Exception as e:
        Actor.log.warning(f'Failed to enrich listing details: {e}')
    
    return listing


def build_search_url(input_data: dict) -> str:
    """Build search URL from input parameters."""
    base_url = "https://www.barnstormers.com/classified_ads.php"
    
    # Map input to query parameters (adjust based on actual site params)
    params = {}
    
    if input_data.get('aircraft_category') and input_data['aircraft_category'] != 'All':
        # This would need to be mapped to actual site category IDs
        params['category'] = input_data['aircraft_category']
    
    if input_data.get('make_filter'):
        params['make'] = input_data['make_filter']
    
    if input_data.get('model_filter'):
        params['model'] = input_data['model_filter']
    
    if input_data.get('min_price'):
        params['price_min'] = input_data['min_price']
    
    if input_data.get('max_price'):
        params['price_max'] = input_data['max_price']
    
    if input_data.get('min_year'):
        params['year_min'] = input_data['min_year']
    
    if input_data.get('max_year'):
        params['year_max'] = input_data['max_year']
    
    if input_data.get('location_state'):
        params['state'] = input_data['location_state']
    
    if params:
        return f"{base_url}?{urlencode(params)}"
    return base_url


async def main():
    """Main scraper entry point."""
    async with Actor:
        # Get input
        actor_input = await Actor.get_input()
        if not actor_input:
            Actor.log.error('No input provided!')
            return
        
        Actor.log.info('Starting Barnstormers scraper...')
        Actor.log.info(f'Input: {actor_input}')
        
        # Build search URL
        search_url = build_search_url(actor_input)
        max_results = actor_input.get('maxResults', 3)
        
        # Setup proxy
        proxy_config = actor_input.get('proxyConfiguration')
        proxy_url = None
        if proxy_config and proxy_config.get('useApifyProxy'):
            # Manual proxy construction for SDK 1.x
            proxy_password = os.getenv('APIFY_PROXY_PASSWORD')
            if proxy_password:
                proxy_url = f"http://auto:{proxy_password}@proxy.apify.com:8000"
        
        # Configure HTTP client
        client_kwargs = {'follow_redirects': True, 'timeout': 30.0}
        if proxy_url:
            client_kwargs['proxy'] = proxy_url  # httpx uses 'proxy', not 'proxies'
        
        results_count = 0
        
        async with httpx.AsyncClient(**client_kwargs) as client:
            # Fetch listing page
            Actor.log.info(f'Fetching search results from: {search_url}')
            response = await client.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Find listing table rows
            table = soup.find('table')
            if not table:
                Actor.log.warning('No listing table found on page')
                return
            
            rows = table.find_all('tr')[1:]  # Skip header row
            Actor.log.info(f'Found {len(rows)} listing rows')
            
            for row in rows:
                if results_count >= max_results:
                    Actor.log.info(f'Reached maxResults limit: {max_results}')
                    break
                
                listing = parse_listing_row(row, search_url)
                if not listing:
                    continue
                
                # Optionally fetch detail page for enrichment
                # (comment out for faster scraping if basic data is enough)
                try:
                    Actor.log.info(f'Fetching details for: {listing["title"]}')
                    detail_response = await client.get(listing['url'])
                    if detail_response.status_code == 200:
                        listing = enrich_listing_detail(listing, detail_response.text)
                except Exception as e:
                    Actor.log.warning(f'Failed to fetch detail page: {e}')
                
                # Push result immediately
                await Actor.push_data(listing)
                results_count += 1
                Actor.log.info(f'Scraped {results_count}/{max_results}: {listing["title"]}')
        
        # Save task metadata
        env = Actor.get_env()
        await Actor.set_value('SAVED-TASK', {
            'actorId': env.get('actor_id'),
            'actorRunId': env.get('actor_run_id'),
            'defaultDatasetId': env.get('default_dataset_id'),
            'startedAt': env.get('started_at'),
            'input': actor_input,
            'stats': {
                'itemsScraped': results_count,
                'requestsTotal': results_count + 1
            }
        })
        
        Actor.log.info(f'Scraping completed! Total results: {results_count}')
