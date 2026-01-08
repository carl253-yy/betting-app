#!/usr/bin/env python3
"""
Test script to investigate HKJC data sources
"""
import requests
from bs4 import BeautifulSoup
import json

def investigate_hkjc():
    """Investigate HKJC websites for data sources"""
    urls_to_check = [
        "https://entertainment.hkjc.com/",
        "https://racing.hkjc.com/racing/english/index.aspx",
        "https://racing.hkjc.com/racing/english/racecard/index.aspx",
        "https://bet.hkjc.com/racing/index.aspx?lang=en"
    ]

    results = {}

    for url in urls_to_check:
        try:
            print(f"Checking {url}")
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })

            results[url] = {
                'status_code': response.status_code,
                'accessible': response.status_code == 200,
                'content_length': len(response.text),
                'title': None,
                'has_api_calls': False,
                'api_endpoints': []
            }

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Get title
                title_tag = soup.find('title')
                results[url]['title'] = title_tag.text.strip() if title_tag else None

                # Look for API calls or data endpoints
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string:
                        # Look for common API patterns
                        import re
                        api_patterns = [
                            r'https?://[^\s<>"\']*api[^\s<>"\']*',
                            r'https?://[^\s<>"\']*json[^\s<>"\']*',
                            r'https?://[^\s<>"\']*data[^\s<>"\']*',
                            r'/api/',
                            r'/data/',
                            r'/json/'
                        ]

                        for pattern in api_patterns:
                            matches = re.findall(pattern, script.string, re.IGNORECASE)
                            if matches:
                                results[url]['has_api_calls'] = True
                                results[url]['api_endpoints'].extend(matches[:10])  # Limit

                # Remove duplicates
                results[url]['api_endpoints'] = list(set(results[url]['api_endpoints']))

        except Exception as e:
            results[url] = {
                'error': str(e),
                'accessible': False
            }

    return results

if __name__ == "__main__":
    print("Investigating HKJC data sources...")
    results = investigate_hkjc()

    print("\n=== HKJC Data Source Investigation ===")
    for url, data in results.items():
        print(f"\n{url}:")
        if 'error' in data:
            print(f"  ❌ Error: {data['error']}")
        else:
            print(f"  ✅ Accessible: {data['accessible']}")
            print(f"  📄 Title: {data.get('title', 'N/A')}")
            print(f"  📊 Content Length: {data.get('content_length', 0)} chars")
            print(f"  🔗 Has API calls: {data.get('has_api_calls', False)}")
            if data.get('api_endpoints'):
                print("  📋 Potential API endpoints:")
                for endpoint in data['api_endpoints'][:5]:  # Show first 5
                    print(f"    - {endpoint}")

    print("\n=== Summary ===")
    accessible_sites = sum(1 for r in results.values() if r.get('accessible', False))
    sites_with_apis = sum(1 for r in results.values() if r.get('has_api_calls', False))

    print(f"✅ Accessible sites: {accessible_sites}/{len(results)}")
    print(f"🔗 Sites with potential API endpoints: {sites_with_apis}/{len(results)}")

    if sites_with_apis == 0:
        print("\n💡 Recommendation: HKJC likely requires authentication or uses proprietary APIs.")
        print("   Consider manual data upload or implementing OAuth flow for HKJC API access.")
    else:
        print(f"\n💡 Found {sites_with_apis} sites with potential API endpoints.")
        print("   These may require authentication to access actual data.")
