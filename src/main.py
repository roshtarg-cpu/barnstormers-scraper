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


def parse_detail_page(title: str, url: str, html_content: str) -> Optional[dict]:
    """Parse aircraft listing detail page."""
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Parse title for make/model/year (e.g., "1993 MD Helicopters 520N")
        title_parts = title.split()
        year = None
        make = None
        model = None
        
        if title_parts and re.match(r'^\d{4}$', title_parts[0]):
            year = int(title_parts[0])
            title_parts = title_parts[1:]
        
        if title_parts:
            make = title_parts[0]
        
        if len(title_parts) > 1:
            model = ' '.join(title_parts[1:])
        
        # Extract price (format: "$1,250,000")
        price = None
        price_text = soup.get_text()
        price_match = re.search(r'\$[\d,]+', price_text)
        if price_match:
            price = extract_number(price_match.group())
        
        # Extract description (main content after title)
        description = None
        main_table = soup.find('table')
        if main_table:
            text_content = main_table.get_text(strip=True, separator=' ')
            # Description is between "FOR SALE" and "Contact"
            desc_match = re.search(r'FOR SALE\s+(.+?)\s+Contact', text_content, re.DOTALL)
            if desc_match:
                description = desc_match.group(1).strip()
        
        # Extract location (format: "Jacksonville, FL 32254")
        location = None
        loc_match = re.search(r'located\s+([^•]+)', price_text)
        if loc_match:
            location = loc_match.group(1).strip()
        
        # Extract seller name (after "Contact")
        seller_name = None
        seller_match = re.search(r'Contact\s+([^,]+)', price_text)
        if seller_match:
            seller_name = seller_match.group(1).strip()
        
        # Extract phone (format: "954-470-9213")
        seller_phone = None
        phone_match = re.search(r'Telephone:\s*(\d{3}-\d{3}-\d{4})', price_text)
        if phone_match:
            seller_phone = phone_match.group(1)
        
        # Extract total time (format: "2230TT")
        total_time = None
        tt_match = re.search(r'(\d+(?:,\d+)?)\s*TT', description or '', re.IGNORECASE)
        if tt_match:
            total_time = extract_number(tt_match.group(1))
        
        # Extract tail number (N-number)
        tail_number = None
        if description:
            tail_match = re.search(r'N\d+[A-Z]*', description, re.IGNORECASE)
            if tail_match:
                tail_number = tail_match.group().upper()
        
        # Extract first image
        image_url = None
        img_tag = soup.find('img', src=re.compile(r'listing_images'))
        if img_tag:
            image_url = img_tag.get('src', '')
            if image_url and not image_url.startswith('http'):
                image_url = urljoin(url, image_url)
        
        return {
            'url': url,
            'listingTitle': title,
            'make': make,
            'model': model,
            'year': year,
            'price': price,
            'category': None,
            'tailNumber': tail_number,
            'totalTimeHours': total_time,
            'location': location,
            'description': description,
            'sellerName': seller_name,
            'sellerPhone': seller_phone,
            'sellerEmail': None,
            'imageUrl': image_url,
            'scrapedAt': datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        Actor.log.warning(f'Failed to parse detail page for {title}: {e}')
        return None
        


def build_search_url(input_data: dict) -> str:
    """Build search URL from input parameters."""
    # Use listing.php for recent listings (simpler page)
    base_url = "https://www.barnstormers.com/listing.php"
    
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
            
            # Find listing links (Barnstormers uses <a class='listing_header'>)
            listing_links = soup.find_all('a', class_='listing_header')
            Actor.log.info(f'Found {len(listing_links)} listing links')
            
            if not listing_links:
                Actor.log.warning('No listings found on page')
                return
            
            for link in listing_links:
                if results_count >= max_results:
                    Actor.log.info(f'Reached maxResults limit: {max_results}')
                    break
                
                # Extract basic info from link
                title = link.get_text(strip=True)
                detail_url = urljoin(search_url, link.get('href', ''))
                
                if not detail_url:
                    continue
                
                Actor.log.info(f'Fetching details for: {title}')
                
                # Fetch detail page
                try:
                    detail_response = await client.get(detail_url)
                    detail_response.raise_for_status()
                    
                    listing = parse_detail_page(title, detail_url, detail_response.text)
                    
                    if listing:
                        await Actor.push_data(listing)
                        results_count += 1
                        Actor.log.info(f'Scraped {results_count}/{max_results}: {title}')
                    
                except Exception as e:
                    Actor.log.warning(f'Failed to fetch detail page for {title}: {e}')
                    continue
        
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
